import { db } from '../../database'
import { sessions, otps, users, allowedUsers } from '../../database/schema'
import { eq } from 'drizzle-orm'
import { randomUUID } from 'node:crypto'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { username_or_id, otp } = body

    if (!username_or_id || !otp) {
      throw createError({ statusCode: 400, statusMessage: 'Username/ID and OTP are required' })
    }

    const searchVal = username_or_id.toString().trim().toLowerCase().replace(/^@/, '')

    const otpRes = await db.select().from(otps)
    let matchedUserId: string | null = null
    let otpDetails: any = null

    for (const item of otpRes) {
      const isIdMatch = item.userId === searchVal
      const isUsernameMatch = item.username && item.username.toLowerCase() === searchVal

      if (isIdMatch || isUsernameMatch) {
        if (item.otp.toString().trim() === otp.toString().trim()) {
          matchedUserId = item.userId
          otpDetails = item
          break
        }
      }
    }

    if (!matchedUserId || !otpDetails) {
      throw createError({ statusCode: 401, statusMessage: 'Invalid username/ID or OTP' })
    }

    const currentTime = new Date()

    if (otpDetails.expiresAt < currentTime) {
      await db.delete(otps).where(eq(otps.userId, matchedUserId))
      throw createError({ statusCode: 401, statusMessage: 'OTP has expired. Please request a new one.' })
    }

    // Check against authorized admin lists in parent .env
    const env = getParentEnv()
    const adminUsernames = (env.DASHBOARD_ADMINS || '').split(',').map((u: string) => u.trim().toLowerCase()).filter(Boolean)
    const adminIds = (env.DASHBOARD_ADMIN_IDS || '').split(',').map((id: string) => id.trim()).filter(Boolean)

    const dbAllowed = await db.select().from(allowedUsers)
    const allowedUsernamesJson = dbAllowed.filter(u => u.type === 'username').map(u => u.value.toLowerCase())
    const allowedIdsJson = dbAllowed.filter(u => u.type === 'id').map(u => u.value)

    let isAuthorized = false
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
      throw createError({ statusCode: 403, statusMessage: 'You are not authorized to access this dashboard.' })
    }

    // OTP is valid and user is authorized! Clean up OTP
    await db.delete(otps).where(eq(otps.userId, matchedUserId))

    // Create session
    const sessionToken = randomUUID()
    const sessionExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000)

    await db.insert(sessions).values({
      token: sessionToken,
      userId: matchedUserId,
      username: otpDetails.username,
      expiresAt: sessionExpiresAt
    })

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
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error'
    })
  }
})
