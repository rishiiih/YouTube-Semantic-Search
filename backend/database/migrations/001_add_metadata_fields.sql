-- Add new columns to videos table for enhanced metadata
ALTER TABLE videos ADD COLUMN thumbnail_url TEXT;
ALTER TABLE videos ADD COLUMN channel_name TEXT;
ALTER TABLE videos ADD COLUMN upload_date TEXT;
ALTER TABLE videos ADD COLUMN view_count INTEGER;
ALTER TABLE videos ADD COLUMN progress_step TEXT;
ALTER TABLE videos ADD COLUMN progress_percent REAL DEFAULT 0;

-- Create question suggestions table
CREATE TABLE IF NOT EXISTS question_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    question TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_suggestions_video ON question_suggestions(video_id);
