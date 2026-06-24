import { db } from '../database'
import { userViolations, activityLogs } from '../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const query = getQuery(event)
    const userId = query.userId as string
    
    if (!userId) {
      throw createError({ statusCode: 400, statusMessage: 'userId is required' })
    }

    const user = await db.select().from(userViolations).where(eq(userViolations.userId, userId))
    
    if (user.length > 0) {
      const username = user[0].username
      await db.delete(userViolations).where(eq(userViolations.userId, userId))
      
      const now_str = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      await db.insert(activityLogs).values({
        time: now_str,
        type: 'action',
        text: `Admin reset strikes for <b>@${username}</b>`,
        username: 'System'
      })
      
      return { success: true, message: `Reset strikes for user ${userId}` }
    } else {
      throw createError({ statusCode: 404, statusMessage: 'User not found' })
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to reset violation'
    })
  }
})
