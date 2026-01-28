export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

export const formatTimestamp = (timestamp: string): string => {
  // Convert [MM:SS] or [HH:MM:SS] format to seconds
  const match = timestamp.match(/\[(\d+):(\d+)(?::(\d+))?\]/)
  if (!match) return timestamp

  const hours = match[3] ? parseInt(match[1]) : 0
  const minutes = match[3] ? parseInt(match[2]) : parseInt(match[1])
  const seconds = match[3] ? parseInt(match[3]) : parseInt(match[2])

  const totalSeconds = hours * 3600 + minutes * 60 + seconds
  return formatDuration(totalSeconds)
}

export const extractVideoId = (url: string): string | null => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  ]

  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }

  return null
}

export const getYouTubeEmbedUrl = (videoId: string, startTime?: number): string => {
  let url = `https://www.youtube.com/embed/${videoId}`
  if (startTime !== undefined) {
    url += `?start=${startTime}`
  }
  return url
}
