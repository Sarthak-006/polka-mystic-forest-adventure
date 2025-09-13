from flask import Flask, request, jsonify, send_from_directory, make_response
import requests
import hashlib
import os
import time
from flask_cors import CORS
import traceback
import pickle
import logging
import threading
from collections import OrderedDict
import json
from datetime import datetime
# Import your story_nodes, other helpers (modified to remove pygame)
# MAKE SURE Pillow is installed for manga generation later
# from PIL import Image, ImageDraw # If doing manga server-side

app = Flask(__name__)
# Configure CORS to allow credentials
CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Set-Cookie"],
        "supports_credentials": True
    }
})

# Replace in-memory session storage with file-based storage for Vercel
# Create a tmp directory if it doesn't exist
os.makedirs('/tmp', exist_ok=True)

# --- In-memory LRU cache for hot sessions (performance boost) ---
class LRUCache:
    def __init__(self, capacity=1000):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

    def set(self, key, value):
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

hot_sessions = LRUCache(capacity=500)

# --- Enhanced session management ---
def get_user_session(session_id):
    # Try in-memory cache first
    session = hot_sessions.get(session_id)
    if session:
        return session
    try:
        session_file = f"/tmp/session_{session_id}.pkl"
        if os.path.exists(session_file):
            with open(session_file, 'rb') as f:
                session = pickle.load(f)
                hot_sessions.set(session_id, session)
                return session
        return {'state': None}
    except Exception as e:
        logging.error(f"Error getting user session: {str(e)}")
        return {'state': None}

def save_user_session(session_id, session_data):
    hot_sessions.set(session_id, session_data)
    try:
        session_file = f"/tmp/session_{session_id}.pkl"
        with open(session_file, 'wb') as f:
            pickle.dump(session_data, f)
        return True
    except Exception as e:
        logging.error(f"Error saving user session: {str(e)}")
        return False

# --- Achievements, Inventory, Stats ---
def init_player_extras():
    return {
        'inventory': [],
        'achievements': set(),
        'stats': {
            'choices_made': 0,
            'unique_nodes': set(),
            'score_history': [],
            'endings_seen': set(),
        }
    }

def add_achievement(session_data, achievement):
    session_data.setdefault('achievements', set()).add(achievement)

def add_to_inventory(session_data, item):
    session_data.setdefault('inventory', []).append(item)

def update_stats(session_data, node_id, score):
    stats = session_data.setdefault('stats', {'choices_made': 0, 'unique_nodes': set(), 'score_history': [], 'endings_seen': set()})
    stats['choices_made'] += 1
    stats['unique_nodes'].add(node_id)
    stats['score_history'].append(score)

# --- Constants (Remove Pygame colors/fonts) ---
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt/"
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024
IMAGE_MODEL = 'flux'
# ... other non-pygame constants ...
# ... your story_nodes dictionary ...

