import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  if (typeof body.group_delays !== 'object') {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid group_delays payload'
    })
  }

  const settingsPath = path.resolve(process.cwd(), '../data/settings.json')
  let currentSettings: any = { group_delays: {} }

  if (fs.existsSync(settingsPath)) {
    try {
      currentSettings = JSON.parse(fs.readFileSync(settingsPath, 'utf-8'))
      if (!currentSettings.group_delays) currentSettings.group_delays = {}
    } catch (e) {
      console.error('Error reading settings.json', e)
    }
  }

  // Parse and validate the new delays
  for (const [chatId, delay] of Object.entries(body.group_delays)) {
    currentSettings.group_delays[chatId] = Math.max(0, parseInt(delay as string) || 0)
  }

  try {
    fs.mkdirSync(path.dirname(settingsPath), { recursive: true })
    fs.writeFileSync(settingsPath, JSON.stringify(currentSettings, null, 2), 'utf-8')
    return { success: true, settings: currentSettings }
  } catch (error) {
    console.error('Error saving settings.json:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to save settings'
    })
  }
})
