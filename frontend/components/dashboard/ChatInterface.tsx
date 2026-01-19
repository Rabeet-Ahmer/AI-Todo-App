'use client'

import { Card } from '@/components/ui/card'
import { ChatWindow } from '@/components/chat/ChatWindow'

interface ChatInterfaceProps {
  className?: string
}

export function ChatInterface({ className }: ChatInterfaceProps) {
  return (
    <Card className={`${className} bg-charcoal border-border-subtle rounded-none h-full overflow-hidden`}>
      <div className="p-4 border-b border-border-subtle">
        <p className="text-xs text-gray-500 font-mono uppercase tracking-wider">
          AI Assistant for Task Operations
        </p>
      </div>
      <div className="p-2 h-[500px]">
        <ChatWindow maxHeight="450px" className="border-0 bg-transparent" />
      </div>
    </Card>
  )
}
