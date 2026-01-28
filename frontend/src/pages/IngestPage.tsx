import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useIngestVideo } from '@/hooks/useApi'
import { extractVideoId } from '@/utils/video'
import { Youtube, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

export function IngestPage() {
  const [url, setUrl] = useState('')
  const [validationError, setValidationError] = useState('')
  const ingestMutation = useIngestVideo()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setValidationError('')

    // Validate YouTube URL
    const videoId = extractVideoId(url)
    if (!videoId) {
      setValidationError('Please enter a valid YouTube URL')
      return
    }

    try {
      await ingestMutation.mutateAsync({ youtube_url: url })
      setUrl('')
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Add New Video</h2>
        <p className="text-muted-foreground">
          Submit a YouTube URL to index and enable semantic search
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Youtube className="h-5 w-5 text-primary" />
            Video Ingestion
          </CardTitle>
          <CardDescription>
            Paste a YouTube video URL. The system will download, transcribe, and index the content.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Input
                type="text"
                placeholder="https://www.youtube.com/watch?v=..."
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value)
                  setValidationError('')
                }}
                disabled={ingestMutation.isPending}
                className={validationError ? 'border-destructive' : ''}
              />
              {validationError && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {validationError}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={ingestMutation.isPending || !url}
            >
              {ingestMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Youtube className="mr-2 h-4 w-4" />
                  Ingest Video
                </>
              )}
            </Button>
          </form>

          {ingestMutation.isSuccess && (
            <div className="mt-4 p-4 rounded-lg bg-primary/10 border border-primary/20 flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="text-sm font-medium">Video ingestion started!</p>
                <p className="text-sm text-muted-foreground">
                  Processing may take a few minutes. Check the Library tab to see progress.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">How it works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3">
            <Badge className="mt-1">1</Badge>
            <div>
              <p className="font-medium">Audio Extraction</p>
              <p className="text-sm text-muted-foreground">
                Downloads the audio track from the YouTube video
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Badge className="mt-1">2</Badge>
            <div>
              <p className="font-medium">Transcription</p>
              <p className="text-sm text-muted-foreground">
                Converts speech to text using Groq Whisper AI (supports unlimited video length)
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Badge className="mt-1">3</Badge>
            <div>
              <p className="font-medium">Semantic Indexing</p>
              <p className="text-sm text-muted-foreground">
                Creates vector embeddings and stores in ChromaDB for fast semantic search
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <Badge className="mt-1">4</Badge>
            <div>
              <p className="font-medium">Ready to Search</p>
              <p className="text-sm text-muted-foreground">
                Ask questions and get answers with exact video timestamps
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
