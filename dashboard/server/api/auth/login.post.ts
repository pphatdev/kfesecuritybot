import fs from 'node:fs'
import path from 'node:path'
import { randomUUID } from 'node:crypto'

const OTP_FILE = path.resolve(process.cwd(), '../data/otps.json')

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { username_or_id, otp } = body

    if (!username_or_id || !otp) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Username/ID and OTP are required'
      })
    }

    if (!fs.existsSync(OTP_FILE)) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid username/ID or OTP'
      })
    }

    const otpsData = fs.readFileSync(OTP_FILE, 'utf-8')
    const otps = JSON.parse(otpsData)

    let matchedUserId: string | null = null
    const searchVal = username_or_id.toString().trim().toLowerCase().replace(/^@/, '')

    for (const [userId, item] of Object.entries(otps)) {
      const otpItem = item as any
      const isIdMatch = userId === searchVal
      const isUsernameMatch = otpItem.username && otpItem.username.toLowerCase() === searchVal

      if (isIdMatch || isUsernameMatch) {
        if (otpItem.otp.toString().trim() === otp.toString().trim()) {
          matchedUserId = userId
          break
        }
      }
    }

    if (!matchedUserId) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid username/ID or OTP'
      })
    }

    const otpDetails = otps[matchedUserId]
    const currentTime = Math.floor(Date.now() / 1000)

    if (otpDetails.expires_at < currentTime) {
      // Clean up expired OTP
      delete otps[matchedUserId]
      fs.writeFileSync(OTP_FILE, JSON.stringify(otps, null, 2), 'utf-8')
      throw createError({
        statusCode: 401,
        statusMessage: 'OTP has expired. Please request a new one.'
      })
    }

    // Check against authorized admin lists in parent .env
    const env = getParentEnv()
    const adminUsernames = (env.DASHBOARD_ADMINS || '')
      .split(',')
      .map((u) => u.trim().toLowerCase())
      .filter(Boolean)
    const adminIds = (env.DASHBOARD_ADMIN_IDS || '')
      .split(',')
      .map((id) => id.trim())
      .filter(Boolean)

    // Check against data/allowed_users.json
    const allowedUsersPath = path.resolve(process.cwd(), '../data/allowed_users.json')
    let allowedUsernamesJson: string[] = []
    let allowedIdsJson: string[] = []
    if (fs.existsSync(allowedUsersPath)) {
      try {
        const allowedData = JSON.parse(fs.readFileSync(allowedUsersPath, 'utf-8'))
        allowedUsernamesJson = (allowedData.usernames || []).map((u: string) => u.trim().toLowerCase())
        allowedIdsJson = (allowedData.user_ids || []).map((id: any) => id.toString().trim())
      } catch (e) {
        console.error('Error reading allowed_users.json', e)
      }
    }

    let isAuthorized = false
    // If no lists are defined at all, we fall back to letting anyone who got an OTP in (since bot restricts who can get an OTP).
    if (adminUsernames.length === 0 && adminIds.length === 0 && allowedUsernamesJson.length === 0 && allowedIdsJson.length === 0) {
      isAuthorized = true
    } else {
      if (adminIds.includes(matchedUserId) || allowedIdsJson.includes(matchedUserId)) {
        isAuthorized = true
      }
      if (otpDetails.username) {
        const lowerUser = otpDetails.username.toLowerCase()
        if (adminUsernames.includes(lowerUser) || allowedUsernamesJson.includes(lowerUser)) {
          isAuthorized = true
        }
      }
    }

    if (!isAuthorized) {
      throw createError({
        statusCode: 403,
        statusMessage: 'You are not authorized to access this dashboard.'
      })
    }

    // OTP is valid and user is authorized! Clean up OTP
    delete otps[matchedUserId]
    fs.writeFileSync(OTP_FILE, JSON.stringify(otps, null, 2), 'utf-8')

    // Create session
    const sessionToken = randomUUID()
    const sessions = loadSessions()
    const sessionExpiresAt = currentTime + (24 * 60 * 60) // 24 hours

    sessions[sessionToken] = {
      user_id: parseInt(matchedUserId),
      username: otpDetails.username,
      expires_at: sessionExpiresAt
    }
    saveSessions(sessions)

    // Set cookie
    setCookie(event, 'session_token', sessionToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 24 * 60 * 60, // 24 hours
      path: '/'
    })

    return {
      success: true,
      user: {
        user_id: matchedUserId,
        username: otpDetails.username
      }
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
