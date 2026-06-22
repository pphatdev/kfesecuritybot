import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler((event) => {
  verifySession(event)
  try {
    // Path to the python bot's keywords json file
    const filePath = path.resolve(process.cwd(), '../data/custom_keywords.json')
    
    if (!fs.existsSync(filePath)) {
      return { 
        spam: [], 
        toxic: [], 
        pattern: [],
        debug_error: "File not found", 
        debug_path: filePath 
      }
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    const parsedData = JSON.parse(fileData)
    
    // Normalize pattern array to objects for the UI
    if (parsedData.pattern && Array.isArray(parsedData.pattern)) {
      parsedData.pattern = parsedData.pattern.map((p: any) => {
        if (typeof p === 'string') {
          return { word: p, response: '' }
        }
        return p
      })
    }
    
    return parsedData
  } catch (error) {
    console.error('Error reading keywords:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read keywords'
    })
  }
})
