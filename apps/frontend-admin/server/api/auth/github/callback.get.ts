// GitHub OAuth callback endpoint
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)
  
  const code = query.code as string
  const state = query.state as string
  
  if (!code || !state) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing code or state parameter'
    })
  }
  
  // Verify state to prevent CSRF attacks
  const cookies = parseCookies(event)
  if (cookies.oauth_state !== state) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid state parameter'
    })
  }
  
  try {
    // Exchange code for access token
    const tokenResponse = await $fetch<{
      access_token: string
      token_type: string
      scope: string
    }>('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: {
        client_id: config.public.githubClientId as string,
        client_secret: config.githubClientSecret,
        code: code
      }
    })
    
    // Get user info from GitHub
    const userResponse = await $fetch<{
      login: string
      id: number
      name: string
      email: string
      avatar_url: string
    }>('https://api.github.com/user', {
      headers: {
        'Authorization': `Bearer ${tokenResponse.access_token}`,
        'User-Agent': 'BBV-BGL-Admin'
      }
    })
    
    // Create session
    const sessionData = {
      user: {
        id: userResponse.id,
        username: userResponse.login,
        name: userResponse.name,
        email: userResponse.email,
        avatar: userResponse.avatar_url
      },
      authenticated: true,
      loginTime: new Date().toISOString()
    }
    
    // Set secure session cookie
    const sessionToken = btoa(JSON.stringify(sessionData))
    
    await setResponseHeader(event, 'Set-Cookie', [
      `admin-auth=${sessionToken}; HttpOnly; SameSite=Strict; Max-Age=86400; Path=/`,
      `oauth_state=; HttpOnly; SameSite=Strict; Max-Age=0; Path=/` // Clear state cookie
    ].join(', '))
    
    return sendRedirect(event, '/')
    
  } catch (error) {
    console.error('GitHub OAuth error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Authentication failed'
    })
  }
})
