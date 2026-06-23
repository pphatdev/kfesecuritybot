export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { chatIds, message } = body

    if (!message || typeof message !== 'string') {
      throw createError({
        statusCode: 400,
        statusMessage: 'Message is required'
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

    const results = []
    
    // Send to each chat concurrently using Promise.allSettled
    const requests = chatIds.map(async (chatId) => {
      const tgResponse = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: message,
          parse_mode: 'HTML' // You could use HTML or Markdown depending on preference
        })
      })

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

