import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  username: text('username')
});

export const groups = sqliteTable('groups', {
  id: text('id').primaryKey(),
  title: text('title')
});

export const keywords = sqliteTable('keywords', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  word: text('word').notNull(),
  category: text('category').notNull(), // 'spam', 'toxic', 'sticker', 'pattern'
  response: text('response') // Only used for 'pattern' currently
});

export const stats = sqliteTable('stats', {
  id: integer('id').primaryKey(), // We'll just use id=1 for the singleton
  total_messages_scanned: integer('total_messages_scanned').default(0).notNull(),
  spam_toxic_blocked: integer('spam_toxic_blocked').default(0).notNull()
});

export const activityLogs = sqliteTable('activity_logs', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  time: text('time').notNull(),
  type: text('type').notNull(),
  text: text('text').notNull(),
  username: text('username').notNull()
});

export const userViolations = sqliteTable('user_violations', {
  userId: text('user_id').primaryKey(),
  username: text('username').notNull(),
  strikes: integer('strikes').default(0).notNull(),
  lastViolation: text('last_violation')
});

export const scheduledMessages = sqliteTable('scheduled_messages', {
  id: text('id').primaryKey(),
  message: text('message').notNull(),
  chatIds: text('chat_ids', { mode: 'json' }).notNull(), // Array of chat IDs stored as JSON string
  sendAt: text('send_at').notNull(),
  status: text('status').notNull(), // 'pending', 'sent', 'failed'
  createdAt: text('created_at').notNull(),
  filePath: text('file_path'),
  fileType: text('file_type') // 'photo', 'video', 'document'
});

export const otps = sqliteTable('otps', {
  userId: text('user_id').primaryKey(),
  username: text('username'),
  otp: text('otp').notNull(),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull()
});

export const sessions = sqliteTable('sessions', {
  token: text('token').primaryKey(),
  userId: text('user_id'),
  username: text('username'),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull()
});

export const allowedUsers = sqliteTable('allowed_users', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  type: text('type').notNull(), // 'id' or 'username'
  value: text('value').notNull()
});

export const settings = sqliteTable('settings', {
  key: text('key').primaryKey(),
  value: text('value', { mode: 'json' }).notNull()
});

export const privateChats = sqliteTable('private_chats', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  username: text('username'),
  message: text('message').notNull(),
  timestamp: text('timestamp').notNull()
});
