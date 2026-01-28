-- Videos table: tracks ingested YouTube videos
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    youtube_url TEXT NOT NULL UNIQUE,
    title TEXT,
    duration REAL,  -- Duration in seconds
    thumbnail_url TEXT,  -- YouTube thumbnail URL
    channel_name TEXT,  -- Channel/uploader name
    upload_date TEXT,  -- Original upload date
    view_count INTEGER,  -- View count at ingestion time
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    progress_step TEXT,  -- Current step: downloading, splitting, transcribing, embedding
    progress_percent REAL DEFAULT 0,  -- Progress percentage 0-100
    error_message TEXT,  -- Error details if status is 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transcripts table: stores full Whisper transcription with timestamps
CREATE TABLE IF NOT EXISTS transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT NOT NULL,
    segment_index INTEGER NOT NULL,  -- Order in original transcript
    text TEXT NOT NULL,
    start_time REAL NOT NULL,  -- Start timestamp in seconds
    end_time REAL NOT NULL,  -- End timestamp in seconds
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Chunks table: stores chunked text segments with ChromaDB references
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id TEXT NOT NULL UNIQUE,  -- UUID for ChromaDB reference
    video_id TEXT NOT NULL,
    text TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    chunk_index INTEGER NOT NULL,  -- Order within video
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_video_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_transcripts_video ON transcripts(video_id);
CREATE INDEX IF NOT EXISTS idx_chunks_video ON chunks(video_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_id ON chunks(chunk_id);
