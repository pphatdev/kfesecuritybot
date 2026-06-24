import { db } from '../database'
import { allowedUsers } from '../database/schema'
import { eq, and } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const target = body?.target
  let type = body?.type // 'username' or 'user_id'

  if (!target || !type) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing target or type'
    })
  }

  if (type === 'user_id') type = 'id' // map to db schema enum type

  try {
    const result = await db.delete(allowedUsers).where(
      and(
        eq(allowedUsers.type, type),
        eq(allowedUsers.value, target)
      )
    )

    if (result.changes > 0) {
      return { success: true }
    } else {
      throw createError({
        statusCode: 404,
        statusMessage: 'Admin not found in custom list'
      })
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('Error removing admin:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to remove admin'
    })
  }
})
