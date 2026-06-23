import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler((event) => {
  // Read from data/allowed_users.json
  const allowedUsersPath = path.resolve(process.cwd(), '../data/allowed_users.json')
  
  let allowedUsers = { usernames: [], user_ids: [] }
  
  if (fs.existsSync(allowedUsersPath)) {
    try {
      allowedUsers = JSON.parse(fs.readFileSync(allowedUsersPath, 'utf-8'))
    } catch (e) {
      console.error('Error reading allowed_users.json', e)
    }
  }

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

  // Add json allowed users (usernames)
  for (const username of (allowedUsers.usernames || [])) {
    // Avoid duplicates if also in env
    if (!envAdmins.includes(username)) {
      adminsList.push({
        id: `json_user_${username}`,
        target: username,
        type: 'username',
        source: 'json',
        label: `@${username}`
      })
    }
  }

  // Add json allowed users (user_ids)
  for (const userId of (allowedUsers.user_ids || [])) {
    adminsList.push({
      id: `json_id_${userId}`,
      target: userId,
      type: 'user_id',
      source: 'json',
      label: `ID: ${userId}`
    })
  }

  return { admins: adminsList }
})
