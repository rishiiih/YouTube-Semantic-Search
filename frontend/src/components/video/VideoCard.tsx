import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDuration } from '@/utils/video'
import { Clock, Calendar, ExternalLink, Eye, User } from 'lucide-react'
import type { Video } from '@/types'

interface VideoCardProps {
  video: Video
}

const statusConfig = {
  pending: { label: 'Pending', variant: 'secondary' as const },
  processing: { label: 'Processing', variant: 'default' as const },
  completed: { label: 'Completed', variant: 'default' as const },
  failed: { label: 'Failed', variant: 'destructive' as const },
}

export function VideoCard({ video }: VideoCardProps) {
  const status = statusConfig[video.status] || statusConfig.pending
  const isCompleted = video.status === 'completed'
  const isProcessing = video.status === 'processing'

  return (
    <Card className="hover:shadow-md transition-shadow overflow-hidden">
      {video.thumbnail_url && (
        <div className="relative w-full h-40 bg-muted overflow-hidden">
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full h-full object-cover"
          />
          {isProcessing && video.progress_percent !== undefined && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-muted">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${video.progress_percent}%` }}
              />
            </div>
          )}
        </div>
      )}
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg line-clamp-2">
            {video.title || 'Untitled Video'}
          </CardTitle>
          <Badge variant={status.variant} className="flex-shrink-0">
            {status.label}
          </Badge>
        </div>
        {video.channel_name && (
          <CardDescription className="flex items-center gap-1.5">
            <User className="h-3 w-3" />
            {video.channel_name}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
          <div className="flex items-center gap-1.5">
            <Clock className="h-4 w-4" />
            <span>{formatDuration(video.duration)}</span>
          </div>
          {video.view_count !== undefined && (
            <div className="flex items-center gap-1.5">
              <Eye className="h-4 w-4" />
              <span>{(video.view_count / 1000).toFixed(0)}K views</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4" />
            <span>{new Date(video.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        {isCompleted && (
          <a
            href={video.youtube_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
          >
            <ExternalLink className="h-4 w-4" />
            Watch on YouTube
          </a>
        )}

        {isProcessing && (
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{video.progress_step || 'Processing...'}</span>
              <span>{video.progress_percent?.toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-500"
                style={{ width: `${video.progress_percent || 0}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
