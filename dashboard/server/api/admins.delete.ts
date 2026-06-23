import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const target = body?.target
  const type = body?.type // 'username' or 'user_id'

  if (!target || !type) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing target or type'
    })
  }

  const allowedUsersPath = path.resolve(process.cwd(), '../data/allowed_users.json')
  
  if (!fs.existsSync(allowedUsersPath)) {
    throw createError({
      statusCode: 404,
      statusMessage: 'No custom admins found'
    })
  }

  try {
    const data = JSON.parse(fs.readFileSync(allowedUsersPath, 'utf-8'))
    let modified = false

    if (type === 'username' && data.usernames) {
      const idx = data.usernames.indexOf(target)
      if (idx !== -1) {
        data.usernames.splice(idx, 1)
        modified = true
      }
    } else if (type === 'user_id' && data.user_ids) {
      const idx = data.user_ids.indexOf(target)
      if (idx !== -1) {
        data.user_ids.splice(idx, 1)
        modified = true
      }
    }

    if (modified) {
      fs.writeFileSync(allowedUsersPath, JSON.stringify(data, null, 2), 'utf-8')
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
