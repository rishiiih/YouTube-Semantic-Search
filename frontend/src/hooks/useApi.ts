import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getVideos, getVideoById, ingestVideo, queryVideo, getVideoSuggestions } from '@/services/api'
import type { IngestRequest, QueryRequest } from '@/services/api'
import toast from 'react-hot-toast'
import { useEffect } from 'react'

export const useVideos = () => {
  const queryClient = useQueryClient()
  
  const query = useQuery({
    queryKey: ['videos'],
    queryFn: getVideos,
  })

  // Auto-refresh every 2 seconds if there are processing videos
  useEffect(() => {
    const hasProcessingVideos = query.data?.some(v => v.status === 'processing')
    
    if (hasProcessingVideos) {
      const interval = setInterval(() => {
        queryClient.invalidateQueries({ queryKey: ['videos'] })
      }, 2000)
      
      return () => clearInterval(interval)
    }
  }, [query.data, queryClient])

  return query
}

export const useVideo = (videoId: string) => {
  return useQuery({
    queryKey: ['video', videoId],
    queryFn: () => getVideoById(videoId),
    enabled: !!videoId,
  })
}

export const useIngestVideo = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: IngestRequest) => ingestVideo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
      toast.success('Video ingestion started!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to ingest video')
    },
  })
}

export const useQueryVideo = () => {
  return useMutation({
    mutationFn: (data: QueryRequest) => queryVideo(data),
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to query video')
    },
  })
}

export const useVideoSuggestions = (videoId: string) => {
  return useQuery({
    queryKey: ['suggestions', videoId],
    queryFn: () => getVideoSuggestions(videoId),
    enabled: !!videoId,
  })
}
