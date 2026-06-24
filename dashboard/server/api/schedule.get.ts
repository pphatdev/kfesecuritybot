import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler((event) => {
  verifySession(event)
  try {
    const filePath = path.resolve(process.cwd(), '../data/scheduled_messages.json')
    
    if (!fs.existsSync(filePath)) {
      return { schedules: [] }
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    const parsedData = JSON.parse(fileData)
    
    return { schedules: parsedData }
  } catch (error) {
    console.error('Error reading schedules:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read schedules'
    })
  }
})
