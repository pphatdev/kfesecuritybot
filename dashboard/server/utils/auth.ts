import fs from 'node:fs'
import path from 'node:path'
import { H3Event } from 'h3'

const SESSIONS_FILE = path.resolve(process.cwd(), '../data/sessions.json')

export interface Session {
  user_id: number
  username: string
  expires_at: number
}

export function loadSessions(): Record<string, Session> {
  if (!fs.existsSync(SESSIONS_FILE)) {
    return {}
  }
  try {
    const data = fs.readFileSync(SESSIONS_FILE, 'utf-8')
    return JSON.parse(data)
  } catch (error) {
    console.error('Error reading sessions file:', error)
    return {}
  }
}

export function saveSessions(sessions: Record<string, Session>) {
  try {
    fs.writeFileSync(SESSIONS_FILE, JSON.stringify(sessions, null, 2), 'utf-8')
  } catch (error) {
    console.error('Error saving sessions file:', error)
  }
}

export function verifySession(event: H3Event): Session {
  const token = getCookie(event, 'session_token')
  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized'
    })
  }

  const sessions = loadSessions()
  const session = sessions[token]

  if (!session || session.expires_at < Math.floor(Date.now() / 1000)) {
    if (session) {
      // Clean up expired session
      delete sessions[token]
      saveSessions(sessions)
    }
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized'
    })
  }

  return session
}
