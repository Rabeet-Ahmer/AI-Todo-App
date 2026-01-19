'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { ChatWindow } from './ChatWindow'
import { MessageSquare, X } from 'lucide-react'

interface FloatingChatProps {
  initialOpen?: boolean
}

export function FloatingChat({ initialOpen = false }: FloatingChatProps) {
  const [open, setOpen] = useState(initialOpen)

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button
            size="icon"
            className="h-14 w-14 rounded-full shadow-lg bg-gradient-to-br from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300 hover:scale-110 active:scale-95"
          >
            {open ? (
              <X className="h-6 w-6 text-white" />
            ) : (
              <MessageSquare className="h-6 w-6 text-white" />
            )}
            <span className="sr-only">Open AI Chat</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="right" className="w-full sm:max-w-md p-0 border-l border-border-subtle bg-charcoal">
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-400" />
                <h2 className="text-lg font-semibold text-white font-display uppercase tracking-wider">Todo Assistant</h2>
              </div>
              <p className="text-xs text-gray-500 font-mono mt-1">
                AI-powered task management assistant
              </p>
            </div>

            {/* Chat Window */}
            <div className="flex-1 overflow-hidden">
              <ChatWindow
                className="border-0 bg-transparent h-full"
                maxHeight="100%"
              />
            </div>
          </div>
        </SheetContent>
      </Sheet>

      {/* Optional: Badge for unread messages */}
      {!open && (
        <div className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full animate-pulse border-2 border-charcoal">
          <span className="sr-only">New messages</span>
        </div>
      )}
    </div>
  )
}
