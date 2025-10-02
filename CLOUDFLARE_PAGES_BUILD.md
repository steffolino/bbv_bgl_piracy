# Cloudflare Pages Configuration

## Build Settings for Cloudflare Pages

When setting up your Cloudflare Pages project, use these settings:

### Build Configuration
- **Framework preset**: Static site
- **Build command**: `cd apps/frontend-public && npm install && npm run build`
- **Build output directory**: `apps/frontend-public/.output/public`
- **Root directory**: `/` (leave as root)
- **Node.js version**: `20`

### Environment Variables
None required - the frontend uses the deployed API at:
`https://basketball-api.inequality.workers.dev`

### Alternative: Custom Build Script
If the above doesn't work, you can use:
- **Build command**: `chmod +x build-pages.sh && ./build-pages.sh`
- **Build output directory**: `public`

## Expected Result
Your basketball analytics will be available at:
`https://[your-project].pages.dev/basketball`

## Why This Works
- ✅ Builds only the frontend (not the API worker)
- ✅ Uses the already-deployed Cloudflare Workers API
- ✅ Generates static files for optimal performance
- ✅ No server dependencies required
