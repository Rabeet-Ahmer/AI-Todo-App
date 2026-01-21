/**
 * API Client for FastAPI Backend
 * Handles token injection from Better Auth JWT (jwt plugin)
 */

async function getAuthToken(): Promise<string | null> {
    // IMPORTANT: better-auth.session_token is NOT a JWT.
    // For FastAPI, we need the JWT issued by the Better Auth jwt plugin.
    // For now, we don't have a safe way to fetch it on the server,
    // so this function returns null and FastAPI endpoints should be tested
    // with auth temporarily disabled or with a manual token.
    return null;
}

export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = await getAuthToken();

    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

    const response = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "API request failed" }));
        const errorMessage = errorData.detail || "API request failed";
        throw new Error(errorMessage);
    }

    return response.json();
}

export const api = {
    get: <T>(endpoint: string, options?: RequestInit) =>
        apiRequest<T>(endpoint, { ...options, method: "GET" }),
    post: <T>(endpoint: string, data: unknown, options?: RequestInit) =>
        apiRequest<T>(endpoint, { ...options, method: "POST", body: JSON.stringify(data) }),
    patch: <T>(endpoint: string, data: unknown, options?: RequestInit) =>
        apiRequest<T>(endpoint, { ...options, method: "PATCH", body: JSON.stringify(data) }),
    delete: <T>(endpoint: string, options?: RequestInit) =>
        apiRequest<T>(endpoint, { ...options, method: "DELETE" }),

    // Chat API for AI Agent
    chat: {
        sendMessage: (content: string) =>
            apiRequest<{ message: string; todos_affected?: unknown[] }>("/chat/message", {
                method: "POST",
                body: JSON.stringify({ content }),
            }),
        clearHistory: () =>
            apiRequest<{ message: string }>("/chat/session", {
                method: "DELETE",
            }),
    },
};
