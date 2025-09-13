# MetaMask Integration with Polkadot Hub Testnet

This document describes the MetaMask integration implemented in the MysticForestAdventure project, allowing users to connect their wallets and interact with the Polkadot Hub Testnet.

## Features Implemented

### 1. Wallet Connection
- **MetaMask Integration**: Users can connect their MetaMask wallet directly from the game interface
- **Automatic Network Detection**: The app automatically detects and switches to Polkadot Hub Testnet
- **Network Addition**: If Polkadot Hub Testnet is not added to MetaMask, the app will prompt to add it automatically

### 2. Polkadot Hub Testnet Configuration
Based on the [official Polkadot documentation](https://docs.polkadot.com/develop/smart-contracts/connect-to-polkadot/#networks-details), the following network configuration is used:

```javascript
const POLKADOT_HUB_TESTNET = {
    chainId: '0x19191916', // 420420422 in hex (official Chain ID)
    chainName: 'Polkadot Hub TestNet',
    nativeCurrency: {
        name: 'PAS',
        symbol: 'PAS',
        decimals: 18,
    },
    rpcUrls: ['https://testnet-passet-hub-eth-rpc.polkadot.io'],
    blockExplorerUrls: ['https://blockscout-passet-hub.parity-testnet.parity.io/'],
    // Additional metadata for better compatibility
    iconUrls: ['https://polkadot.network/assets/img/brand/Polkadot_Token_PolkadotToken_Pink.svg'],
    shortName: 'polkadot-hub-testnet',
    testnet: true,
    faucetUrls: ['https://faucet.polkadot.io/']
};
```

### 3. Blockchain Integration
- **Game State Persistence**: Game progress can be saved to the blockchain
- **Digital Signatures**: All blockchain interactions are cryptographically signed
- **Wallet Balance Display**: Shows current PAS token balance
- **Transaction History**: Tracks all blockchain interactions

### 4. User Interface Enhancements
- **Wallet Status Display**: Shows connected wallet address and connection status
- **Connect/Disconnect Buttons**: Easy wallet management
- **Notification System**: Real-time feedback for wallet operations
- **Blockchain Save Button**: Appears on game completion when wallet is connected

## Technical Implementation

### Frontend (JavaScript)
- **Web3 Integration**: Uses MetaMask's Ethereum provider
- **Event Listeners**: Monitors account and network changes
- **Error Handling**: Comprehensive error handling for wallet operations
- **State Management**: Tracks wallet connection status and user address

### Backend (Python/Flask)
- **Blockchain API Endpoints**: 
  - `/api/save-to-blockchain` - Save game data to blockchain
  - `/api/load-from-blockchain` - Load saved game data
  - `/api/wallet-balance` - Get wallet balance
- **Data Persistence**: File-based storage for blockchain records
- **Signature Verification**: Validates wallet signatures

## Usage Instructions

### For Users

1. **Install MetaMask**: Ensure MetaMask browser extension is installed
2. **Connect Wallet**: Click the "Connect Wallet" button in the game header
3. **Network Setup**: The app will automatically add and switch to Polkadot Hub Testnet
4. **Play Game**: Enjoy the enhanced experience with blockchain integration
5. **Save Progress**: Use "Save to Blockchain" button when completing the game

### For Developers

1. **Network Configuration**: The Polkadot Hub Testnet configuration is defined in `public/script.js`
2. **API Endpoints**: Backend endpoints are implemented in `api/index.py`
3. **Error Handling**: Comprehensive error handling throughout the integration
4. **Testing**: Use testnet tokens for testing (obtain from Polkadot Hub Testnet faucet)

## Security Considerations

- **Signature Verification**: All blockchain operations require valid wallet signatures
- **Network Validation**: Ensures operations only occur on the correct testnet
- **Data Integrity**: Blockchain records include cryptographic hashes for verification
- **User Privacy**: Wallet addresses are handled securely and not logged unnecessarily

## Network Details

### Polkadot Hub Testnet
- **Network Name**: Polkadot Hub TestNet
- **Currency Symbol**: PAS
- **Chain ID**: 420420422 (0x19191916)
- **RPC URL**: https://testnet-passet-hub-eth-rpc.polkadot.io
- **Block Explorer**: https://blockscout-passet-hub.parity-testnet.parity.io/

## Getting Test Tokens

To interact with the blockchain features, users need test tokens. The app now includes automatic faucet integration:

1. **Automatic Detection**: The app automatically detects low wallet balance
2. **Faucet Button**: A "Get Test Tokens" button appears when balance is low
3. **Official Faucet**: Clicking the button opens the [official Polkadot Faucet](https://faucet.polkadot.io/)
4. **Network Selection**: Select "Polkadot Hub TestNet" from the Network dropdown
5. **Token Request**: Paste your wallet address and click "Get Some PASs"

### Manual Steps:
1. Connect to Polkadot Hub Testnet in MetaMask
2. Visit [https://faucet.polkadot.io/](https://faucet.polkadot.io/)
3. Select "Polkadot Hub TestNet" from the Network dropdown
4. Paste your wallet address and click "Get Some PASs"
5. Wait for tokens to arrive in your wallet

## Troubleshooting

### Common Issues

1. **MetaMask Not Detected**
   - Ensure MetaMask extension is installed and enabled
   - Refresh the page after installing MetaMask

2. **Network Connection Issues**
   - Check if Polkadot Hub Testnet is properly added to MetaMask
   - Verify RPC endpoint accessibility

3. **Transaction Failures**
   - Ensure sufficient test tokens in wallet
   - Check network connection and try again

4. **Signature Errors**
   - Ensure wallet is unlocked
   - Try disconnecting and reconnecting wallet

## Future Enhancements

- **Real Blockchain Integration**: Replace file-based storage with actual blockchain transactions
- **NFT Integration**: Create NFTs for game achievements
- **Token Rewards**: Implement token rewards for game completion
- **Multi-chain Support**: Support for additional blockchain networks
- **Advanced Analytics**: Detailed blockchain interaction analytics

## Dependencies

- MetaMask browser extension
- Modern web browser with Web3 support
- Polkadot Hub Testnet access
- Test PAS tokens for transactions

## Support

For technical support or questions about the MetaMask integration:
1. Check the browser console for error messages
2. Verify MetaMask is properly configured
3. Ensure you're connected to the correct network
4. Contact the development team for additional assistance

---

*This integration follows the official MetaMask setup guide for Polkadot networks and implements best practices for Web3 application development.*
