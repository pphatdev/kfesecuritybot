import { db } from '../database'
import { keywords } from '../database/schema'
import { eq, and } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const body = await readBody(event)
    const { category, oldWord, newWord, newResponse } = body
    
    if (!category || !oldWord || !newWord) {
      throw createError({ statusCode: 400, statusMessage: 'Category, oldWord, and newWord are required' })
    }

    const trimmedOldWord = category === 'pattern' || category === 'sticker' ? oldWord.trim() : oldWord.trim().toLowerCase()
    const trimmedNewWord = category === 'pattern' || category === 'sticker' ? newWord.trim() : newWord.trim().toLowerCase()
    
    // Check if new word exists if changing word
    if (trimmedOldWord !== trimmedNewWord) {
      const existing = await db.select().from(keywords).where(
        and(eq(keywords.word, trimmedNewWord), eq(keywords.category, category))
      )
      if (existing.length > 0) {
        throw createError({ statusCode: 400, statusMessage: 'New keyword already exists' })
      }
    }

    const result = await db.update(keywords)
      .set({ 
        word: trimmedNewWord, 
        response: category === 'pattern' ? newResponse || '' : null 
      })
      .where(and(eq(keywords.word, trimmedOldWord), eq(keywords.category, category)))
      
    if (result.changes > 0) {
      return { success: true, message: `Updated keyword '${trimmedOldWord}'` }
    } else {
      throw createError({ statusCode: 404, statusMessage: 'Original keyword not found' })
    }

  } catch (error: any) {
    if (error.statusCode) throw error;
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to update keyword'
    })
  }
})
