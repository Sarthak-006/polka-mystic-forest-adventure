# MetaMask Integration Flow

## User Journey

```
1. User opens MysticForestAdventure
   ↓
2. Clicks "Connect Wallet" button
   ↓
3. MetaMask popup appears requesting connection
   ↓
4. User approves connection
   ↓
5. App checks current network
   ↓
6. If not Polkadot Hub Testnet:
   - App prompts to add network
   - User approves network addition
   - App switches to Polkadot Hub Testnet
   ↓
7. Wallet connected successfully
   ↓
8. User plays game normally
   ↓
9. Game state automatically saved to blockchain
   ↓
10. On game completion:
    - "Save to Blockchain" button appears
    - User can save final game state
    - Digital signature created
    - Data stored with cryptographic hash
```

## Technical Architecture

```
Frontend (Browser)
├── MetaMask Extension
│   ├── Wallet Connection
│   ├── Network Management
│   └── Digital Signatures
├── JavaScript (script.js)
│   ├── Web3 Integration
│   ├── Wallet State Management
│   ├── UI Updates
│   └── API Communication
└── HTML/CSS
    ├── Wallet UI Components
    ├── Connection Buttons
    └── Status Display

Backend (Server)
├── Flask API (index.py)
│   ├── /api/save-to-blockchain
│   ├── /api/load-from-blockchain
│   ├── /api/wallet-balance
│   └── Signature Verification
└── Data Storage
    ├── File-based Records
    ├── Cryptographic Hashes
    └── Timestamp Tracking

Blockchain (Polkadot Hub Testnet)
├── Network: Polkadot Hub TestNet
├── Currency: PAS
├── Chain ID: 420420422
└── RPC: testnet-passet-hub-eth-rpc.polkadot.io
```

## Key Features

### 1. Automatic Network Detection
- Checks current MetaMask network
- Automatically switches to Polkadot Hub Testnet
- Adds network if not present

### 2. Wallet State Management
- Tracks connection status
- Monitors account changes
- Handles disconnection events

### 3. Blockchain Integration
- Saves game progress with signatures
- Loads previous game states
- Tracks transaction history

### 4. User Experience
- Seamless wallet connection
- Real-time notifications
- Error handling and recovery

## Security Features

- **Digital Signatures**: All blockchain operations require wallet signatures
- **Network Validation**: Ensures operations only on correct testnet
- **Data Integrity**: Cryptographic hashes for record verification
- **User Privacy**: Secure handling of wallet addresses

## Error Handling

- MetaMask not installed
- Wallet connection rejected
- Network switching failures
- Transaction errors
- Signature verification failures

## Future Enhancements

- Real blockchain transactions
- NFT integration
- Token rewards
- Multi-chain support
- Advanced analytics
