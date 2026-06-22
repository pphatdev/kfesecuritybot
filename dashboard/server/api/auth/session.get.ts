export default defineEventHandler((event) => {
  try {
    const session = verifySession(event)
    return {
      authenticated: true,
      user: {
        user_id: session.user_id,
        username: session.username
      }
    }
  } catch (error) {
    return {
      authenticated: false
    }
  }
})
