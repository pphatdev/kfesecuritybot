import { db } from '../database'
import { stats, activityLogs, userViolations } from '../database/schema'
import { desc } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    const statsResult = await db.select().from(stats).limit(1)
    const statData = statsResult[0] || { total_messages_scanned: 0, spam_toxic_blocked: 0 }
    
    const activities = await db.select().from(activityLogs).orderBy(desc(activityLogs.id)).limit(50)
    
    const violationsResult = await db.select().from(userViolations)
    const violationsMap: Record<string, any> = {}
    violationsResult.forEach(v => {
      violationsMap[v.userId] = {
        username: v.username,
        strikes: v.strikes,
        last_violation: v.lastViolation
      }
    })

    return {
      total_messages_scanned: statData.total_messages_scanned,
      spam_toxic_blocked: statData.spam_toxic_blocked,
      recent_activity: activities,
      violations: violationsMap
    }
  } catch (error) {
    console.error('Error reading stats from DB:', error)
    return {
      total_messages_scanned: 0,
      spam_toxic_blocked: 0,
      recent_activity: [],
      violations: {}
    }
  }
})