# --- Game Story Nodes ---
story_nodes = {
    "start": {
        "situation": "You find yourself in a mysterious forest. The path ahead splits in two directions. What do you do?",
        "prompt": "Fantasy forest with two paths, mysterious, ethereal light, detailed",
        "seed": 12345,
        "choices": [
            {
                "text": "Take the path that leads deeper into the forest",
                "next_node": "deep_forest",
                "score_modifier": 1,
                "tag": "curious"
            },
            {
                "text": "Take the path that seems to lead out of the forest",
                "next_node": "forest_edge",
                "score_modifier": 0,
                "tag": "cautious"
            }
        ]
    },
    "deep_forest": {
        "situation": "As you venture deeper into the forest, you encounter a small magical creature trapped under a fallen branch.",
        "prompt": "Small magical glowing creature trapped under branch, fantasy forest, rays of light, detailed",
        "seed": 54321,
        "choices": [
            {
                "text": "Help free the creature",
                "next_node": "grateful_creature",
                "score_modifier": 2,
                "tag": "kind"
            },
            {
                "text": "Ignore the creature and continue exploring",
                "next_node": "lost_forest",
                "score_modifier": -1,
                "tag": "selfish"
            }
        ]
    },
    "grateful_creature": {
        "situation": "You free the creature, who thanks you and offers to lead you to a hidden treasure as a reward.",
        "prompt": "Magical glowing creature leading adventurer through fantasy forest, magical trail, treasure map, detailed",
        "seed": 67890,
        "choices": [
            {
                "text": "Follow the creature to the treasure",
                "next_node": "hidden_treasure",
                "score_modifier": 1,
                "tag": "adventurous"
            },
            {
                "text": "Thank the creature but say you need to find your way out",
                "next_node": "creature_guidance",
                "score_modifier": 0,
                "tag": "practical"
            }
        ]
    },
    "hidden_treasure": {
        "situation": "The creature leads you to an ancient chest hidden beneath tree roots. Inside you find a magical amulet that glows with power.",
        "prompt": "Ancient treasure chest with magical glowing amulet, tree roots, fantasy forest, detailed",
        "seed": 13579,
        "choices": [
            {
                "text": "Take the amulet and wear it",
                "next_node": "amulet_power",
                "score_modifier": 2,
                "tag": "risk-taker"
            },
            {
                "text": "Leave the amulet, treasures in enchanted forests often have curses",
                "next_node": "wise_decision",
                "score_modifier": 1,
                "tag": "wise"
            }
        ]
    },
    "amulet_power": {
        "situation": "As you put on the amulet, you feel a surge of magical energy. Your senses heighten, and you can now see magical paths in the forest that were invisible before.",
        "prompt": "Character wearing glowing magical amulet, visible magical paths, enchanted forest, magical energy, detailed",
        "seed": 24680,
        "choices": [
            {
                "text": "Follow the brightest magical path",
                "next_node": "_calculate_end",
                "score_modifier": 1,
                "tag": "bold"
            },
            {
                "text": "Use your new power to find the safest way out",
                "next_node": "_calculate_end",
                "score_modifier": 0,
                "tag": "careful"
            }
        ]
    },
    "forest_edge": {
        "situation": "You reach the edge of the forest and see a small village in the distance. There's also a strange cave entrance nearby.",
        "prompt": "Edge of fantasy forest, distant village, mysterious cave entrance, sunset, detailed",
        "seed": 97531,
        "choices": [
            {
                "text": "Head toward the village",
                "next_node": "village_arrival",
                "score_modifier": 0,
                "tag": "social"
            },
            {
                "text": "Explore the mysterious cave",
                "next_node": "cave_entrance",
                "score_modifier": 1,
                "tag": "adventurous"
            }
        ]
    },
    "generic_good_ending": {
        "is_end": True,
        "ending_category": "Heroic Journey",
        "situation": "Your choices have led you to become a hero of the forest. The magical creatures celebrate your deeds, and you've discovered powers within yourself you never knew existed. You return home with incredible stories and the knowledge that you've made a positive difference in this magical realm.",
        "prompt": "Hero celebrated by magical forest creatures, magical aura, fantasy celebration, triumphant pose, detailed",
        "seed": 11111,
        "choices": []
    },
    "generic_neutral_ending": {
        "is_end": True,
        "ending_category": "Forest Explorer",
        "situation": "You've had an interesting adventure in the magical forest. While you didn't become a legendary hero, you've seen wonders few others have witnessed. You make your way back home, forever changed by your experiences in the enchanted woods.",
        "prompt": "Character exiting magical forest, looking back with wonder, mixed emotions, sunset, detailed",
        "seed": 22222,
        "choices": []
    },
    "generic_bad_ending": {
        "is_end": True,
        "ending_category": "Lost Wanderer",
        "situation": "Your choices have led you astray. You find yourself hopelessly lost in the darkening forest. The magical creatures no longer help you, and strange shadows follow your every move. You fear you may never find your way home again.",
        "prompt": "Lost traveler in dark fantasy forest, ominous shadows, fear, getting dark, detailed",
        "seed": 33333,
        "choices": []
    },
    "lost_forest": {
        "situation": "As you continue deeper into the forest, ignoring the trapped creature, you start to realize you're getting lost. The trees seem to close in around you.",
        "prompt": "Lost in dense fantasy forest, closing in trees, disorienting paths, foreboding atmosphere, detailed",
        "seed": 44444,
        "choices": [
            {
                "text": "Try to retrace your steps",
                "next_node": "lost_deeper",
                "score_modifier": -1,
                "tag": "practical"
            },
            {
                "text": "Climb a tree to get a better view",
                "next_node": "tree_climb",
                "score_modifier": 1,
                "tag": "resourceful"
            }
        ]
    },
    "lost_deeper": {
        "situation": "Attempting to retrace your steps only leads you deeper into the forest. Night is falling, and strange noises surround you.",
        "prompt": "Dark fantasy forest at night, eerie glowing eyes, lost traveler, fear, detailed",
        "seed": 55555,
        "choices": [
            {
                "text": "Make camp and wait for daylight",
                "next_node": "_calculate_end",
                "score_modifier": -1,
                "tag": "patient"
            },
            {
                "text": "Keep moving despite the darkness",
                "next_node": "_calculate_end",
                "score_modifier": -2,
                "tag": "stubborn"
            }
        ]
    },
    "tree_climb": {
        "situation": "From atop a tall tree, you spot a clearing with a strange stone circle that seems to glow with magic. You also see the forest edge in the far distance.",
        "prompt": "View from tall tree, fantasy forest, glowing stone circle in clearing, forest edge in distance, detailed",
        "seed": 66666,
        "choices": [
            {
                "text": "Head toward the mysterious stone circle",
                "next_node": "stone_circle",
                "score_modifier": 1,
                "tag": "curious"
            },
            {
                "text": "Make your way toward the forest edge",
                "next_node": "forest_edge",
                "score_modifier": 0,
                "tag": "cautious"
            }
        ]
    },
    "creature_guidance": {
        "situation": "The magical creature nods understandingly and offers to guide you to the forest edge instead. It leads you along a hidden path that seems to shimmer with gentle magic.",
        "prompt": "Magical creature guiding traveler along shimmering path, forest edge visible, fantasy forest, detailed",
        "seed": 77777,
        "choices": [
            {
                "text": "Thank the creature again before parting ways",
                "next_node": "forest_edge",
                "score_modifier": 1,
                "tag": "grateful"
            },
            {
                "text": "Ask the creature if it would like to accompany you further",
                "next_node": "_calculate_end",
                "score_modifier": 2,
                "tag": "friendly"
            }
        ]
    },
    "stone_circle": {
        "situation": "You find an ancient stone circle with strange symbols. The air feels charged with magic, and the stones seem to pulse with an inner light.",
        "prompt": "Ancient stone circle with glowing symbols, magical aura, fantasy forest clearing, detailed",
        "seed": 88888,
        "choices": [
            {
                "text": "Touch the central stone and speak a word of power",
                "next_node": "_calculate_end",
                "score_modifier": 1,
                "tag": "magical"
            },
            {
                "text": "Study the symbols to try to understand their meaning",
                "next_node": "_calculate_end",
                "score_modifier": 1,
                "tag": "scholarly"
            }
        ]
    },
    "wise_decision": {
        "situation": "You decide to leave the amulet behind. As you walk away, you hear a faint hissing sound and turn to see the amulet dissolving into a puddle of poisonous liquid. Your caution has saved you.",
        "prompt": "Fantasy amulet dissolving into poisonous liquid, cautious adventurer backing away, magical chest, detailed",
        "seed": 99999,
        "choices": [
            {
                "text": "Continue exploring the forest with heightened caution",
                "next_node": "_calculate_end",
                "score_modifier": 1,
                "tag": "vigilant"
            },
            {
                "text": "Ask the creature to guide you back to safer territory",
                "next_node": "creature_guidance",
                "score_modifier": 0,
                "tag": "practical"
            }
        ]
    },
    "village_arrival": {
        "situation": "You arrive at the village to find it's inhabited by friendly forest folk who welcome you warmly. They offer food and shelter, curious about your forest adventures.",
        "prompt": "Fantasy village with forest folk welcoming traveler, cozy cottages, warm lighting, detailed",
        "seed": 12121,
        "choices": [
            {
                "text": "Share your adventures and ask about the forest's secrets",
                "next_node": "_calculate_end",
                "score_modifier": 1,
                "tag": "social"
            },
            {
                "text": "Thank them but explain you need to continue your journey",
                "next_node": "_calculate_end",
                "score_modifier": 0,
                "tag": "independent"
            }
        ]
    },
    "cave_entrance": {
        "situation": "The cave entrance reveals a passage lined with glowing crystals that illuminate the darkness with a soft blue light.",
        "prompt": "Cave entrance with glowing blue crystals, mysterious passage, fantasy setting, detailed",
        "seed": 23232,
        "choices": [
            {
                "text": "Venture deeper into the crystal cave",
                "next_node": "_calculate_end",
                "score_modifier": 2,
                "tag": "brave"
            },
            {
                "text": "Take just one small crystal and head back to the forest edge",
                "next_node": "_calculate_end",
                "score_modifier": -1,
                "tag": "greedy"
            }
        ]
    },
    "heroic_savior_ending": {
        "is_end": True,
        "ending_category": "Heroic Savior",
        "situation": "Your kindness and courage have made you a legendary hero of the forest. The magical creatures see you as their champion and protector. You've discovered ancient powers within yourself that allow you to communicate with the forest and its inhabitants. Your name will be sung in the folklore of this realm for generations to come.",
        "prompt": "Epic fantasy hero, magical forest defender, ancient powers, magical creatures celebrating, detailed fantasy illustration",
        "seed": 11112,
        "choices": []
    },
    "wise_mage_ending": {
        "is_end": True,
        "ending_category": "Wise Mage",
        "situation": "Your wisdom and magical affinity have transformed you into a powerful mage. The forest has accepted you as one of its guardians, and you've established a small tower where you study the ancient magics that flow through this realm. Many travelers seek your guidance, and you've become a respected figure throughout the lands.",
        "prompt": "Wise mage in forest tower, magical tomes, arcane study, glowing runes, fantasy illustration, detailed",
        "seed": 11113,
        "choices": []
    },
    "forest_guardian_ending": {
        "is_end": True,
        "ending_category": "Forest Guardian",
        "situation": "The magic of the forest has chosen you as its guardian. You've bonded with the ancient spirits of the woods, gaining the ability to shape and protect this magical realm. Your body now carries marks of the forest—perhaps leaves for hair or bark-like skin—as you've become part-human, part-forest entity, respected and sometimes feared by those who enter your domain.",
        "prompt": "Human-forest hybrid guardian, bark skin, leaf hair, forest spirits, magical forest throne, fantasy character, detailed illustration",
        "seed": 11114,
        "choices": []
    },
    "peaceful_traveler_ending": {
        "is_end": True,
        "ending_category": "Peaceful Traveler",
        "situation": "You've explored the wonders of the magical forest and learned much from your journey. Though you didn't become a legendary hero, you carry the forest's wisdom with you. You now travel between villages, sharing tales of the enchanted woods and occasionally using small magics you learned there to help those in need.",
        "prompt": "Wandering storyteller, magical trinkets, village gathering, fantasy traveler, sunset, detailed illustration",
        "seed": 22223,
        "choices": []
    },
    "forest_explorer_ending": {
        "is_end": True, 
        "ending_category": "Forest Explorer",
        "situation": "Your exploration of the magical forest has made you a renowned expert in magical flora and fauna. You've documented countless species unknown to the outside world, creating detailed journals that scholars pay handsomely to study. You now lead occasional expeditions into the forest, guiding those brave enough to witness its wonders.",
        "prompt": "Fantasy naturalist, magical creature sketches, expedition camp, journals, forest background, detailed illustration",
        "seed": 22224,
        "choices": []
    },
    "merchant_ending": {
        "is_end": True,
        "ending_category": "Forest Merchant",
        "situation": "Your adventures in the magical forest have given you access to rare herbs, magical trinkets, and exotic materials. You've established a small but profitable trading post at the forest's edge, becoming the go-to merchant for magical components. Wizards and alchemists from far and wide seek your uniquely sourced goods.",
        "prompt": "Fantasy merchant shop, magical herbs and potions, trading post, forest edge, customer wizards, detailed illustration",
        "seed": 22225,
        "choices": []
    },
    "lost_soul_ending": {
        "is_end": True,
        "ending_category": "Lost Soul",
        "situation": "The forest's magic has clouded your mind and you've lost your way—both literally and figuratively. You wander the ever-shifting paths, no longer remembering who you were before entering these woods. The forest creatures watch you with pity, but none approach, for you have become a cautionary tale told to those who might enter the forest unprepared.",
        "prompt": "Lost wanderer in dark forest, tattered clothes, confused expression, glowing eyes watching from darkness, fantasy horror, detailed illustration",
        "seed": 33334,
        "choices": []
    },
    "cursed_wanderer_ending": {
        "is_end": True,
        "ending_category": "Cursed Wanderer",
        "situation": "Your selfish actions in the forest have drawn the ire of ancient spirits. A curse now follows you—perhaps your shadow moves independently, or your reflection shows a twisted version of yourself. You search endlessly for a cure, but the curse seems to strengthen the further you get from the forest that birthed it.",
        "prompt": "Cursed traveler, unnatural shadow, twisted reflection in water, dark fantasy, horror elements, detailed illustration",
        "seed": 33335,
        "choices": []
    },
    "forest_prisoner_ending": {
        "is_end": True,
        "ending_category": "Forest Prisoner",
        "situation": "The forest has claimed you as its prisoner. The paths continuously lead you back to the center, no matter which direction you travel. You've built a small shelter and learned to survive, but freedom eludes you. Sometimes you see other travelers through the trees, but when you call out, they cannot seem to hear you—as if you exist in a separate layer of reality.",
        "prompt": "Prisoner of magical forest, small shelter, paths that loop back, barrier of light, travelers passing by unaware, fantasy horror, detailed illustration",
        "seed": 33336,
        "choices": []
    }
}

