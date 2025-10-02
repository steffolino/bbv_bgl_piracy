# Cloudflare Pages Deployment Instructions

## 🚀 Deploy Basketball Analytics Frontend to Cloudflare Pages

### Step 1: Connect Repository to Cloudflare Pages
1. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
2. Click "Create a project"
3. Connect your GitHub account
4. Select repository: `steffolino/bbv_bgl_piracy`

### Step 2: Configure Build Settings
```
Framework preset: Nuxt.js
Build command: npm run build
Build output directory: .output/public
Root directory: apps/frontend-public
Node.js version: 20
```

### Step 3: Environment Variables (if needed)
```
NODE_VERSION=20
```

### Step 4: Deploy
- Click "Save and Deploy"
- Your site will be available at: `https://bbv-bgl-piracy.pages.dev`

## Benefits of Cloudflare Pages
✅ Free hosting
✅ Global CDN
✅ Automatic deployments on git push
✅ Perfect integration with Cloudflare Workers API
✅ Custom domains supported
✅ HTTPS by default

## Current Setup
- **API**: https://basketball-api.inequality.workers.dev (Cloudflare Workers)
- **Frontend**: Will be deployed to Cloudflare Pages
- **Domain**: Custom .pages.dev subdomain included
