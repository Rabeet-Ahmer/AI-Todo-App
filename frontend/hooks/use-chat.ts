"use client"

import { useState, useCallback } from "react"
import { clearChatHistoryAction, sendChatMessageAction } from "@/actions/chat.actions"
import type { ChatMessage, ChatResponse } from "@/lib/types"

interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  sendMessage: (content: string) => Promise<void>
  clearHistory: () => Promise<void>
  clearError: () => void
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return

    // Clear any previous error
    setError(null)

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call Server Action (issues backend JWT securely)
      const response = await sendChatMessageAction(content.trim()) as ChatResponse

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      // Set user-friendly error message
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Sorry, something went wrong. Please try again."
      setError(errorMessage)

      // Add error as assistant message so user can see it
      const errorAssistantMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I couldn't complete that. Please try again!",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorAssistantMessage])
    } finally {
      setIsLoading(false)
    }
  }, [isLoading])

  const clearHistory = useCallback(async () => {
    try {
      await clearChatHistoryAction()
      setMessages([])
      setError(null)
    } catch (err) {
      setError("Failed to clear chat history")
    }
  }, [])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearHistory,
    clearError,
  }
}
