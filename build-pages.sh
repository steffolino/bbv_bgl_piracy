#!/bin/bash

# Cloudflare Pages Build Script for Frontend Public
# Build using pnpm for workspace support

echo "🚀 Building Basketball Analytics Frontend for Cloudflare Pages"

# Install all workspace dependencies from root
echo "📦 Installing workspace dependencies..."
pnpm install

# Build only the frontend-public app using pnpm filter
echo "🏗️ Building frontend with workspace support..."
pnpm run build --filter=@bg/frontend-public

echo "✅ Frontend build complete!"
echo "📁 Output directory: apps/frontend-public/.output/public"

echo "🎉 Ready for Cloudflare Pages deployment!"
