import zlib from 'node:zlib'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const query = getQuery(event)
    const fileId = query.file_id as string
    if (!fileId) {
      throw createError({
        statusCode: 400,
        statusMessage: 'file_id is required'
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

    // 1. Get file path
    const fileResponse = await fetch(`https://api.telegram.org/bot${botToken}/getFile?file_id=${encodeURIComponent(fileId)}`)
    const fileData = await fileResponse.json()
    if (!fileResponse.ok || !fileData.ok) {
      throw createError({
        statusCode: 500,
        statusMessage: fileData.description || 'Failed to get sticker file info'
      })
    }

    const filePath = fileData.result.file_path
    if (!filePath) {
      throw createError({
        statusCode: 500,
        statusMessage: 'File path not returned'
      })
    }

    // 2. Fetch the actual file content
    const imgResponse = await fetch(`https://api.telegram.org/file/bot${botToken}/${filePath}`)
    if (!imgResponse.ok) {
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to download sticker file'
      })
    }

    const buffer = await imgResponse.arrayBuffer()
    let dataBuffer = Buffer.from(buffer)
    
    let mimeType = 'image/webp'
    const lowerPath = filePath.toLowerCase()
    if (lowerPath.endsWith('.webp')) {
      mimeType = 'image/webp'
    } else if (lowerPath.endsWith('.jpg') || lowerPath.endsWith('.jpeg')) {
      mimeType = 'image/jpeg'
    } else if (lowerPath.endsWith('.png')) {
      mimeType = 'image/png'
    } else if (lowerPath.endsWith('.gif')) {
      mimeType = 'image/gif'
    } else if (lowerPath.endsWith('.webm')) {
      mimeType = 'video/webm'
    } else if (lowerPath.endsWith('.tgs')) {
      mimeType = 'application/json'
      try {
        dataBuffer = zlib.gunzipSync(dataBuffer)
      } catch (err) {
        console.error('Failed to gunzip TGS sticker:', err)
      }
    }

    setResponseHeader(event, 'Content-Type', mimeType)
    setResponseHeader(event, 'Cache-Control', 'public, max-age=31536000, immutable')

    return dataBuffer
  } catch (error: any) {
    console.error('Error in stickers/image proxy:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
