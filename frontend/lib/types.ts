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
