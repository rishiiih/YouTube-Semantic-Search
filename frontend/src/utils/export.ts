import type { ChatMessage } from '@/types'

interface ExportOptions {
  format: 'markdown' | 'text'
  videoTitle: string
  videoUrl: string
}

function parseTimestamp(timestamp: string): number | null {
  // Parse [MM:SS] or [HH:MM:SS] format
  const match = timestamp.match(/\[(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\]/)
  if (match) {
    const hours = match[1] ? parseInt(match[1]) : 0
    const minutes = parseInt(match[2])
    const seconds = parseInt(match[3])
    return hours * 3600 + minutes * 60 + seconds
  }
  return null
}

export function exportConversation(
  messages: ChatMessage[],
  options: ExportOptions
): string {
  const { format, videoTitle, videoUrl } = options

  if (format === 'markdown') {
    let markdown = `# ${videoTitle}\n\n`
    markdown += `**Video URL:** ${videoUrl}\n\n`
    markdown += `**Exported:** ${new Date().toLocaleString()}\n\n`
    markdown += `---\n\n`

    for (const message of messages) {
      if (message.role === 'user') {
        markdown += `## Q: ${message.content}\n\n`
      } else {
        markdown += `### A:\n\n${message.content}\n\n`

        if (message.timestamps && message.timestamps.length > 0) {
          markdown += `**Timestamps:**\n\n`
          for (const ts of message.timestamps) {
            const seconds = parseTimestamp(ts)
            if (seconds !== null) {
              const youtubeUrl = `${videoUrl}&t=${Math.floor(seconds)}s`
              markdown += `- [${ts}](${youtubeUrl})\n`
            }
          }
          markdown += `\n`
        }
      }
    }

    return markdown
  }

  // Text format
  let text = `${videoTitle}\n`
  text += `Video URL: ${videoUrl}\n`
  text += `Exported: ${new Date().toLocaleString()}\n\n`
  text += `${'='.repeat(60)}\n\n`

  for (const message of messages) {
    if (message.role === 'user') {
      text += `Q: ${message.content}\n\n`
    } else {
      text += `A: ${message.content}\n\n`

      if (message.timestamps && message.timestamps.length > 0) {
        text += `Timestamps:\n`
        for (const ts of message.timestamps) {
          const seconds = parseTimestamp(ts)
          if (seconds !== null) {
            const youtubeUrl = `${videoUrl}&t=${Math.floor(seconds)}s`
            text += `  ${ts}\n  ${youtubeUrl}\n`
          }
        }
        text += `\n`
      }
    }
  }

  return text
}

export function downloadFile(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
