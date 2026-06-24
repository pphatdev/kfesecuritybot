export default defineEventHandler(async (event) => {
  try {
    const session = await verifySession(event)
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
