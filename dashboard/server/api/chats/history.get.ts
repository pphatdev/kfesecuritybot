import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const chatId = query.chat_id as string
  
  if (!chatId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'chat_id parameter is required'
    })
  }

  const historyDbPath = path.resolve(process.cwd(), '../data/chat_history.json')
  let historyData: Record<string, any> = {}

  if (fs.existsSync(historyDbPath)) {
    try {
      historyData = JSON.parse(fs.readFileSync(historyDbPath, 'utf-8'))
    } catch (e) {
      console.error('Error reading chat_history.json', e)
    }
  }

  const chatList = historyData[chatId] || []
  return { history: chatList }
})
