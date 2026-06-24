import fs from 'node:fs'
import path from 'node:path'
import { db } from '../database'
import { allowedUsers } from '../database/schema'
import { eq } from 'drizzle-orm'

export default defineEventHandler(async (event) => {
  // Read from db
  const dbUsers = await db.select().from(allowedUsers)
  
  // Also read from .env for super admins
  const envPath = path.resolve(process.cwd(), '../.env')
  let envAdmins: string[] = []
  
  if (fs.existsSync(envPath)) {
    try {
      const envContent = fs.readFileSync(envPath, 'utf-8')
      const match = envContent.match(/^DASHBOARD_ADMINS=(.*)$/m)
      if (match && match[1]) {
        envAdmins = match[1].split(',').map(u => u.trim().replace('@', '')).filter(Boolean)
      }
    } catch (e) {
      console.error('Error reading .env', e)
    }
  }

  // Format response into a unified list
  const adminsList = []

  // Add env super admins
  for (const username of envAdmins) {
    adminsList.push({
      id: `env_${username}`,
      target: username,
      type: 'username',
      source: 'env',
      label: `@${username}`
    })
  }

  // Add db allowed users
  for (const user of dbUsers) {
    if (user.type === 'username') {
      if (!envAdmins.includes(user.value)) {
        adminsList.push({
          id: `json_user_${user.value}`,
          target: user.value,
          type: 'username',
          source: 'json',
          label: `@${user.value}`
        })
      }
    } else if (user.type === 'id') {
      adminsList.push({
        id: `json_id_${user.value}`,
        target: user.value,
        type: 'user_id', // Note: frontend uses 'user_id' but db schema has 'id'
        source: 'json',
        label: `ID: ${user.value}`
      })
    }
  }

  return { admins: adminsList }
})
