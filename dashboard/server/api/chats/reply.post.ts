import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const chatId = body?.chat_id
    const replyToMessageId = body?.reply_to_message_id
    const text = typeof body?.text === 'string' ? body.text : ''

    if (chatId === undefined || chatId === null || chatId === '') {
      throw createError({ statusCode: 400, statusMessage: 'chat_id is required' })
    }
    if (replyToMessageId === undefined || replyToMessageId === null || replyToMessageId === '') {
      throw createError({ statusCode: 400, statusMessage: 'reply_to_message_id is required' })
    }
    if (!text.trim()) {
      throw createError({ statusCode: 400, statusMessage: 'text is required' })
    }

    const env = getParentEnv()
    const botToken = env.TELEGRAM_BOT_TOKEN
    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({ statusCode: 500, statusMessage: 'Bot token not configured on server.' })
    }

    const apiUrl = `https://api.telegram.org/bot${botToken}/sendMessage`
    const payload = {
      chat_id: chatId,
      text,
      parse_mode: 'HTML',
      reply_parameters: {
        message_id: Number(replyToMessageId),
        allow_sending_without_reply: true
      }
    }
    const tgResponse = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const tgResult: any = await tgResponse.json()
    if (!tgResponse.ok || !tgResult?.ok) {
      throw createError({
        statusCode: 400,
        statusMessage: tgResult?.description || 'Failed to send reply via Telegram'
      })
    }

    // Log the sent reply into chat_history.json so the UI reflects it on next poll
    try {
      const historyDbPath = path.resolve(process.cwd(), '../data/chat_history.json')
      let historyData: Record<string, any[]> = {}
      if (fs.existsSync(historyDbPath)) {
        historyData = JSON.parse(fs.readFileSync(historyDbPath, 'utf-8'))
      }
      const strChatId = String(chatId)
      const chatList = historyData[strChatId] || []
      const timeStr = new Date().toLocaleTimeString('en-US', {
        hour: 'numeric', minute: '2-digit', hour12: false, timeZone: 'Asia/Phnom_Penh'
      })
      chatList.push({
        message_id: tgResult.result?.message_id || Date.now(),
        sender_id: tgResult.result?.from?.id || 0,
        sender: tgResult.result?.from?.first_name || 'Bot',
        text,
        timestamp: Math.floor(Date.now() / 1000),
        time: timeStr,
        is_bot: true,
        sticker_id: null,
        media_type: null,
        media_name: null,
        buttons: null,
        is_deleted: false,
        delete_reason: null,
        reply_to_message_id: Number(replyToMessageId)
      })
      historyData[strChatId] = chatList.slice(-100)
      const tmp = historyDbPath + '.tmp'
      fs.writeFileSync(tmp, JSON.stringify(historyData, null, 2), 'utf-8')
      fs.renameSync(tmp, historyDbPath)
    } catch (err) {
      console.error('Failed to log reply to chat history:', err)
    }

    return { success: true, message_id: tgResult.result?.message_id }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
