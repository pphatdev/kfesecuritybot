import { db } from '../../database'
import { sessions } from '../../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'session_token')
  if (token) {
    await db.delete(sessions).where(eq(sessions.token, token))
  }
  
  deleteCookie(event, 'session_token', {
    path: '/'
  })
  
  return {
    success: true
  }
})
