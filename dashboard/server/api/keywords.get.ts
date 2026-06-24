import { db } from '../database'
import { keywords } from '../database/schema'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const allKeywords = await db.select().from(keywords)
    
    const parsedData: Record<string, any[]> = {
      spam: [],
      toxic: [],
      pattern: [],
      sticker: []
    }
    
    for (const kw of allKeywords) {
      if (kw.category === 'pattern') {
        parsedData.pattern.push({ id: kw.id, word: kw.word, response: kw.response || '' })
      } else if (parsedData[kw.category]) {
        parsedData[kw.category].push(kw.word)
      }
    }
    
    return parsedData
  } catch (error) {
    console.error('Error reading keywords from DB:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read keywords'
    })
  }
})
