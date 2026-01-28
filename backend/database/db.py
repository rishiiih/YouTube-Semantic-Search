import aiosqlite
from pathlib import Path
from typing import Optional
from backend.app.config import settings


class Database:
    """SQLite database manager with async support"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.sqlite_db_path
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """Create database directory if it doesn't exist"""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database schema from schema.sql"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign key constraints
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Read and execute schema
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            await db.executescript(schema_sql)
            await db.commit()
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get a database connection"""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row  # Enable column access by name
        await conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    async def check_health(self) -> bool:
        """Check if database is accessible"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
            return True
        except Exception:
            return False


# Singleton instance
db = Database()


async def init_db():
    """Initialize database (call on startup)"""
    await db.initialize()
