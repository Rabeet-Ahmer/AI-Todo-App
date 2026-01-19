export interface User {
  id: string
  email: string
  name?: string
  image?: string
}

export interface Todo {
  id: number
  title: string
  description?: string
  completed: boolean
  priority: "LOW" | "MEDIUM" | "HIGH"
  user_id: string
  created_at: string
  updated_at: string
}

export interface ApiError {
  detail: string
  status_code?: number
}

// T048: ChatMessage type for agent chat interface
export interface ChatMessage {
  id: string
  sender: "user" | "agent"
  text: string
  timestamp: Date
  actionPerformed?: "create" | "read" | "update" | "delete" | "query" | "none"
  todosAffected?: number[]
  clarificationNeeded?: boolean
  clarificationPrompt?: string
}

// T048: ChatResponse type from backend API
export interface ChatResponse {
  success: boolean
  message: string
  action_performed?: string | null
  todos_affected?: number[] | null
  clarification_needed?: boolean
  clarification_prompt?: string | null
  session_id: string
}
