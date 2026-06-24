import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const { id } = body

    if (!id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Schedule ID is required'
      })
    }

    const filePath = path.resolve(process.cwd(), '../data/scheduled_messages.json')
    if (!fs.existsSync(filePath)) {
      throw createError({
        statusCode: 404,
        statusMessage: 'No scheduled messages found'
      })
    }

    const fileData = fs.readFileSync(filePath, 'utf-8')
    let schedules: any[] = JSON.parse(fileData)

    const index = schedules.findIndex(s => s.id === id)
    if (index === -1) {
      throw createError({
        statusCode: 404,
        statusMessage: 'Scheduled message not found'
      })
    }

    schedules.splice(index, 1)

    fs.writeFileSync(filePath, JSON.stringify(schedules, null, 2), 'utf-8')

    return { success: true }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
