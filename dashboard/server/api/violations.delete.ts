import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    const query = getQuery(event)
    const userId = query.userId
    
    if (!userId) {
      throw createError({ statusCode: 400, statusMessage: 'userId is required' })
    }

    const filePath = path.resolve(process.cwd(), '../data/dashboard_stats.json')
    if (!fs.existsSync(filePath)) {
      throw createError({ statusCode: 404, statusMessage: 'Stats file not found' })
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    const data = JSON.parse(fileData)
    
    if (data.violations && data.violations[String(userId)]) {
      const username = data.violations[String(userId)].username
      
      // Remove the violation
      delete data.violations[String(userId)]
      
      // Log the action
      const now_str = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      const activity = {
        time: now_str,
        type: "action",
        text: `Admin reset strikes for <b>@${username}</b>`,
        username: "System"
      }
      
      if (!data.recent_activity) data.recent_activity = []
      data.recent_activity.unshift(activity)
      data.recent_activity = data.recent_activity.slice(0, 50)
      
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
      return { success: true, message: `Reset strikes for user ${userId}` }
    } else {
      throw createError({ statusCode: 404, statusMessage: 'User not found' })
    }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Failed to reset violation'
    })
  }
})
