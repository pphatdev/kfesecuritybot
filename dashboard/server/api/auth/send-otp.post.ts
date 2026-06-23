import fs from 'node:fs'
import path from 'node:path'

const OTP_FILE = path.resolve(process.cwd(), '../data/otps.json')

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { username_or_id } = body

    if (!username_or_id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Username or ID is required'
      })
    }

    const val = username_or_id.toString().trim()
    const lowerVal = val.toLowerCase().replace(/^@/, '')

    // Resolve username <-> user_id
    const usersDbPath = path.resolve(process.cwd(), '../data/users.json')
    let resolvedUsername = lowerVal
    let resolvedUserId = lowerVal
    const isNumericInput = /^\d+$/.test(lowerVal)

    if (fs.existsSync(usersDbPath)) {
      try {
        const usersData = JSON.parse(fs.readFileSync(usersDbPath, 'utf-8'))
        if (isNumericInput) {
          if (usersData[lowerVal] && usersData[lowerVal].username) {
            resolvedUsername = usersData[lowerVal].username
          }
        } else {
          for (const [uid, udata] of Object.entries(usersData)) {
            if ((udata as any).username === lowerVal) {
              resolvedUserId = uid
              break
            }
          }
        }
      } catch(e) {
         console.error('Error reading users.json', e)
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
    const adminUsernames = (env.DASHBOARD_ADMINS || '')
      .split(',')
      .map((u) => u.trim().toLowerCase())
      .filter(Boolean)
    const adminIds = (env.DASHBOARD_ADMIN_IDS || '')
      .split(',')
      .map((id) => id.trim())
      .filter(Boolean)

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
      throw createError({
        statusCode: 403,
        statusMessage: 'You are not authorized to access this dashboard.'
      })
    }

    // 2. Generate OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString()
    const expiresAt = Math.floor(Date.now() / 1000) + 300 // 5 minutes

    let otps: any = {}
    if (fs.existsSync(OTP_FILE)) {
      try {
        otps = JSON.parse(fs.readFileSync(OTP_FILE, 'utf-8'))
      } catch (e) {
        // Ignore JSON parse errors, will overwrite
      }
    }

    // Save OTP using the resolved user ID
    otps[resolvedUserId] = {
      otp: otp,
      username: resolvedUsername,
      expires_at: expiresAt
    }

    fs.mkdirSync(path.dirname(OTP_FILE), { recursive: true })
    fs.writeFileSync(OTP_FILE, JSON.stringify(otps, null, 2), 'utf-8')

    // 3. Send OTP via Telegram HTTP API
    const botToken = env.TELEGRAM_BOT_TOKEN
    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({
        statusCode: 500,
        statusMessage: 'Bot token not configured on server.'
      })
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
        statusMessage: `Failed to send OTP via Telegram. Please ensure you have started a private chat with the bot first. Error: ${tgResult.description || 'Unknown error'}`
      })
    }

    return { success: true }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
