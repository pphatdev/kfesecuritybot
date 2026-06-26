export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const query = getQuery(event)
    let name = query.name as string
    if (!name) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Sticker set name is required'
      })
    }

    // Extract sticker pack name from link formats (t.me/addstickers/Name, telegram.me/addstickers/Name, tg://addstickers?set=Name)
    name = name.trim()
    const linkRegex = /(?:t\.me|telegram\.me)\/addstickers\/([a-zA-Z0-9_]+)/i
    const linkMatch = name.match(linkRegex)
    if (linkMatch) {
      name = linkMatch[1]!
    } else {
      const tgRegex = /tg:\/\/addstickers\?set=([a-zA-Z0-9_]+)/i
      const tgMatch = name.match(tgRegex)
      if (tgMatch) {
        name = tgMatch[1]!
      } else if (name.includes('/')) {
        const parts = name.split('/')
        const last = parts[parts.length - 1]?.trim()
        if (last) name = last
      }
    }

    const env = getParentEnv()
    const botToken = env.TELEGRAM_BOT_TOKEN
    if (!botToken || botToken === 'your_telegram_bot_token_here') {
      throw createError({
        statusCode: 500,
        statusMessage: 'Bot token not configured on server.'
      })
    }

    const response = await fetch(`https://api.telegram.org/bot${botToken}/getStickerSet?name=${encodeURIComponent(name)}`)
    const data = await response.json()
    if (!response.ok || !data.ok) {
      const isNotFound = response.status === 404 || data.description?.includes('STICKERSET_INVALID')
      throw createError({
        statusCode: isNotFound ? 404 : 500,
        statusMessage: isNotFound 
          ? 'Sticker pack not found. Ensure the name or link is correct (case-sensitive).' 
          : (data.description || 'Failed to fetch sticker set')
      })
    }

    return { success: true, result: data.result }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
