import { db } from '../database'
import { keywords } from '../database/schema'
import { eq, and } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const query = getQuery(event)
    const word = query.word as string
    const category = query.category as string
    
    if (!word || !category) {
      throw createError({ statusCode: 400, statusMessage: 'Word and category are required' })
    }

    const result = await db.delete(keywords).where(
      and(eq(keywords.word, word), eq(keywords.category, category))
    )
    
    if (result.changes > 0) {
      return { success: true, message: `Removed '${word}' from ${category}` }
    } else {
      // Return success anyway, assuming it's already removed
      return { success: true, message: `Removed '${word}' from ${category}` }
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to delete keyword'
    })
  }
})
