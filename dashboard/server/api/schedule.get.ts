import { db } from '../database'
import { scheduledMessages } from '../database/schema'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const schedules = await db.select().from(scheduledMessages)
    return { schedules }
  } catch (error) {
    console.error('Error reading schedules from DB:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to read schedules'
    })
  }
})