# --- Game State (In-memory - BAD for multiple users/production) ---
game_state = {
    "current_node_id": "start",
    "story_path": [], # Store tuples: (node_id, choice_text, score_mod)
    "current_score": 0,
    "sentiment_tally": {},
    "last_error": None,
    "last_reset": time.time()  # Track when the game was last reset
}

# Add a user_sessions dictionary to track individual user sessions
user_sessions = {}

# --- Helper Functions (Refactored - NO PYGAME) ---
def get_dynamic_seed(base_seed, path_node_ids, session_id=None):
    """Generate a unique seed based on the path taken and session ID"""
    if not session_id:
        # Use existing path-based seed if no session ID
        path_hash = hashlib.md5(''.join(path_node_ids).encode()).hexdigest()
        seed = (base_seed + int(path_hash, 16)) % 999999
    else:
        # Create a unique seed combining base seed, path, and session ID
        combined = f"{base_seed}-{''.join(path_node_ids)}-{session_id}"
        seed_hash = hashlib.md5(combined.encode()).hexdigest()
        seed = int(seed_hash, 16) % 999999
    
    return seed

def enhance_prompt(base_prompt, path_tuples, sentiment_tally, last_choice, session_id=None):
    """Enhance a prompt based on the user's journey and style preferences"""
    # Start with base style elements
    style_elements = ["detailed", "fantasy style"]
    
    if session_id:
        # Get user session data
        session_data = get_user_session(session_id)
        
        # Get style preferences from session data
        style_preferences = session_data.get('style_preferences', [])
        if style_preferences:
            style_elements.extend(style_preferences)
    
    # Add elements based on sentiment tally
    positive_traits = ["kind", "adventurous", "bold", "wise", "resourceful"]
    negative_traits = ["selfish", "cautious", "stubborn"]
    
    positive_count = sum(sentiment_tally.get(tag, 0) for tag in positive_traits)
    negative_count = sum(sentiment_tally.get(tag, 0) for tag in negative_traits)
    
    # Add style modifiers based on sentiment balance
    if positive_count > negative_count:
        style_elements.append("bright")
        style_elements.append("vibrant colors")
    elif negative_count > positive_count:
        style_elements.append("dark")
        style_elements.append("muted colors")
    
    # Combine everything into an enhanced prompt
    enhanced = f"{base_prompt}, {', '.join(style_elements)}"
    
    # Make each image different even for the same node by adding timestamp
    timestamp = int(time.time())
    enhanced += f", seed:{timestamp}"
    
    return enhanced

