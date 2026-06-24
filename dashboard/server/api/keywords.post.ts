import { db } from '../database'
import { keywords } from '../database/schema'
import { eq, and } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const body = await readBody(event)
    const { word, category, response } = body
    
    if (!word || !category) {
      throw createError({ statusCode: 400, statusMessage: 'Word and category are required' })
    }

    const trimmedWord = category === 'pattern' || category === 'sticker' ? word.trim() : word.trim().toLowerCase()
    
    const existing = await db.select().from(keywords).where(
      and(eq(keywords.word, trimmedWord), eq(keywords.category, category))
    )
    
    if (existing.length > 0) {
      throw createError({ statusCode: 400, statusMessage: 'Keyword already exists' })
    }
    
    await db.insert(keywords).values({
      word: trimmedWord,
      category,
      response: category === 'pattern' ? response || '' : null
    })
    
    return { success: true, message: `Added '${trimmedWord}' to ${category}` }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to add keyword'
    })
  }
})
