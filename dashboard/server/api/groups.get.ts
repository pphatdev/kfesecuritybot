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

  const historyDbPath = path.resolve(process.cwd(), '../data/chat_history.json')
  let historyData: Record<string, any> = {}
  if (fs.existsSync(historyDbPath)) {
    try {
      historyData = JSON.parse(fs.readFileSync(historyDbPath, 'utf-8'))
    } catch (e) {
      console.error('Error reading chat_history.json', e)
    }
  }

  // Convert the object mapping into an array
  const groupsList = Object.entries(groupsData).map(([id, data]) => {
    const history = historyData[id] || []
    const lastMsg = history.length > 0 ? history[history.length - 1] : null
    return {
      id,
      title: data.title || `Group ${id}`,
      type: 'Group/Channel',
      has_mention_or_reply: data.has_mention_or_reply || false,
      last_mention_or_reply_at: data.last_mention_or_reply_at || null,
      last_message: lastMsg ? {
        text: lastMsg.text,
        time: lastMsg.time,
        sender: lastMsg.sender
      } : null
    }
  })

  const usersList = Object.entries(usersData).map(([id, data]) => {
    const history = historyData[id] || []
    const lastMsg = history.length > 0 ? history[history.length - 1] : null
    return {
      id,
      title: data.username ? `@${data.username}` : `User ${id}`,
      type: 'Private Chat',
      has_mention_or_reply: data.has_mention_or_reply || false,
      last_mention_or_reply_at: data.last_mention_or_reply_at || null,
      last_message: lastMsg ? {
        text: lastMsg.text,
        time: lastMsg.time,
        sender: lastMsg.sender
      } : null
    }
  })

  return { groups: [...groupsList, ...usersList] }
})
