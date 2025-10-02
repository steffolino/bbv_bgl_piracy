// Logout endpoint
export default defineEventHandler(async (event) => {
  // Clear auth cookie
  await setResponseHeader(event, 'Set-Cookie', 'admin-auth=; HttpOnly; SameSite=Strict; Max-Age=0; Path=/')
  
  return { success: true, message: 'Logged out successfully' }
})
