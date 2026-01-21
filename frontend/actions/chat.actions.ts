"use server"

import { requireAuth } from "@/actions/auth.actions"
import { issueBackendJwt } from "@/lib/backend-jwt"
import type { ChatResponse } from "@/lib/types"

function getUserIdFromSession(session: unknown): string | null {
    if (!session || typeof session !== "object") return null
    const maybeUser = (session as { user?: unknown }).user
    if (!maybeUser || typeof maybeUser !== "object") return null
    const maybeId = (maybeUser as { id?: unknown }).id
    return typeof maybeId === "string" && maybeId.length > 0 ? maybeId : null
}

/**
 * Send a message to the AI chat agent.
 * Uses server action to securely issue JWT for FastAPI authentication.
 */
export async function sendChatMessageAction(content: string): Promise<ChatResponse> {
    if (!content.trim()) {
        throw new Error("Message content is required")
    }

    const session = await requireAuth()
    const userId = getUserIdFromSession(session)

    if (!userId) {
        throw new Error("Authenticated session is missing user id")
    }

    const token = await issueBackendJwt(userId)
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

    const response = await fetch(`${baseUrl}/chat/message`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ content: content.trim() }),
    })

    if (!response.ok) {
        const errorText = await response.text()
        console.error("Chat API error:", errorText)
        throw new Error("Failed to send message. Please try again.")
    }

    return await response.json() as ChatResponse
}

/**
 * Clear chat history for the current user.
 */
export async function clearChatHistoryAction(): Promise<{ message: string }> {
    const session = await requireAuth()
    const userId = getUserIdFromSession(session)

    if (!userId) {
        throw new Error("Authenticated session is missing user id")
    }

    const token = await issueBackendJwt(userId)
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

    const response = await fetch(`${baseUrl}/chat/session`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
        },
    })

    if (!response.ok) {
        throw new Error("Failed to clear chat history")
    }

    return await response.json()
}
