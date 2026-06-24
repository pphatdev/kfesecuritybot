import { db } from '../database'
import { scheduledMessages } from '../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const body = await readBody(event)
    const { id } = body

    if (!id) {
      throw createError({ statusCode: 400, statusMessage: 'Schedule ID is required' })
    }

    const result = await db.delete(scheduledMessages).where(eq(scheduledMessages.id, id))
    
    if (result.changes > 0) {
      return { success: true }
    } else {
      throw createError({ statusCode: 404, statusMessage: 'Scheduled message not found' })
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error'
    })
  }
})
