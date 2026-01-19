/**
 * useChat hook - chat state management and API communication
 *
 * T043-T048: Implement useChat hook with API calls
 * T043: Create hook with messages state
 * T044: Add sendMessage function calling POST /api/v1/chat/message
 * T045: Add isLoading state
 * T046: Add error handling
 * T047: Update api-client.ts (validate function exists)
 * T048: Add ChatMessage type to types.ts
 */

"use client";

import { useState, useCallback } from "react";

// Chat API endpoint
const CHAT_API_ENDPOINT = "/chat/message";

// T048: ChatMessage type (also defined in types.ts)
export interface ChatMessage {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: Date;
  actionPerformed?: "create" | "read" | "update" | "delete" | "query" | "none";
  todosAffected?: number[];
  clarificationNeeded?: boolean;
  clarificationPrompt?: string;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  action_performed?: string | null;
  todos_affected?: number[] | null;
  clarification_needed?: boolean;
  clarification_prompt?: string | null;
  session_id: string;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  setSessionId: (sessionId: string) => void;
}

/**
 * Hook for managing chat state and API communication
 *
 * Handles:
 * - Message history
 * - Loading states
 * - Error handling
 * - API communication with backend
 * - Session management
 */
export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  /**
   * T044: Send message to agent API
   * T045: Manage loading state
   * T046: Handle errors
   * T047: Use existing api.post from api-client.ts
   */
  const sendMessage = useCallback(
    async (message: string): Promise<void> => {
      // Previous message object (will be sent to API after response)
      const tempUserMessage: ChatMessage = {
        id: crypto.randomUUID(),
        sender: "user",
        text: message,
        timestamp: new Date(),
      };

      // Add user message immediately
      setMessages((prev) => [...prev, tempUserMessage]);
      setIsLoading(true);
      setError(null);

      try {
        // Dynamically import api to avoid SSR issues
        const { api } = await import("@/lib/api-client");

        const response = await api.post<ChatResponse>(CHAT_API_ENDPOINT, {
          message,
          session_id: sessionId,
        });

        // Add agent message
        const agentMessage: ChatMessage = {
          id: crypto.randomUUID(),
          sender: "agent",
          text: response.message,
          timestamp: new Date(),
          actionPerformed: response.action_performed as
            | "create"
            | "read"
            | "update"
            | "delete"
            | "query"
            | "none"
            | undefined,
          todosAffected: response.todos_affected || undefined,
          clarificationNeeded: response.clarification_needed,
          clarificationPrompt: response.clarification_prompt || undefined,
        };

        setMessages((prev) => [...prev, agentMessage]);

        // Update session ID for conversation continuity
        if (response.session_id) {
          setSessionId(response.session_id);
        }
      } catch (err) {
        // T046: Error handling
        const errorMessage =
          err instanceof Error ? err.message : "Failed to send message";
        setError(errorMessage);

        // Remove the user message on error (optional - you could keep it)
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  const clearMessages = () => {
    setMessages([]);
    setError(null);
  };

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearMessages,
    setSessionId,
  };
}
