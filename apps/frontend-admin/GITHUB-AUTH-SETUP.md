# GitHub OAuth Setup for Basketball Admin

## Overview

The Basketball Admin frontend now supports GitHub OAuth for secure authentication. Users can log in with their GitHub accounts to access the crawl logs and admin features.

## Features

✅ **GitHub OAuth Integration** - Secure login with GitHub accounts  
✅ **Fallback Demo Login** - admin/password for testing  
✅ **User Profile Display** - Shows GitHub avatar and username  
✅ **Session Management** - Secure JWT-like sessions with HttpOnly cookies  
✅ **CSRF Protection** - State parameter verification  

## Setup Instructions

### 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/applications/new)
2. Create a new OAuth App with these settings:
   - **Application name**: `Basketball Admin`
   - **Homepage URL**: `http://localhost:8081`
   - **Authorization callback URL**: `http://localhost:8081/api/auth/github/callback`

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your GitHub OAuth credentials:
   ```bash
   GITHUB_CLIENT_ID=your_actual_client_id
   GITHUB_CLIENT_SECRET=your_actual_client_secret
   BASE_URL=http://localhost:8081
   ```

### 3. Production Setup

For production deployment:

1. Update GitHub OAuth app with production URLs
2. Set production environment variables:
   ```bash
   GITHUB_CLIENT_ID=prod_client_id
   GITHUB_CLIENT_SECRET=prod_client_secret
   BASE_URL=https://your-domain.com
   ```

## API Endpoints

The following authentication endpoints are available:

- `GET /api/auth/github` - Initiate GitHub OAuth flow
- `GET /api/auth/github/callback` - Handle GitHub OAuth callback
- `GET /api/auth/me` - Get current user information
- `POST /api/auth/logout` - Logout and clear session

## Usage

### GitHub Login
1. Click "Login with GitHub" on the login page
2. Authorize the app on GitHub
3. Get redirected back to the admin dashboard

### Demo Login (for testing)
- Username: `admin`
- Password: `password`

### User Profile
- GitHub avatar displayed in navigation
- Username and name shown in dropdown
- Logout option available

## Security Features

- **State Parameter**: CSRF protection during OAuth flow
- **HttpOnly Cookies**: Session tokens not accessible via JavaScript
- **SameSite Strict**: Cookie protection against CSRF
- **Secure Cookies**: HTTPS-only in production
- **Session Expiry**: 24-hour session lifetime

## Development

The system works without GitHub OAuth setup - the demo login will always work for testing. GitHub OAuth is gracefully degraded when not properly configured.

## Troubleshooting

### GitHub OAuth not working
1. Check that `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are correctly set
2. Verify the callback URL matches exactly: `http://localhost:8081/api/auth/github/callback`
3. Ensure the GitHub OAuth app is not suspended

### Demo login not working
- Default credentials are `admin` / `password`
- Demo login works independently of GitHub OAuth configuration

### Session issues
- Clear browser cookies for `localhost:8081`
- Check that cookies are being set (dev tools → Application → Cookies)
