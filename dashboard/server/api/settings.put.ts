import { db } from '../database'
import { settings } from '../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  if (typeof body.group_delays !== 'object') {
    throw createError({ statusCode: 400, statusMessage: 'Invalid group_delays payload' })
  }

  try {
    const currentSetting = await db.select().from(settings).where(eq(settings.key, 'group_delays'))
    let group_delays: Record<string, number> = currentSetting.length > 0 ? currentSetting[0].value as Record<string, number> : {}

    for (const [chatId, delay] of Object.entries(body.group_delays)) {
      group_delays[chatId] = Math.max(0, parseInt(delay as string) || 0)
    }

    if (currentSetting.length > 0) {
      await db.update(settings).set({ value: group_delays }).where(eq(settings.key, 'group_delays'))
    } else {
      await db.insert(settings).values({ key: 'group_delays', value: group_delays })
    }

    return { success: true, settings: { group_delays } }
  } catch (error) {
    console.error('Error saving settings to DB:', error)
    throw createError({ statusCode: 500, statusMessage: 'Failed to save settings' })
  }
})
