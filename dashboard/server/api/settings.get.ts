import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  const settingsPath = path.resolve(process.cwd(), '../data/settings.json')
  
  if (!fs.existsSync(settingsPath)) {
    return {
      group_delays: {}
    }
  }

  try {
    const data = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'))
    return {
      group_delays: data.group_delays || {}
    }
  } catch (error) {
    console.error('Error reading settings.json:', error)
    return {
      group_delays: {}
    }
  }
})
