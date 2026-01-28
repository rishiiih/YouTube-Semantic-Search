export interface Video {
  video_id: string
  title: string
  youtube_url: string
  duration: number
  thumbnail_url?: string
  channel_name?: string
  upload_date?: string
  view_count?: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress_step?: string
  progress_percent?: number
  created_at: string
}

export interface QueryResult {
  answer: string
  video_id: string
  question: string
  timestamps?: string[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  timestamps?: string[]
}
