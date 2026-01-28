import { create } from 'zustand'
import type { ChatMessage } from '@/types'

interface ChatStore {
  messages: ChatMessage[]
  currentVideoId: string | null
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  clearMessages: () => void
  setCurrentVideoId: (videoId: string | null) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  currentVideoId: null,
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: Math.random().toString(36).substr(2, 9),
          timestamp: new Date(),
        },
      ],
    })),
  clearMessages: () => set({ messages: [] }),
  setCurrentVideoId: (videoId) => set({ currentVideoId: videoId }),
}))
