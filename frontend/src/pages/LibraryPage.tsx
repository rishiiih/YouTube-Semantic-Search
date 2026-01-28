import { useVideos } from '@/hooks/useApi'
import { VideoCard } from '@/components/video/VideoCard'
import { VideoCardSkeleton } from '@/components/video/VideoCardSkeleton'
import { Card, CardContent } from '@/components/ui/card'
import { AlertCircle, Library, VideoOff } from 'lucide-react'

export function LibraryPage() {
  const { data: videos, isLoading, isError, error } = useVideos()

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Video Library</h2>
          <p className="text-muted-foreground mt-2">
            All indexed videos ready for semantic search
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <VideoCardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Video Library</h2>
          <p className="text-muted-foreground mt-2">
            All indexed videos ready for semantic search
          </p>
        </div>

        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="pt-6 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-destructive">Failed to load videos</p>
              <p className="text-sm text-muted-foreground mt-1">
                {error instanceof Error ? error.message : 'An error occurred'}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Video Library</h2>
          <p className="text-muted-foreground mt-2">
            All indexed videos ready for semantic search
          </p>
        </div>

        <Card>
          <CardContent className="pt-12 pb-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
              <VideoOff className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">No videos yet</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Head to the Ingest tab to add your first YouTube video
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const completedCount = videos.filter(v => v.status === 'completed').length
  const processingCount = videos.filter(v => v.status === 'processing').length

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Library className="h-8 w-8 text-primary" />
            Video Library
          </h2>
          <p className="text-muted-foreground mt-2">
            {videos.length} video{videos.length !== 1 ? 's' : ''} indexed
            {completedCount > 0 && ` • ${completedCount} ready to search`}
            {processingCount > 0 && ` • ${processingCount} processing`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => (
          <VideoCard key={video.video_id} video={video} />
        ))}
      </div>
    </div>
  )
}
