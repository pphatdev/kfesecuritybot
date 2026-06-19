import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler((event) => {
  try {
    const filePath = path.resolve(process.cwd(), '../data/dashboard_stats.json')
    
    if (!fs.existsSync(filePath)) {
      return {
        total_messages_scanned: 0,
        spam_toxic_blocked: 0,
        recent_activity: [],
        violations: {}
      }
    }
    
    const fileData = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(fileData)
  } catch (error) {
    console.error('Error reading stats:', error)
    return {
      total_messages_scanned: 0,
      spam_toxic_blocked: 0,
      recent_activity: [],
      violations: {}
    }
  }
})
