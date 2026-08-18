import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const chatId = body?.chat_id
    const messageId = body?.message_id

    if (chatId === undefined || chatId === null || chatId === '') {
      throw createError({ statusCode: 400, statusMessage: 'chat_id is required' })
    }
    if (messageId === undefined || messageId === null || messageId === '') {
      throw createError({ statusCode: 400, statusMessage: 'message_id is required' })
    }

    const env = getParentEnv()
    const botToken = env.TELEGRAM_BOT_TOKEN
    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({ statusCode: 500, statusMessage: 'Bot token not configured on server.' })
    }

    const apiUrl = `https://api.telegram.org/bot${botToken}/deleteMessage`
    const tgResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, message_id: Number(messageId) })
    })
    const tgResult: any = await tgResponse.json()

    // Telegram returns 400 "message to delete not found" / "message can't be deleted"
    // if the message is too old (>48h) or was already removed. Still mark it locally.
    const telegramOk = tgResponse.ok && tgResult?.ok === true
    const telegramReason = tgResult?.description || 'Telegram delete failed'

    const historyDbPath = path.resolve(process.cwd(), '../data/chat_history.json')
    if (fs.existsSync(historyDbPath)) {
      try {
        const historyData: Record<string, any[]> = JSON.parse(fs.readFileSync(historyDbPath, 'utf-8'))
        const strChatId = String(chatId)
        const chatList = historyData[strChatId] || []
        const target = chatList.find(m => m.message_id === Number(messageId))
        if (target) {
          target.is_deleted = true
          target.delete_reason = telegramOk ? 'Removed via dashboard' : telegramReason
          historyData[strChatId] = chatList
          const tmp = historyDbPath + '.tmp'
          fs.writeFileSync(tmp, JSON.stringify(historyData, null, 2), 'utf-8')
          fs.renameSync(tmp, historyDbPath)
        }
      } catch (err) {
        console.error('Failed to update chat history after delete:', err)
      }
    }

    if (!telegramOk) {
      throw createError({ statusCode: 400, statusMessage: telegramReason })
    }
    return { success: true }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
