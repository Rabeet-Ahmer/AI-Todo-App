"use client"

import { useEffect, useRef } from "react"
import { Trash2Icon, MessageSquareIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { ChatLoading } from "./ChatLoading"
import { useChat } from "@/hooks/use-chat"
import { cn } from "@/lib/utils"

interface ChatWindowProps {
  className?: string
}

export function ChatWindow({ className }: ChatWindowProps) {
  const { messages, isLoading, error, sendMessage, clearHistory } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  const isEmpty = messages.length === 0

  return (
    <div className={cn("flex h-full flex-col", className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b bg-background/50 px-4 py-3">
        <div className="flex items-center gap-2">
          <MessageSquareIcon className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">Chat Assistant</h2>
        </div>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearHistory}
            className="text-muted-foreground hover:text-destructive"
          >
            <Trash2Icon className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <MessageSquareIcon className="h-12 w-12 text-muted-foreground/30 mb-4" />
            <h3 className="font-medium text-muted-foreground mb-2">
              Hi! I can help you manage your todos.
            </h3>
            <p className="text-sm text-muted-foreground/70 max-w-[250px]">
              Try saying &quot;show my todos&quot; or &quot;add a task to buy groceries&quot;
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && <ChatLoading />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mb-2 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Input Area */}
      <ChatInput
        onSend={sendMessage}
        disabled={isLoading}
        placeholder="Ask me to manage your todos..."
      />
    </div>
  )
}
