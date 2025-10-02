# Cloudflare Pages Configuration

## Build Settings for Cloudflare Pages

When setting up your Cloudflare Pages project, use these settings:

### Build Configuration
- **Framework preset**: Static site  
- **Build command**: `pnpm install && cd apps/frontend-public && pnpm run build`
- **Build output directory**: `apps/frontend-public/.output/public`
- **Deploy command**: `echo "Deploying to Cloudflare Pages"`
- **Root directory**: `/` (leave as root)
- **Node.js version**: `20`

### Environment Variables
Set these in your Cloudflare Pages dashboard under "Settings" > "Environment variables":

**For Basketball Frontend (frontend-public):**
- No environment variables required (uses deployed API automatically)

**For Admin Dashboard (frontend-admin):**
- `DEMO_USERNAME`: Admin login username (default: admin)
- `DEMO_PASSWORD`: Admin login password (default: password)
- `PUBLIC_API_BASE`: API endpoint (default: https://basketball-api.inequality.workers.dev)
- `GITHUB_CLIENT_ID`: GitHub OAuth app ID (optional)
- `GITHUB_CLIENT_SECRET`: GitHub OAuth secret (optional)

### Alternative: Custom Build Script
If the above doesn't work, you can use:
- **Build command**: `pnpm install && pnpm run build --filter=@bg/frontend-public`
- **Build output directory**: `apps/frontend-public/.output/public`

## Expected Result
Your basketball analytics will be available at:
`https://[your-project].pages.dev/basketball`

## Why This Works
- ✅ Builds only the frontend (not the API worker)
- ✅ Uses the already-deployed Cloudflare Workers API
- ✅ Generates static files for optimal performance
- ✅ No server dependencies required
