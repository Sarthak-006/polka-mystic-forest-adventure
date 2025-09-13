# Vercel Deployment Guide

## Quick Deploy to Vercel

Your Polkadot Forest Adventure with MetaMask integration is ready for Vercel deployment!

### Prerequisites
- Vercel account (free at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)

### Deployment Steps

1. **Push to Git Repository**
   ```bash
   git add .
   git commit -m "Add Polkadot integration and MetaMask support"
   git push origin main
   ```

   **Repository**: [https://github.com/Sarthak-006/polka-mystic-forest-adventure](https://github.com/Sarthak-006/polka-mystic-forest-adventure)

2. **Deploy on Vercel**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your Git repository
   - Vercel will automatically detect it's a Python project
   - Click "Deploy"

3. **Configuration**
   - The `vercel.json` is already configured
   - All dependencies are in `requirements.txt`
   - No additional setup needed

### What's Included

✅ **Flask Backend** (`api/index.py`)
- Game state management
- Blockchain integration endpoints
- MetaMask wallet support
- Polkadot Hub TestNet configuration

✅ **Frontend** (`public/`)
- Interactive game interface
- MetaMask wallet connection
- Polkadot branding and features
- Responsive design

✅ **Vercel Configuration** (`vercel.json`)
- Python runtime configuration
- CORS headers for MetaMask
- Static file serving
- API routing

### Features After Deployment

- 🌐 **Live URL**: Your app will be available at `https://your-project.vercel.app`
- 🔗 **MetaMask Integration**: Full wallet connection support
- 💎 **Polkadot Features**: DOT token display, blockchain saves
- 🎮 **Interactive Game**: Complete adventure experience
- 📱 **Mobile Responsive**: Works on all devices

### Environment Variables

No environment variables needed! The app works out of the box.

### Custom Domain (Optional)

1. Go to your Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Monitoring

- View logs in Vercel dashboard
- Monitor API usage
- Check deployment status

### Troubleshooting

If deployment fails:
1. Check that all files are committed
2. Ensure `requirements.txt` is in root directory
3. Verify `vercel.json` syntax
4. Check Vercel logs for specific errors

### Production Notes

- The app uses file-based storage for blockchain records
- MetaMask integration works with any EVM-compatible network
- Polkadot Hub TestNet may require manual network addition
- All features are production-ready

---

**Your Polkadot Forest Adventure is ready to deploy! 🚀**
