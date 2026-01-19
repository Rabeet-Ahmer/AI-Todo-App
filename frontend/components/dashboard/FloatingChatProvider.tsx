'use client'

import { FloatingChat } from '@/components/chat/FloatingChat'

interface FloatingChatProviderProps {
  children: React.ReactNode
}

export function FloatingChatProvider({ children }: FloatingChatProviderProps) {
  return (
    <>
      {children}
      <FloatingChat />
    </>
  )
}