export default defineEventHandler((event) => {
  const token = getCookie(event, 'session_token')
  if (token) {
    const sessions = loadSessions()
    delete sessions[token]
    saveSessions(sessions)
  }
  
  deleteCookie(event, 'session_token', {
    path: '/'
  })
  
  return {
    success: true
  }
})
