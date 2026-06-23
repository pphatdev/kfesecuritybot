import fs from 'node:fs'
import path from 'node:path'

export default defineEventHandler(async (event) => {
  const groupsDbPath = path.resolve(process.cwd(), '../data/groups.json')
  let groupsData: Record<string, any> = {}

  if (fs.existsSync(groupsDbPath)) {
    try {
      groupsData = JSON.parse(fs.readFileSync(groupsDbPath, 'utf-8'))
    } catch (e) {
      console.error('Error reading groups.json', e)
    }
  }

  const usersDbPath = path.resolve(process.cwd(), '../data/users.json')
  let usersData: Record<string, any> = {}

  if (fs.existsSync(usersDbPath)) {
    try {
      usersData = JSON.parse(fs.readFileSync(usersDbPath, 'utf-8'))
    } catch (e) {
      console.error('Error reading users.json', e)
    }
  }

  // Convert the object mapping into an array
  const groupsList = Object.entries(groupsData).map(([id, data]) => ({
    id,
    title: data.title || `Group ${id}`,
    type: 'Group/Channel'
  }))

  const usersList = Object.entries(usersData).map(([id, data]) => ({
    id,
    title: data.username ? `@${data.username}` : `User ${id}`,
    type: 'Private Chat'
  }))

  return { groups: [...groupsList, ...usersList] }
})
