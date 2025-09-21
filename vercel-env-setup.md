# 🔐 Vercel Environment Variables Setup

## Quick Setup Commands

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Login to Vercel
vercel login

# Add environment variables
vercel env add GEMINI_API_KEY
# When prompted, enter your actual Gemini API key
# Select: Production, Preview, Development

vercel env add DEVELOPMENT_MODE
# Enter: false
# Select: Production only

# Deploy with new environment variables
vercel --prod
```

## Visual Guide - Dashboard Method

### Step 1: Go to Project Settings
```
vercel.com → Your Project → Settings Tab
```

### Step 2: Find Environment Variables Section
```
Settings → Environment Variables → Add New
```

### Step 3: Add Variables
```
Variable 1:
Name: GEMINI_API_KEY
Value: AIzaSy... (your actual key)
Environments: ✅ Production ✅ Preview ✅ Development

Variable 2:
Name: DEVELOPMENT_MODE
Value: false  
Environments: ✅ Production only
```

### Step 4: Save & Redeploy
```
Click "Save" → Trigger new deployment
```

## 🚀 Your Specific Variables for This Project

Add these exact environment variables:

| Variable | Value | Environment | Purpose |
|----------|-------|-------------|---------|
| `GEMINI_API_KEY` | `your_actual_key_here` | All | Your built-in API key for free tier |
| `DEVELOPMENT_MODE` | `false` | Production | Forces production mode |
| `FREE_TIER_DAILY_LIMIT` | `3` | Production | Conservative free tier limit |

## ⚠️ Important Notes

1. **Never commit API keys to Git!** Always use environment variables
2. **Production vs Preview**: Set different values for different environments
3. **Redeploy Required**: Changes take effect after redeployment
4. **Case Sensitive**: Variable names are case-sensitive

## 🔍 Verify Your Setup

After deployment, check if variables are working:

```bash
# Check your deployment
curl https://your-app.vercel.app/api/health

# Should return:
{
  "status": "ok",
  "service": "PRD to Test Case Generator", 
  "free_tier_available": true,
  "development_mode": false,  ← Should be false in production
  "tier": "production"
}
```

## 🆘 Troubleshooting

### Environment Variable Not Working?
1. Check spelling (case-sensitive)
2. Make sure you selected the right environment
3. Redeploy after adding variables
4. Check the "Functions" logs in Vercel dashboard

### Still in Development Mode?
```bash
# Force production mode
vercel env add DEVELOPMENT_MODE
# Enter: false
# Select: Production only
# Then redeploy
```

### API Key Not Found?
1. Double-check your Gemini API key is valid
2. Make sure `GEMINI_API_KEY` is set in Production environment
3. Check Vercel Function logs for any errors
