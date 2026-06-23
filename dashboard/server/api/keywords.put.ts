import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const { category, oldWord, newWord, newResponse } = body
    
    if (!category || !oldWord || !newWord) {
      throw createError({ statusCode: 400, statusMessage: 'Category, oldWord, and newWord are required' })
    }

    const filePath = path.resolve(process.cwd(), '../data/custom_keywords.json')
    if (!fs.existsSync(filePath)) {
      throw createError({ statusCode: 404, statusMessage: 'Keywords file not found' })
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    const data = JSON.parse(fileData)
    
    if (!data[category]) {
      throw createError({ statusCode: 400, statusMessage: 'Invalid category' })
    }

    if (category === 'pattern') {
      const lowerOldWord = oldWord.trim()
      const lowerNewWord = newWord.trim()
      
      const idx = data.pattern.findIndex((p: any) => (typeof p === 'string' ? p : p.word) === lowerOldWord)
      if (idx === -1) {
        throw createError({ statusCode: 404, statusMessage: 'Original keyword not found' })
      }
      
      // Check for conflict if word is changing
      if (lowerOldWord !== lowerNewWord) {
        const conflict = data.pattern.some((p: any) => (typeof p === 'string' ? p : p.word) === lowerNewWord)
        if (conflict) {
          throw createError({ statusCode: 400, statusMessage: 'New keyword already exists' })
        }
      }
      
      data.pattern[idx] = { word: lowerNewWord, response: newResponse || '' }
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
      return { success: true, message: `Updated pattern '${lowerOldWord}'` }
      
    } else if (category === 'sticker') {
      const trimmedOldWord = oldWord.trim()
      const trimmedNewWord = newWord.trim()
      
      const idx = data[category].indexOf(trimmedOldWord)
      if (idx === -1) {
        throw createError({ statusCode: 404, statusMessage: 'Original keyword not found' })
      }
      
      if (trimmedOldWord !== trimmedNewWord && data[category].includes(trimmedNewWord)) {
        throw createError({ statusCode: 400, statusMessage: 'New keyword already exists' })
      }
      
      data[category][idx] = trimmedNewWord
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
      return { success: true, message: `Updated sticker '${trimmedOldWord}'` }
      
    } else {
      const lowerOldWord = oldWord.trim().toLowerCase()
      const lowerNewWord = newWord.trim().toLowerCase()
      
      const idx = data[category].indexOf(lowerOldWord)
      if (idx === -1) {
        throw createError({ statusCode: 404, statusMessage: 'Original keyword not found' })
      }
      
      if (lowerOldWord !== lowerNewWord && data[category].includes(lowerNewWord)) {
        throw createError({ statusCode: 400, statusMessage: 'New keyword already exists' })
      }
      
      data[category][idx] = lowerNewWord
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
      return { success: true, message: `Updated keyword '${lowerOldWord}'` }
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to update keyword'
    })
  }
})
