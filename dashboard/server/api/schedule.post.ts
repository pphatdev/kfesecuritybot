import { db } from '../database'
import { scheduledMessages } from '../database/schema'
import path from 'node:path'
import fs from 'node:fs'
import crypto from 'node:crypto'

export default defineEventHandler(async (event) => {
  await verifySession(event)
  try {
    let message = ''
    let chatIds: string[] = []
    let sendAt = ''
    let fileData: any = null

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
          } else if (field.name === 'file') {
            fileData = field
          }
        }
      }
    } else {
      const body = await readBody(event)
      message = body.message
      chatIds = Array.isArray(body.chatIds) ? body.chatIds : [body.chatIds]
      sendAt = body.sendAt
    }

    if (!fileData && (!message || typeof message !== 'string')) {
      throw createError({ statusCode: 400, statusMessage: 'Message is required when no file is attached' })
    }

    if (!chatIds || chatIds.length === 0) {
      throw createError({ statusCode: 400, statusMessage: 'At least one target group must be selected' })
    }

    if (!sendAt || typeof sendAt !== 'string') {
      throw createError({ statusCode: 400, statusMessage: 'Schedule send time is required' })
    }

    const sendTime = new Date(sendAt).getTime()
    if (isNaN(sendTime)) {
      throw createError({ statusCode: 400, statusMessage: 'Invalid schedule date/time format' })
    }

    if (sendTime <= Date.now()) {
      throw createError({ statusCode: 400, statusMessage: 'Schedule time must be in the future' })
    }

    const scheduleId = crypto.randomUUID()
    let savedFilePath: string | null = null
    let fileType: string | null = null

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

    const newSchedule = {
      id: scheduleId,
      message,
      chatIds, // Will be serialized by Drizzle since mode: 'json'
      sendAt,
      status: 'pending',
      createdAt: new Date().toISOString(),
      filePath: savedFilePath,
      fileType: fileType
    }

    await db.insert(scheduledMessages).values(newSchedule)

    return { success: true, schedule: newSchedule }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal Server Error'
    })
  }
})
