// Get current user info
export default defineEventHandler(async (event) => {
  const cookies = parseCookies(event)
  const authCookie = cookies['admin-auth']
  
  if (!authCookie) {
    return { authenticated: false }
  }
  
  try {
    const sessionData = JSON.parse(atob(authCookie))
    return {
      authenticated: true,
      user: sessionData.user,
      loginTime: sessionData.loginTime
    }
  } catch (error) {
    return { authenticated: false }
  }
})
