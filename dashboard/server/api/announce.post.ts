import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  try {
    let message = ''
    let chatIds: string[] = []
    let fileData: any = null
    let stickerId = ''
    let buttons: Array<{ text: string, url: string }> = []
    let buttonText = ''
    let buttonUrl = ''
    let stickerThumbId = ''
    let isAnimated = false
    let isVideo = false

    // Check content type to see if it's multipart
    const contentType = getRequestHeader(event, 'content-type') || ''
    
    if (contentType.includes('multipart/form-data')) {
      const multipart = await readMultipartFormData(event)
      if (multipart) {
        for (const field of multipart) {
          if (field.name === 'message') {
            message = field.data.toString('utf-8')
          } else if (field.name === 'chatIds') {
            chatIds.push(field.data.toString('utf-8'))
          } else if (field.name === 'file') {
            fileData = field
          } else if (field.name === 'stickerId') {
            stickerId = field.data.toString('utf-8')
          } else if (field.name === 'buttons') {
            try {
              buttons = JSON.parse(field.data.toString('utf-8'))
            } catch (e) {
              console.error('Failed to parse buttons JSON:', e)
            }
          } else if (field.name === 'buttonText') {
            buttonText = field.data.toString('utf-8')
          } else if (field.name === 'buttonUrl') {
            buttonUrl = field.data.toString('utf-8')
          } else if (field.name === 'stickerThumbId') {
            stickerThumbId = field.data.toString('utf-8')
          } else if (field.name === 'isAnimated') {
            isAnimated = field.data.toString('utf-8') === 'true'
          } else if (field.name === 'isVideo') {
            isVideo = field.data.toString('utf-8') === 'true'
          }
        }
      }
    } else {
      const body = await readBody(event)
      message = body.message
      chatIds = Array.isArray(body.chatIds) ? body.chatIds : [body.chatIds]
      stickerId = body.stickerId || ''
      if (body.buttons) {
        buttons = Array.isArray(body.buttons) ? body.buttons : []
      }
      buttonText = body.buttonText || ''
      buttonUrl = body.buttonUrl || ''
      stickerThumbId = body.stickerThumbId || ''
      isAnimated = body.isAnimated === true || body.isAnimated === 'true'
      isVideo = body.isVideo === true || body.isVideo === 'true'
    }

    if (!fileData && !stickerId && (!message || typeof message !== 'string')) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Message is required when no file or sticker is attached'
      })
    }

    if (!chatIds || !Array.isArray(chatIds) || chatIds.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'At least one target group must be selected'
      })
    }

    const env = getParentEnv()
    const botToken = env.TELEGRAM_BOT_TOKEN

    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({
        statusCode: 500,
        statusMessage: 'Bot token not configured on server.'
      })
    }

    let apiUrl = `https://api.telegram.org/bot${botToken}/sendMessage`
    let method = 'sendMessage'
    let mediaType = ''
    
    if (stickerId) {
      method = 'sendSticker'
      apiUrl = `https://api.telegram.org/bot${botToken}/${method}`
    } else if (fileData) {
      const mime = fileData.type || ''
      if (mime.startsWith('image/')) {
        method = 'sendPhoto'
        mediaType = 'photo'
      } else if (mime.startsWith('video/')) {
        method = 'sendVideo'
        mediaType = 'video'
      } else {
        method = 'sendDocument'
        mediaType = 'document'
      }
      apiUrl = `https://api.telegram.org/bot${botToken}/${method}`
    }

    // Construct inline keyboard markup (each button in its own row)
    let inlineKeyboard: any[] = []
    if (buttons && buttons.length > 0) {
      inlineKeyboard = buttons
        .filter(btn => btn.text && btn.text.trim() && btn.url && btn.url.trim())
        .map(btn => [
          { text: btn.text.trim(), url: btn.url.trim() }
        ])
    } else if (buttonText.trim() && buttonUrl.trim()) {
      inlineKeyboard = [
        [
          { text: buttonText.trim(), url: buttonUrl.trim() }
        ]
      ]
    }

    const replyMarkup = inlineKeyboard.length > 0 ? {
      inline_keyboard: inlineKeyboard
    } : null

    // Send to each chat concurrently using Promise.allSettled
    const requests = chatIds.map(async (chatId) => {
      let fetchOptions: any = { method: 'POST' }

      if (stickerId) {
        fetchOptions.headers = { 'Content-Type': 'application/json' }
        const payload: any = {
          chat_id: chatId,
          sticker: stickerId
        }
        if (replyMarkup) {
          payload.reply_markup = replyMarkup
        }
        fetchOptions.body = JSON.stringify(payload)
      } else if (fileData) {
        const fd = new FormData()
        fd.append('chat_id', chatId)
        fd.append('caption', message)
        fd.append('parse_mode', 'HTML')
        if (replyMarkup) {
          fd.append('reply_markup', JSON.stringify(replyMarkup))
        }
        const blob = new Blob([fileData.data], { type: fileData.type || 'application/octet-stream' })
        fd.append(mediaType, blob, fileData.filename || 'file')
        fetchOptions.body = fd
      } else {
        fetchOptions.headers = { 'Content-Type': 'application/json' }
        const payload: any = {
          chat_id: chatId,
          text: message,
          parse_mode: 'HTML'
        }
        if (replyMarkup) {
          payload.reply_markup = replyMarkup
        }
        fetchOptions.body = JSON.stringify(payload)
      }

      const tgResponse = await fetch(apiUrl, fetchOptions)
      const tgResult = await tgResponse.json()
      if (!tgResponse.ok || !tgResult.ok) {
        throw new Error(tgResult.description || 'Unknown Telegram API error')
      }
      
      // Log to chat history
      try {
        const historyDbPath = path.resolve(process.cwd(), '../data/chat_history.json')
        let historyData: Record<string, any> = {}
        if (fs.existsSync(historyDbPath)) {
          historyData = JSON.parse(fs.readFileSync(historyDbPath, 'utf-8'))
        }
        
        const strChatId = String(chatId)
        const chatList = historyData[strChatId] || []
        
        // Format time (e.g. "02:35 PM")
        const now = new Date()
        const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: false, timeZone: 'Asia/Phnom_Penh' })
        
        const msgButtons = inlineKeyboard.length > 0 ? inlineKeyboard.map(row => row[0]) : null

        const msgEntry = {
          message_id: tgResult.result?.message_id || Date.now(),
          sender_id: tgResult.result?.from?.id || 0,
          sender: tgResult.result?.from?.first_name || 'Bot',
          text: message || (stickerId ? '[Sticker]' : fileData ? `[${mediaType}]` : ''),
          timestamp: Math.floor(Date.now() / 1000),
          time: timeStr,
          is_bot: true,
          sticker_id: stickerId || null,
          sticker_thumb_id: stickerThumbId || null,
          is_animated: isAnimated,
          is_video: isVideo,
          media_type: mediaType || null,
          media_name: fileData ? fileData.filename : null,
          buttons: msgButtons,
          is_deleted: false,
          delete_reason: null
        }
        
        chatList.push(msgEntry)
        historyData[strChatId] = chatList.slice(-100) // Keep last 100
        
        fs.writeFileSync(historyDbPath, JSON.stringify(historyData, null, 2), 'utf-8')
      } catch (err) {
        console.error('Failed to log message to history:', err)
      }
      
      return { chatId, success: true }
    })

    const outcomes = await Promise.allSettled(requests)
    
    const successes = outcomes.filter(o => o.status === 'fulfilled').length
    const failures = outcomes.filter(o => o.status === 'rejected').length

    return { 
      success: true, 
      sent: successes,
      failed: failures,
      details: outcomes.map((o, index) => ({
        chatId: chatIds[index],
        success: o.status === 'fulfilled',
        error: o.status === 'rejected' ? (o.reason as Error).message : null
      }))
    }

  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})

