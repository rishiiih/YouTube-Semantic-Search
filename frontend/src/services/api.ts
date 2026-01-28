import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface IngestRequest {
  youtube_url: string
}

export interface IngestResponse {
  message: string
  video_id: string
  status: string
}

export interface QueryRequest {
  video_id: string
  question: string
}

export interface QueryResponse {
  answer: string
  video_id: string
  sources_used: number
  question: string
  timestamps?: string[]
}

export interface QuestionSuggestion {
  id: number
  video_id: string
  question: string
  created_at: string
}

export interface Video {
  video_id: string
  title: string
  youtube_url: string
  duration: number
  thumbnail_url?: string
  channel_name?: string
  upload_date?: string
  view_count?: number
  status: string
  progress_step?: string
  progress_percent?: number
  created_at: string
}

// Ingest a new video
export const ingestVideo = async (data: IngestRequest): Promise<IngestResponse> => {
  const response = await api.post('/ingest/', data)
  return response.data
}

// Query a video
export const queryVideo = async (data: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post('/query/', data)
  return response.data
}

// Get all videos
export const getVideos = async (): Promise<Video[]> => {
  const response = await api.get('/videos/')
  // Backend returns { videos: [...], total: number }
  return response.data.videos || []
}

// Get video by ID
export const getVideoById = async (videoId: string): Promise<Video> => {
  const response = await api.get(`/videos/${videoId}`)
  return response.data
}

// Get suggested questions for a video
export const getVideoSuggestions = async (videoId: string): Promise<QuestionSuggestion[]> => {
  const response = await api.get(`/videos/${videoId}/suggestions`)
  return response.data
}