def reset_game_state(session_id=None):
    """Reset the game state"""
    initial_state = {
        "current_node_id": "start",
        "path_history": ["start"],
        "score": 0,
        "sentiment_tally": {},
        "choice_history": [],
        "created_at": time.time()
    }
    
    # If we have a session ID, store the state in persistent storage
    if session_id:
        try:
            import random
            all_style_options = [
                "fantasy", "medieval", "ethereal", "mystical", "dramatic", 
                "whimsical", "dark", "bright", "colorful", "muted"
            ]
            traits = ["cautious", "bold", "diplomatic", "direct", "curious", "practical", 
                      "optimistic", "pessimistic", "detailed", "concise"]
            
            # Get existing session or create new one
            session_data = get_user_session(session_id)
            
            # Update the session data
            session_data['style_preferences'] = random.sample(all_style_options, 3)
            session_data['personality_traits'] = random.sample(traits, 3)
            session_data['state'] = initial_state
            
            # Save the updated session
            save_user_session(session_id, session_data)
            
            logging.info(f"Successfully reset state for session {session_id}")
            return initial_state
        except Exception as e:
            logging.error(f"Error resetting state: {str(e)}")
            return initial_state
    
    return initial_state

def get_node_details(node_id):
    """Get details for a story node with personalized content"""
    try:
        # Get base node
        node = story_nodes.get(node_id)
        if not node:
            return None
            
        # Make a copy so we don't modify the original
        node_copy = node.copy()
        
        # Personalize choices if we're not at an end node
        if not node_copy.get("is_end", False) and "choices" in node_copy:
            # Deep copy choices to avoid modifying original
            node_copy["choices"] = [choice.copy() for choice in node_copy["choices"]]
            
            # Personalize choice texts with small variations
            for choice in node_copy["choices"]:
                if "text" in choice:
                    # We could add small variations to choice text here
                    # But we'll keep the first choice consistent as required
                    pass  # Implemented in the next update
        
        return node_copy
        
    except Exception as e:
        traceback.print_exc()
        return None

