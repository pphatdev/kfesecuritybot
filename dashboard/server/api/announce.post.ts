export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    let message = ''
    let chatIds: string[] = []
    let fileData: any = null

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
          }
        }
      }
    } else {
      const body = await readBody(event)
      message = body.message
      chatIds = Array.isArray(body.chatIds) ? body.chatIds : [body.chatIds]
    }

    if (!fileData && (!message || typeof message !== 'string')) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Message is required when no file is attached'
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
    
    if (fileData) {
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

    // Send to each chat concurrently using Promise.allSettled
    const requests = chatIds.map(async (chatId) => {
      let fetchOptions: any = { method: 'POST' }

      if (fileData) {
        const fd = new FormData()
        fd.append('chat_id', chatId)
        fd.append('caption', message)
        fd.append('parse_mode', 'HTML')
        const blob = new Blob([fileData.data], { type: fileData.type || 'application/octet-stream' })
        fd.append(mediaType, blob, fileData.filename || 'file')
        fetchOptions.body = fd
      } else {
        fetchOptions.headers = { 'Content-Type': 'application/json' }
        fetchOptions.body = JSON.stringify({
          chat_id: chatId,
          text: message,
          parse_mode: 'HTML'
        })
      }

      const tgResponse = await fetch(apiUrl, fetchOptions)
      const tgResult = await tgResponse.json()
      if (!tgResponse.ok || !tgResult.ok) {
        throw new Error(tgResult.description || 'Unknown Telegram API error')
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

