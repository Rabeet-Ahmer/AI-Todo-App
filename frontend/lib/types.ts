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

// Chat types for AI Agent
export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export interface ChatRequest {
  content: string
}

export interface ChatResponse {
  message: string
  todos_affected?: Todo[]
}
