# MysticForestAdventure - Polkadot Integration

An interactive fantasy adventure game built for the Polkadot ecosystem with MetaMask wallet integration and blockchain state persistence.

## Features

- 🎮 **Interactive Story Game**: Choose your own adventure through a mystical forest
- 🔗 **MetaMask Integration**: Connect your wallet and interact with Polkadot Hub TestNet
- 💎 **DOT Token Support**: Display and manage DOT token balances
- ⚡ **Blockchain Persistence**: Save your game progress to the blockchain
- 🔐 **Digital Signatures**: All blockchain interactions are cryptographically signed
- 🎨 **Polkadot Branding**: Built specifically for the Polkadot ecosystem
- Choice-based gameplay with branching narratives
- Dynamic image generation based on your story choices
- Score tracking based on your decisions
- Different endings depending on your path and score

## Setup

1. Install Python 3.7+ and pip
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Running Locally

1. Start the Flask backend:
   ```
   python -m flask --app api/index.py run
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Deployment on Vercel

This application is configured to be deployed on Vercel:

1. Fork/clone this repository
2. Connect to Vercel
3. Deploy

## How to Play

1. Read the situation text and look at the image
2. Choose one of the options presented
3. Each choice affects your score and leads to different story paths
4. Reach one of several possible endings based on your choices

## Polkadot Features

- **Network**: Polkadot Hub TestNet (Chain ID: 420420422)
- **Currency**: PAS tokens
- **RPC**: https://testnet-passet-hub-eth-rpc.polkadot.io
- **Block Explorer**: https://blockscout-passet-hub.parity-testnet.parity.io/

## Technical Details

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Blockchain: MetaMask, Polkadot Hub TestNet
- Image Generation: Pollinations.ai API
- Deployment: Vercel

## Documentation

- [MetaMask Integration Guide](METAMASK_INTEGRATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Deployment Instructions](DEPLOYMENT.md)
- [Integration Flow](INTEGRATION_FLOW.md)

## Development

To modify the game:
- Edit `api/index.py` to change the story nodes and game logic
- Edit files in the `public` directory to change the frontend appearance and behavior

## Built for Polkadot

This application demonstrates:
- Polkadot Hub TestNet integration
- DOT token functionality
- Blockchain state persistence
- MetaMask wallet connectivity
- Cryptographic signature verification

---

**Ready to deploy and showcase your Polkadot ecosystem integration! 🚀** 