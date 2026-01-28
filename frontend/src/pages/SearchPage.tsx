import { useState, useRef, useEffect } from 'react'
import { useVideos, useQueryVideo, useVideoSuggestions } from '@/hooks/useApi'
import { useChatStore } from '@/store/chatStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ChatMessageItem } from '@/components/chat/ChatMessageItem'
import { Send, Search as SearchIcon, Loader2, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'

export function SearchPage() {
  const [question, setQuestion] = useState('')
  const [selectedVideoId, setSelectedVideoId] = useState<string>('')
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: videos, isLoading: videosLoading } = useVideos()
  const queryMutation = useQueryVideo()
  const { data: suggestions, isLoading: suggestionsLoading } = useVideoSuggestions(selectedVideoId)
  const { messages, addMessage, currentVideoId, setCurrentVideoId } = useChatStore()

  const completedVideos = videos?.filter(v => v.status === 'completed') || []

  useEffect(() => {
    if (selectedVideoId && selectedVideoId !== currentVideoId) {
      setCurrentVideoId(selectedVideoId)
    }
  }, [selectedVideoId, currentVideoId, setCurrentVideoId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e?: React.FormEvent, suggestedQuestion?: string) => {
    e?.preventDefault()
    
    const questionText = suggestedQuestion || question.trim()
    if (!questionText) return
    if (!selectedVideoId) {
      toast.error('Please select a video first')
      return
    }

    const userMessage = questionText
    setQuestion('')

    addMessage({
      role: 'user',
      content: userMessage,
    })

    try {
      const response = await queryMutation.mutateAsync({
        video_id: selectedVideoId,
        question: userMessage,
      })

      // Extract timestamp strings from response
      const timestampStrings = response.timestamps?.map(t => `[${t.time}]`) || []
      
      addMessage({
        role: 'assistant',
        content: response.answer,
        timestamps: timestampStrings,
      })
    } catch (error) {
      addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
      })
    }
  }

  const handleTimestampClick = (timestamp: string) => {
    const videoUrl = completedVideos.find(v => v.video_id === selectedVideoId)?.youtube_url
    if (videoUrl) {
      // Parse [MM:SS] or [HH:MM:SS] format
      const match = timestamp.match(/\[(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\]/)
      if (match) {
        const hours = match[1] ? parseInt(match[1]) : 0
        const minutes = parseInt(match[2])
        const seconds = parseInt(match[3])
        const totalSeconds = hours * 3600 + minutes * 60 + seconds
        
        window.open(`${videoUrl}&t=${totalSeconds}`, '_blank')
      }
    }
  }

  if (videosLoading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (completedVideos.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <Card>
          <CardContent className="pt-12 pb-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
              <SearchIcon className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">No videos ready to search</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Add and process videos in the Ingest tab to start asking questions
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <SearchIcon className="h-8 w-8 text-primary" />
          Search Videos
        </h2>
        <p className="text-muted-foreground mt-2">
          Ask questions about your indexed videos and get answers with timestamps
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 flex flex-col h-[600px]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Conversation
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0 pb-6 px-6 min-h-0">
            <ScrollArea className="flex-1 pr-4" ref={scrollRef}>
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-center text-muted-foreground">
                  <div>
                    <p className="text-sm">Select a video and ask a question to start</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4 pb-4">
                  {messages.map((message) => (
                    <ChatMessageItem
                      key={message.id}
                      message={message}
                      onTimestampClick={handleTimestampClick}
                    />
                  ))}
                  {queryMutation.isPending && (
                    <div className="flex gap-3 p-4 rounded-lg bg-card border">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">AI Assistant</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          Thinking...
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            {suggestions && suggestions.length > 0 && messages.length === 0 && (
              <div className="py-4 border-t space-y-2">
                <p className="text-xs font-medium text-muted-foreground">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((suggestion) => (
                    <Badge
                      key={suggestion.id}
                      variant="secondary"
                      className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                      onClick={() => handleSubmit(undefined, suggestion.question)}
                    >
                      {suggestion.question}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex gap-2 pt-4 border-t">
              <Input
                placeholder="Ask a question about the video..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={queryMutation.isPending || !selectedVideoId}
              />
              <Button
                type="submit"
                disabled={queryMutation.isPending || !question.trim() || !selectedVideoId}
              >
                {queryMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Select Video</CardTitle>
            </CardHeader>
            <CardContent>
              <Select value={selectedVideoId} onValueChange={setSelectedVideoId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a video" />
                </SelectTrigger>
                <SelectContent>
                  {completedVideos.map((video) => (
                    <SelectItem key={video.video_id} value={video.video_id}>
                      {video.title || video.video_id}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          {selectedVideoId && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Video Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {(() => {
                  const video = completedVideos.find(v => v.video_id === selectedVideoId)
                  if (!video) return null
                  return (
                    <>
                      <div>
                        <p className="text-sm font-medium">Title</p>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {video.title || 'Untitled'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm font-medium">Video ID</p>
                        <p className="text-sm text-muted-foreground font-mono">
                          {video.video_id}
                        </p>
                      </div>
                    </>
                  )
                })()}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>• Click on timestamps to jump to that moment in the video</p>
              <p>• Ask specific questions for better answers</p>
              <p>• Try questions like "How do I fix X?" or "What is Y?"</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
