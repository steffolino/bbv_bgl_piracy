// Global auth middleware - protect all pages except login
export default defineNuxtRouteMiddleware(async (to) => {
  // Skip auth check for login page and API routes
  if (to.path === '/login' || to.path.startsWith('/api/')) {
    return
  }

  // Check if user is authenticated
  try {
    const authData = await $fetch<{ authenticated: boolean; user?: any }>('/api/auth/me')
    
    if (!authData?.authenticated) {
      return navigateTo('/login')
    }
  } catch (error) {
    return navigateTo('/login')
  }
})