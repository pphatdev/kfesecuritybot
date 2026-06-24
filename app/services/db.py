import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/bot.db')

class DBWrapper:
    async def __aenter__(self):
        self.db = await aiosqlite.connect(DB_PATH)
        self.db.row_factory = aiosqlite.Row
        return self.db
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db.close()

async def get_db():
    return DBWrapper()