# --- API Endpoints ---
@app.route('/')
def serve_index():
    try:
        return send_from_directory('../public', 'index.html')
    except Exception as e:
        print(f"Error serving index: {str(e)}")
        return f"Error serving page: {str(e)}", 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('../public', path)
    except Exception as e:
        print(f"Error serving static file {path}: {str(e)}")
        return f"Error serving file: {str(e)}", 404

@app.route('/api/state', methods=['GET', 'OPTIONS'])
def get_current_state():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        # Get user's session ID from cookies or create a new one
        session_id = request.cookies.get('session_id')
        if not session_id:
            # Generate a new session ID
            session_id = hashlib.md5(f"{time.time()}-{os.urandom(8).hex()}".encode()).hexdigest()
        
        # Get or create the user's game state from persistent storage
        session_data = get_user_session(session_id)
        game_state = session_data.get('state')
        
        if not game_state:
            # Reset/initialize the game state
            game_state = reset_game_state(session_id)
            session_data['state'] = game_state
            save_user_session(session_id, session_data)
            logging.info(f"Created new state for session {session_id}")
        
        current_node_id = game_state["current_node_id"]
        node_details = get_node_details(current_node_id)
        
        if not node_details:
            return jsonify({"error": "Invalid node"}), 400
        
        # Generate image URL with dynamic seed and enhanced prompt
        path_node_ids = game_state.get("path_history", [])
        sentiment_tally = game_state.get("sentiment_tally", {})
        choice_history = game_state.get("choice_history", [])
        last_choice = choice_history[-1] if choice_history else None
        
        base_seed = node_details.get("seed", 12345)
        dynamic_seed = get_dynamic_seed(base_seed, path_node_ids, session_id)
        
        path_tuples = [(node, game_state.get("sentiment_tally", {}).get(node, 0)) 
                       for node in path_node_ids]
        
        base_prompt = node_details.get("prompt", "")
        enhanced_prompt = enhance_prompt(base_prompt, path_tuples, sentiment_tally, last_choice, session_id)
        
        # Create the image URL
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        image_url = f"{POLLINATIONS_BASE_URL}{encoded_prompt}"
        
        # Create response data
        state_details = {
            "current_node": node_details,
            "score": game_state.get("score", 0),
            "image_url": image_url,
            "is_end": node_details.get("is_end", False),
            "choices": node_details.get("choices", []),
            "situation": node_details.get("situation", "")
        }
        
        # Create response with cookie
        response = make_response(jsonify(state_details))
        response.set_cookie('session_id', session_id, httponly=True, samesite='Strict')
        return response
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/choice', methods=['POST', 'OPTIONS'])
def make_choice():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        # Get post data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get user's session ID from cookies
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({"error": "No session found"}), 400
            
        # Get choice index
        choice_index = data.get("choice_index")
        if choice_index is None:
            return jsonify({"error": "No choice index provided"}), 400
            
        # Try to convert to integer
        try:
            choice_index = int(choice_index)
        except ValueError:
            return jsonify({"error": "Choice index must be a number"}), 400
            
        # Get the user's game state from persistent storage
        session_data = get_user_session(session_id)
        game_state = session_data.get('state')
        
        if not game_state:
            return jsonify({"error": "No game in progress"}), 400
            
        # Get current node
        current_node_id = game_state.get("current_node_id", "")
        if not current_node_id:
            return jsonify({"error": "No current node in game state"}), 400
        
        # Get current node details
        node_details = get_node_details(current_node_id)
        if not node_details:
            return jsonify({"error": "Invalid current node"}), 400
            
        # Validate choice index
        if not node_details.get("choices") or choice_index >= len(node_details["choices"]):
            return jsonify({"error": "Invalid choice index"}), 400
            
        # Get the chosen choice
        choice = node_details["choices"][choice_index]
        
        # Special processing for dynamic ending calculation
        next_node_id = choice.get("next_node")
        if next_node_id == "_calculate_end":
            # Calculate ending based on score and sentiment
            score = game_state.get("score", 0)
            sentiment_tally = game_state.get("sentiment_tally", {})
            
            # Count positive vs negative tags
            positive_count = sum(sentiment_tally.get(tag, 0) for tag in 
                             ["kind", "adventurous", "bold", "wise", "resourceful"])
            negative_count = sum(sentiment_tally.get(tag, 0) for tag in 
                             ["selfish", "cautious", "stubborn"])
            
            # Determine ending based on score and sentiment balance
            if score >= 5 and positive_count > negative_count:
                next_node_id = "generic_good_ending"
            elif score <= 0 or negative_count > positive_count:
                next_node_id = "generic_bad_ending"
            else:
                next_node_id = "generic_neutral_ending"
                
            # Create a unique ending variation based on the session ID
            # This ensures each user gets a different ending
            custom_endings = {
                "generic_good_ending": [
                    "heroic_savior_ending", "wise_mage_ending", "forest_guardian_ending"
                ],
                "generic_neutral_ending": [
                    "peaceful_traveler_ending", "forest_explorer_ending", "merchant_ending"
                ],
                "generic_bad_ending": [
                    "lost_soul_ending", "cursed_wanderer_ending", "forest_prisoner_ending"
                ]
            }
            
            if next_node_id in custom_endings:
                # Use the session ID to pick a specific variant
                session_hash = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
                ending_options = custom_endings[next_node_id]
                ending_index = session_hash % len(ending_options)
                custom_ending = ending_options[ending_index]
                
                # If we have this ending defined, use it instead
                if custom_ending in story_nodes:
                    next_node_id = custom_ending
        
        # Update game state
        game_state["current_node_id"] = next_node_id
        game_state["path_history"].append(next_node_id)
        
        # Update score
        score_modifier = choice.get("score_modifier", 0)
        game_state["score"] += score_modifier
        
        # Update sentiment tally
        tag = choice.get("tag")
        if tag:
            if tag not in game_state["sentiment_tally"]:
                game_state["sentiment_tally"][tag] = 0
            game_state["sentiment_tally"][tag] += 1
        
        # Record this choice
        game_state["choice_history"].append({
            "from_node": current_node_id,
            "choice_index": choice_index,
            "choice_text": choice.get("text", ""),
            "tag": tag
        })
        
        # Save the updated state to persistent storage
        session_data['state'] = game_state
        save_user_session(session_id, session_data)
        logging.info(f"Saved updated state after choice for session {session_id}")
        
        # Return the new state
        return get_current_state()
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_game():
    try:
        # Get user's session ID from cookies
        session_id = request.cookies.get('session_id')
        if not session_id:
            # Generate a new session ID
            session_id = hashlib.md5(f"{time.time()}-{os.urandom(8).hex()}".encode()).hexdigest()
        
        # Reset the game state for this session
        reset_game_state(session_id)
        logging.info(f"Reset game state for session {session_id}")
        
        # Instead of just returning success message, return the actual game state
        # by calling the get_current_state function
        return get_current_state()
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/share-image', methods=['GET'])
def generate_share_image():
    try:
        # Get user's session ID from cookies
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({"error": "No session found"}), 400
        
        # Get the user's game state from persistent storage
        session_data = get_user_session(session_id)
        game_state = session_data.get('state')
        
        if not game_state:
            return jsonify({"error": "No game in progress"}), 400
            
        # Get score and ending information
        score = game_state.get("score", 0)
        current_node_id = game_state.get("current_node_id", "")
        node_details = get_node_details(current_node_id)
        
        if not node_details:
            return jsonify({"error": "Invalid node"}), 400
            
        # Check if the game has ended
        if not node_details.get("is_end", False):
            return jsonify({"error": "Game has not ended yet"}), 400
            
        # Get the ending category
        ending_category = node_details.get("ending_category", "Adventure Complete")
        
        # Generate the specific manga image prompt with user's journey details
        path_node_ids = game_state.get("path_history", [])
        sentiment_tally = game_state.get("sentiment_tally", {})
        
        # Generate main traits from sentiment tally
        main_traits = []
        for tag, count in sentiment_tally.items():
            if count > 0:
                main_traits.append(tag)
        
        # Select top 3 traits if we have that many
        top_traits = main_traits[:3] if len(main_traits) >= 3 else main_traits
        traits_text = ", ".join(top_traits)
        
        # Create a personalized story description
        personality = f"a {traits_text} adventurer" if traits_text else "an adventurer"
        
        # Generate image URL with enhanced prompt
        base_prompt = node_details.get("prompt", "")
        path_tuples = [(node, sentiment_tally.get(node, 0)) for node in path_node_ids]
        choice_history = game_state.get("choice_history", [])
        last_choice = choice_history[-1] if choice_history else None
        
        # Get dynamic seed
        base_seed = node_details.get("seed", 12345)
        dynamic_seed = get_dynamic_seed(base_seed, path_node_ids, session_id)
        
        # Generate enhanced prompt for manga-style image
        enhanced_prompt = enhance_prompt(base_prompt, path_tuples, sentiment_tally, last_choice, session_id)
        
        # Create manga-style panel layout prompt
        share_manga_prompt = f"Manga style, 4-panel comic strip telling the story of {personality} who achieved the '{ending_category}' ending with a score of {score}, {enhanced_prompt}, clean white background with title 'Mystic Forest Adventure' and score displayed"
        
        # URL encode the prompt
        encoded_manga_prompt = requests.utils.quote(share_manga_prompt)
        share_image_url = f"{POLLINATIONS_BASE_URL}{encoded_manga_prompt}"
        
        # Return the share image URL
        return jsonify({
            "share_image_url": share_image_url,
            "score": score,
            "ending_category": ending_category
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/save-to-blockchain', methods=['POST', 'OPTIONS'])
def save_to_blockchain():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        wallet_address = data.get('walletAddress')
        game_data = data.get('gameData')
        signature = data.get('signature')
        message = data.get('message')

        if not all([wallet_address, game_data, signature, message]):
            return jsonify({"error": "Missing required fields"}), 400

        # Create a blockchain record
        blockchain_record = {
            'walletAddress': wallet_address,
            'gameData': game_data,
            'signature': signature,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'blockchainHash': hashlib.sha256(f"{wallet_address}{message}{signature}".encode()).hexdigest()
        }

        # In a real implementation, you would save this to a blockchain
        # For now, we'll save it to a file-based storage
        blockchain_file = f"/tmp/blockchain_{wallet_address}.json"
        
        # Load existing records
        existing_records = []
        if os.path.exists(blockchain_file):
            try:
                with open(blockchain_file, 'r') as f:
                    existing_records = json.load(f)
            except:
                existing_records = []

        # Add new record
        existing_records.append(blockchain_record)

        # Save back to file
        with open(blockchain_file, 'w') as f:
            json.dump(existing_records, f, indent=2)

        logging.info(f"Saved blockchain record for wallet {wallet_address}")

        return jsonify({
            "success": True,
            "blockchainHash": blockchain_record['blockchainHash'],
            "message": "Game data saved to blockchain successfully"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/load-from-blockchain', methods=['GET', 'OPTIONS'])
def load_from_blockchain():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        wallet_address = request.args.get('walletAddress')
        if not wallet_address:
            return jsonify({"error": "Wallet address required"}), 400

        blockchain_file = f"/tmp/blockchain_{wallet_address}.json"
        
        if not os.path.exists(blockchain_file):
            return jsonify({"records": [], "message": "No blockchain records found"})

        with open(blockchain_file, 'r') as f:
            records = json.load(f)

        # Return the most recent record
        if records:
            latest_record = max(records, key=lambda x: x.get('timestamp', ''))
            return jsonify({
                "records": records,
                "latest": latest_record,
                "message": f"Found {len(records)} blockchain records"
            })
        else:
            return jsonify({"records": [], "message": "No blockchain records found"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet-balance', methods=['GET', 'OPTIONS'])
def get_wallet_balance():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        wallet_address = request.args.get('walletAddress')
        if not wallet_address:
            return jsonify({"error": "Wallet address required"}), 400

        # In a real implementation, you would query the blockchain
        # For now, we'll return a mock balance
        mock_balance = {
            'balance': '1000.0',
            'currency': 'PAS',
            'walletAddress': wallet_address,
            'network': 'Polkadot Hub Testnet'
        }

        return jsonify(mock_balance)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Vercel expects the app object for Python runtimes
# The file is usually named index.py inside an 'api' folder
# If running locally:
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')