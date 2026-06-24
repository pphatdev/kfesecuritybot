import { defineConfig } from 'drizzle-kit';
import path from 'path';

export default defineConfig({
  schema: './server/database/schema.ts',
  out: './server/database/migrations',
  dialect: 'sqlite',
  dbCredentials: {
    url: path.resolve(__dirname, '../data/bot.db')
  }
});
