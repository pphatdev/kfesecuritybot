import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const body = await readBody(event)
    const { chatIds, message, sendAt } = body

    if (!message || typeof message !== 'string') {
      throw createError({
        statusCode: 400,
        statusMessage: 'Message is required'
      })
    }

    if (!chatIds || !Array.isArray(chatIds) || chatIds.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'At least one target group must be selected'
      })
    }

    if (!sendAt || typeof sendAt !== 'string') {
      throw createError({
        statusCode: 400,
        statusMessage: 'Schedule send time is required'
      })
    }

    // Verify sendAt is a valid date and in the future
    const sendTime = new Date(sendAt).getTime()
    if (isNaN(sendTime)) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Invalid schedule date/time format'
      })
    }

    if (sendTime <= Date.now()) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Schedule time must be in the future'
      })
    }

    const filePath = path.resolve(process.cwd(), '../data/scheduled_messages.json')
    let schedules: any[] = []

    if (fs.existsSync(filePath)) {
      try {
        schedules = JSON.parse(fs.readFileSync(filePath, 'utf-8'))
      } catch (e) {
        console.error('Error reading scheduled_messages.json', e)
      }
    }

    const newSchedule = {
      id: crypto.randomUUID(),
      message,
      chatIds,
      sendAt,
      status: 'pending',
      createdAt: new Date().toISOString()
    }

    schedules.push(newSchedule)

    fs.mkdirSync(path.dirname(filePath), { recursive: true })
    fs.writeFileSync(filePath, JSON.stringify(schedules, null, 2), 'utf-8')

    return { success: true, schedule: newSchedule }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
