import { db } from '../../database'
import { users, otps, allowedUsers } from '../../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { username_or_id } = body

    if (!username_or_id) {
      throw createError({ statusCode: 400, statusMessage: 'Username or ID is required' })
    }

    const val = username_or_id.toString().trim()
    const lowerVal = val.toLowerCase().replace(/^@/, '')

    let resolvedUsername = lowerVal
    let resolvedUserId = lowerVal
    const isNumericInput = /^\d+$/.test(lowerVal)

    if (isNumericInput) {
      const userRes = await db.select().from(users).where(eq(users.id, lowerVal))
      const firstUser = userRes[0]
      if (firstUser && firstUser.username) {
        resolvedUsername = firstUser.username.toLowerCase()
      }
    } else {
      const userRes = await db.select().from(users)
      const foundUser = userRes.find(u => u.username?.toLowerCase() === lowerVal)
      if (foundUser) {
        resolvedUserId = foundUser.id
      }
    }

    if (!isNumericInput && resolvedUserId === lowerVal) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Could not find your Telegram ID. Please start a conversation with the bot (send /start) first.'
      })
    }

    // 1. Authorization Check
    const env = getParentEnv()
    const adminUsernames = (env.DASHBOARD_ADMINS || '').split(',').map((u: string) => u.trim().toLowerCase()).filter(Boolean)
    const adminIds = (env.DASHBOARD_ADMIN_IDS || '').split(',').map((id: string) => id.trim()).filter(Boolean)

    const dbAllowed = await db.select().from(allowedUsers)
    const allowedUsernamesJson = dbAllowed.filter(u => u.type === 'username').map(u => u.value.toLowerCase())
    const allowedIdsJson = dbAllowed.filter(u => u.type === 'id').map(u => u.value)

    let isAuthorized = false
    const noListsDefined = adminUsernames.length === 0 && adminIds.length === 0 && allowedUsernamesJson.length === 0 && allowedIdsJson.length === 0
    
    if (noListsDefined) {
      isAuthorized = true
    } else {
      if (adminIds.includes(resolvedUserId) || allowedIdsJson.includes(resolvedUserId)) {
        isAuthorized = true
      }
      if (adminUsernames.includes(resolvedUsername) || allowedUsernamesJson.includes(resolvedUsername)) {
        isAuthorized = true
      }
    }

    if (!isAuthorized) {
      throw createError({ statusCode: 403, statusMessage: 'You are not authorized to access this dashboard.' })
    }

    // 2. Generate OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString()
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000)

    const existingOtp = await db.select().from(otps).where(eq(otps.userId, resolvedUserId))
    if (existingOtp.length > 0) {
      await db.update(otps).set({ otp, expiresAt, username: resolvedUsername }).where(eq(otps.userId, resolvedUserId))
    } else {
      await db.insert(otps).values({ userId: resolvedUserId, username: resolvedUsername, otp, expiresAt })
    }

    // 3. Send OTP via Telegram HTTP API
    const botToken = env.TELEGRAM_BOT_TOKEN
    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({ statusCode: 500, statusMessage: 'Bot token not configured on server.' })
    }

    const text = `🔐 *BotControl Dashboard Login*\n\nYour One-Time Password (OTP) is: \`${otp}\`\nIt is valid for 5 minutes.\n\nEnter this OTP on the dashboard login page.`

    const tgResponse = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: resolvedUserId,
        text: text,
        parse_mode: 'Markdown'
      })
    })

    const tgResult = await tgResponse.json()

    if (!tgResponse.ok || !tgResult.ok) {
      console.error('Telegram API Error:', tgResult)
      throw createError({
        statusCode: 400,
        statusMessage: `Failed to send OTP via Telegram. Error: ${tgResult.description || 'Unknown error'}`
      })
    }

    return { success: true }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error'
    })
  }
})
