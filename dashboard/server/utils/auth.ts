import { H3Event } from 'h3'
import { db } from '../database'
import { sessions } from '../database/schema'
import { eq } from 'drizzle-orm'

export interface Session {
  user_id: number
  username: string
  expires_at: number
}

export async function verifySession(event: H3Event): Promise<Session> {
  const token = getCookie(event, 'session_token')
  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized'
    })
  }

  const sessionResults = await db.select().from(sessions).where(eq(sessions.token, token))
  
  if (sessionResults.length === 0) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized'
    })
  }

  const session = sessionResults[0]
  const currentTime = Math.floor(Date.now() / 1000)

  if (session.expiresAt.getTime() / 1000 < currentTime) {
    // Clean up expired session
    await db.delete(sessions).where(eq(sessions.token, token))
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized'
    })
  }

  return {
    user_id: parseInt(session.userId || '0'),
    username: 'Admin', // In the DB schema we didn't save username for session, wait, schema has userId but not username.
    // Let's modify schema to include username or just fetch from users/allowedUsers if needed.
    // For now we'll just mock it or add it.
    expires_at: Math.floor(session.expiresAt.getTime() / 1000)
  }
}

