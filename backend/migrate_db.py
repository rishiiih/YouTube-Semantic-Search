"""
Run database migrations
"""
import sqlite3
import sys
from pathlib import Path

def run_migration():
    """Apply database migration for new fields"""
    db_path = Path("data/videos.db")
    
    if not db_path.exists():
        print("Database not found. Run the app first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(videos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        migrations = []
        
        if 'thumbnail_url' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN thumbnail_url TEXT")
        if 'channel_name' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN channel_name TEXT")
        if 'upload_date' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN upload_date TEXT")
        if 'view_count' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN view_count INTEGER")
        if 'progress_step' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN progress_step TEXT")
        if 'progress_percent' not in columns:
            migrations.append("ALTER TABLE videos ADD COLUMN progress_percent REAL DEFAULT 0")
        
        for migration in migrations:
            print(f"Executing: {migration}")
            cursor.execute(migration)
        
        # Create question_suggestions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                question TEXT NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_suggestions_video 
            ON question_suggestions(video_id)
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
