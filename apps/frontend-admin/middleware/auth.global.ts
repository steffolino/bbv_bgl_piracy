// Global auth middleware - protect all pages except login
export default defineNuxtRouteMiddleware((to) => {
  // Skip auth check for login page
  if (to.path === '/login') {
    return
  }

  // Check if user is authenticated (simple cookie-based check)
  const authCookie = useCookie('admin-auth', {
    default: () => null,
    secure: true,
    httpOnly: false,
    sameSite: 'strict'
  })

  if (!authCookie.value) {
    return navigateTo('/login')
  }
})