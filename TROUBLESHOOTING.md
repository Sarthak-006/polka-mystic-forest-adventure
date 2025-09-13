# MetaMask Integration Troubleshooting Guide

## Common Issues and Solutions

### 1. Chain ID Mismatch Error

**Error Message**: "Chain ID returned by the custom network does not match the submitted chain ID"

**Cause**: This error occurs when MetaMask cannot verify the Chain ID with the RPC endpoint, often due to:
- Network compatibility issues
- RPC endpoint problems
- EVM compatibility limitations

**Solutions**:

#### Option A: Manual Network Addition
1. **Click "Manual Network Setup"** button in the app
2. **Follow the instructions** displayed in the popup
3. **Add network manually** in MetaMask with these exact details:
   - **Network Name**: `Polkadot Hub TestNet`
   - **RPC URL**: `https://testnet-passet-hub-eth-rpc.polkadot.io`
   - **Chain ID**: `420420422`
   - **Currency Symbol**: `PAS`
   - **Block Explorer**: `https://blockscout-passet-hub.parity-testnet.parity.io/`

#### Option B: Use Fallback Network
1. **Let the app handle it** - it will automatically suggest Goerli testnet
2. **Accept the fallback** when prompted
3. **Continue with Goerli** for testing purposes

#### Option C: Skip Network Addition
1. **Cancel the network addition** in MetaMask
2. **Use your current network** (Ethereum Mainnet, etc.)
3. **The app will still work** for basic functionality

### 2. MetaMask Not Detected

**Error**: "MetaMask is not installed"

**Solution**:
1. Install MetaMask browser extension
2. Refresh the page
3. Ensure MetaMask is enabled

### 3. Wallet Connection Rejected

**Error**: "Wallet connection rejected by user"

**Solution**:
1. Click "Connect Wallet" again
2. Click "Connect" in MetaMask popup
3. Ensure MetaMask is unlocked

### 4. Network Switching Issues

**Error**: "Failed to switch network"

**Solution**:
1. Try manual network addition (see Option A above)
2. Check if the network is already added in MetaMask
3. Clear MetaMask cache and try again

### 5. Low Balance Issues

**Error**: "Insufficient funds for transaction"

**Solution**:
1. **Get test tokens** from the faucet:
   - Click "Get Test Tokens" button (if available)
   - Or visit: https://faucet.polkadot.io/
   - Select "Polkadot Hub TestNet" from dropdown
   - Enter your wallet address
   - Click "Get Some PASs"

### 6. RPC Endpoint Issues

**Error**: "RPC endpoint not responding"

**Solution**:
1. Check your internet connection
2. Try refreshing the page
3. The RPC endpoint might be temporarily down
4. Use manual network addition with alternative RPC URLs

## Alternative RPC URLs

If the main RPC URL doesn't work, try these alternatives:

- Primary: `https://testnet-passet-hub-eth-rpc.polkadot.io`
- Alternative: `https://rpc.polkadot.io` (if available)
- Fallback: Use Goerli testnet for testing

## Network Compatibility Notes

### Polkadot Hub TestNet
- **EVM Compatibility**: Limited (may cause Chain ID errors)
- **MetaMask Support**: Partial (requires manual setup)
- **Recommended for**: Advanced users familiar with Polkadot

### Goerli TestNet (Fallback)
- **EVM Compatibility**: Full
- **MetaMask Support**: Excellent
- **Recommended for**: General testing and development

## Getting Help

### 1. Check Browser Console
- Open Developer Tools (F12)
- Look for error messages in Console tab
- Take screenshots of any errors

### 2. Verify Network Details
- Ensure all network parameters are correct
- Double-check Chain ID (420420422)
- Verify RPC URL is accessible

### 3. Test with Different Networks
- Try connecting to Ethereum Mainnet first
- Then try adding Polkadot Hub TestNet manually
- Use Goerli as a fallback for testing

### 4. MetaMask Settings
- Ensure "Show test networks" is enabled
- Check if "Auto-detect tokens" is enabled
- Clear MetaMask cache if needed

## Quick Fixes

### For Chain ID Mismatch:
1. **Cancel** the network addition in MetaMask
2. Click **"Manual Network Setup"** in the app
3. Follow the **step-by-step instructions**
4. Add the network **manually** with exact details

### For Connection Issues:
1. **Refresh** the page
2. **Unlock** MetaMask
3. **Try again** with "Connect Wallet"

### For Testing Purposes:
1. **Use Goerli testnet** as fallback
2. **Get GoerliETH** from https://goerlifaucet.com/
3. **Test the app** functionality

## Success Indicators

✅ **Wallet Connected**: Address shows in top-right corner
✅ **Network Active**: Correct network name in MetaMask
✅ **Balance Visible**: Token balance displayed (if applicable)
✅ **Transactions Work**: Can sign messages and interact with blockchain

## Still Having Issues?

If you're still experiencing problems:

1. **Try the fallback network** (Goerli)
2. **Use manual network setup**
3. **Check the browser console** for detailed error messages
4. **Ensure MetaMask is updated** to the latest version
5. **Try a different browser** (Chrome, Firefox, Edge)

Remember: The app will work with any EVM-compatible network, so you can test the core functionality even if Polkadot Hub TestNet doesn't work perfectly with MetaMask.
