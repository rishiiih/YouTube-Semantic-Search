import { cn } from '@/lib/utils'
import { Bot, User } from 'lucide-react'
import type { ChatMessage } from '@/types'

interface ChatMessageItemProps {
  message: ChatMessage
  onTimestampClick?: (timestamp: string) => void
}

export function ChatMessageItem({ message, onTimestampClick }: ChatMessageItemProps) {
  const isUser = message.role === 'user'

  const renderContentWithTimestamps = () => {
    // Match all timestamp patterns in content: [MM:SS] or [HH:MM:SS]
    const timestampPattern = /\[(?:\d{1,2}:)?\d{1,2}:\d{2}\]/g
    const matches = Array.from(message.content.matchAll(timestampPattern))
    
    if (matches.length === 0) {
      return <p className="whitespace-pre-wrap">{message.content}</p>
    }

    const parts: React.ReactNode[] = []
    let lastIndex = 0

    matches.forEach((match, idx) => {
      const timestamp = match[0]
      const timestampIndex = match.index!
      
      // Add text before timestamp
      if (timestampIndex > lastIndex) {
        parts.push(
          <span key={`text-${idx}`}>
            {message.content.substring(lastIndex, timestampIndex)}
          </span>
        )
      }

      // Add clickable timestamp
      parts.push(
        <button
          key={`timestamp-${idx}`}
          onClick={() => onTimestampClick?.(timestamp)}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors font-mono text-sm"
        >
          {timestamp}
        </button>
      )

      lastIndex = timestampIndex + timestamp.length
    })

    // Add remaining text
    if (lastIndex < message.content.length) {
      parts.push(
        <span key="text-final">{message.content.substring(lastIndex)}</span>
      )
    }

    return <div className="whitespace-pre-wrap">{parts}</div>
  }

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg',
        isUser ? 'bg-muted' : 'bg-card border'
      )}
    >
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-secondary'
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div className="flex-1 space-y-2 overflow-hidden">
        <div className="text-sm font-medium">
          {isUser ? 'You' : 'AI Assistant'}
        </div>
        <div className="text-sm text-foreground">{renderContentWithTimestamps()}</div>
        <div className="text-xs text-muted-foreground">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
