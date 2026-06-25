import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

export default defineEventHandler(async (event) => {
  verifySession(event)
  try {
    let message = ''
    let chatIds: string[] = []
    let sendAt = ''
    let cron = ''
    let fileData: any = null
    let buttons: Array<{ text: string, url: string }> = []
    let buttonText = ''
    let buttonUrl = ''

    const contentType = getRequestHeader(event, 'content-type') || ''
    
    if (contentType.includes('multipart/form-data')) {
      const multipart = await readMultipartFormData(event)
      if (multipart) {
        for (const field of multipart) {
          if (field.name === 'message') {
            message = field.data.toString('utf-8')
          } else if (field.name === 'chatIds') {
            chatIds.push(field.data.toString('utf-8'))
          } else if (field.name === 'sendAt') {
            sendAt = field.data.toString('utf-8')
          } else if (field.name === 'cron') {
            cron = field.data.toString('utf-8')
          } else if (field.name === 'file') {
            fileData = field
          } else if (field.name === 'buttons') {
            try {
              buttons = JSON.parse(field.data.toString('utf-8'))
            } catch (e) {
              console.error('Failed to parse buttons JSON:', e)
            }
          } else if (field.name === 'buttonText') {
            buttonText = field.data.toString('utf-8')
          } else if (field.name === 'buttonUrl') {
            buttonUrl = field.data.toString('utf-8')
          }
        }
      }
    } else {
      const body = await readBody(event)
      message = body.message
      chatIds = Array.isArray(body.chatIds) ? body.chatIds : [body.chatIds]
      sendAt = body.sendAt
      cron = body.cron
      if (body.buttons) {
        buttons = Array.isArray(body.buttons) ? body.buttons : []
      }
      buttonText = body.buttonText || ''
      buttonUrl = body.buttonUrl || ''
    }

    if (!fileData && (!message || typeof message !== 'string')) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Message is required when no file is attached'
      })
    }

    if (!chatIds || chatIds.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'At least one target group must be selected'
      })
    }

    if (cron) {
      const cronRegex = /^(\S+\s+){4}\S+$/
      if (!cronRegex.test(cron.trim())) {
        throw createError({
          statusCode: 400,
          statusMessage: 'Invalid cron expression format (must have exactly 5 fields)'
        })
      }
      sendAt = ''
    } else {
      if (!sendAt || typeof sendAt !== 'string') {
        throw createError({
          statusCode: 400,
          statusMessage: 'Schedule send time or cron expression is required'
        })
      }

      // Verify sendAt is a valid date and in the future
      const sendTime = new Date(sendAt).getTime()
      if (isNaN(sendTime)) {
        throw createError({
          statusCode: 400,
          statusMessage: 'Invalid schedule date/time format'
        })
      }

      if (sendTime <= Date.now()) {
        throw createError({
          statusCode: 400,
          statusMessage: 'Schedule time must be in the future'
        })
      }
    }

    const filePath = path.resolve(process.cwd(), '../data/scheduled_messages.json')
    let schedules: any[] = []

    if (fs.existsSync(filePath)) {
      try {
        schedules = JSON.parse(fs.readFileSync(filePath, 'utf-8'))
      } catch (e) {
        console.error('Error reading scheduled_messages.json', e)
      }
    }

    const scheduleId = crypto.randomUUID()
    let savedFilePath = null
    let fileType = null

    if (fileData) {
      const uploadsDir = path.resolve(process.cwd(), '../data/uploads')
      fs.mkdirSync(uploadsDir, { recursive: true })
      
      const ext = fileData.filename ? path.extname(fileData.filename) : ''
      const safeFilename = `${scheduleId}${ext}`
      const fullPath = path.join(uploadsDir, safeFilename)
      
      fs.writeFileSync(fullPath, fileData.data)
      savedFilePath = fullPath

      const mime = fileData.type || ''
      if (mime.startsWith('image/')) {
        fileType = 'photo'
      } else if (mime.startsWith('video/')) {
        fileType = 'video'
      } else {
        fileType = 'document'
      }
    }

    const newSchedule: any = {
      id: scheduleId,
      message,
      chatIds,
      sendAt,
      cron: cron ? cron.trim() : null,
      status: 'pending',
      createdAt: new Date().toISOString()
    }

    if (buttons && buttons.length > 0) {
      newSchedule.buttons = buttons.filter(btn => btn.text && btn.text.trim() && btn.url && btn.url.trim())
    }

    if (buttonText.trim() && buttonUrl.trim()) {
      newSchedule.button_text = buttonText.trim()
      newSchedule.button_url = buttonUrl.trim()
    }

    if (savedFilePath && fileType) {
      newSchedule.file_path = savedFilePath
      newSchedule.file_type = fileType
    }

    schedules.push(newSchedule)

    fs.mkdirSync(path.dirname(filePath), { recursive: true })
    fs.writeFileSync(filePath, JSON.stringify(schedules, null, 2), 'utf-8')

    return { success: true, schedule: newSchedule }
  } catch (error: any) {
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || 'Internal Server Error'
    })
  }
})
