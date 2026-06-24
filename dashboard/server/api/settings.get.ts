import { db } from '../database'
import { settings } from '../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  try {
    const groupDelaysSetting = await db.select().from(settings).where(eq(settings.key, 'group_delays'))
    
    let groupDelays = {}
    if (groupDelaysSetting.length > 0) {
      groupDelays = groupDelaysSetting[0].value as Record<string, number>
    }
    
    return { group_delays: groupDelays }
  } catch (error) {
    console.error('Error reading settings from DB:', error)
    return { group_delays: {} }
  }
})
