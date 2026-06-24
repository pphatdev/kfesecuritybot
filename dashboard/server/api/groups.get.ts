import { db } from '../database'
import { groups, users } from '../database/schema'

export default defineEventHandler(async (event) => {
  const groupsData = await db.select().from(groups)
  const usersData = await db.select().from(users)

  const groupsList = groupsData.map((data) => ({
    id: data.id,
    title: data.title || `Group ${data.id}`,
    type: 'Group/Channel'
  }))

  const usersList = usersData.map((data) => ({
    id: data.id,
    title: data.username ? `@${data.username}` : `User ${data.id}`,
    type: 'Private Chat'
  }))

  return { groups: [...groupsList, ...usersList] }
})
