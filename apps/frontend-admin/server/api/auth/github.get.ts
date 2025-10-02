// GitHub OAuth login endpoint
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  
  const params = new URLSearchParams({
    client_id: config.public.githubClientId as string,
    redirect_uri: `${config.public.baseUrl}/api/auth/github/callback`,
    scope: 'user:email',
    state: generateRandomState()
  })
  
  // Store state in session for verification
  await setResponseHeader(event, 'Set-Cookie', `oauth_state=${params.get('state')}; HttpOnly; SameSite=Strict; Max-Age=600`)
  
  return sendRedirect(event, `https://github.com/login/oauth/authorize?${params.toString()}`)
})

function generateRandomState(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
}
