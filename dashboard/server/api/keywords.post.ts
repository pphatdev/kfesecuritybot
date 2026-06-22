import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const { word, category } = body
    
    if (!word || !category) {
      throw createError({ statusCode: 400, statusMessage: 'Word and category are required' })
    }

    const filePath = path.resolve(process.cwd(), '../data/custom_keywords.json')
    if (!fs.existsSync(filePath)) {
      throw createError({ statusCode: 404, statusMessage: 'Keywords file not found' })
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    const data = JSON.parse(fileData)
    if (!data.pattern) data.pattern = []
    
    if (data[category]) {
      const lowerWord = category === 'pattern' ? word.trim() : word.trim().toLowerCase()
      if (data[category].includes(lowerWord)) {
        throw createError({ statusCode: 400, statusMessage: 'Keyword already exists' })
      }
      data[category].push(lowerWord)
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
      return { success: true, message: `Added '${lowerWord}' to ${category}` }
    } else {
      throw createError({ statusCode: 400, statusMessage: 'Invalid category' })
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to add keyword'
    })
  }
})
