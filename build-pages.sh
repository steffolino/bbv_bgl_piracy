#!/bin/bash

# Cloudflare Pages Build Script for Frontend Public
# Only build the frontend-public app

echo "🚀 Building Basketball Analytics Frontend for Cloudflare Pages"

# Navigate to frontend-public directory
cd apps/frontend-public

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the frontend
echo "🏗️ Building frontend..."
npm run build

echo "✅ Frontend build complete!"
echo "📁 Output directory: apps/frontend-public/.output/public"

# Copy output to root public directory for Pages
echo "📋 Copying build output..."
mkdir -p ../../public
cp -r .output/public/* ../../public/

echo "🎉 Ready for Cloudflare Pages deployment!"
