export default defineNuxtRouteMiddleware(async (to, from) => {
  const authState = useState<{ authenticated: boolean; user?: { username: string; user_id: number } }>('auth', () => ({
    authenticated: false
  }))

  // Fetch session data on initial load
  const isInitialCheck = useState<boolean>('auth-checked', () => false)
  if (!isInitialCheck.value) {
    try {
      const { data } = await useFetch('/api/auth/session')
      if (data.value) {
        authState.value = data.value as any
      }
    } catch (e) {
      console.error('Failed to fetch auth session:', e)
    }
    isInitialCheck.value = true
  }

  const isAuthenticated = authState.value?.authenticated

  if (to.path === '/login') {
    if (isAuthenticated) {
      return navigateTo('/')
    }
  } else {
    if (!isAuthenticated) {
      return navigateTo('/login')
    }
  }
})
