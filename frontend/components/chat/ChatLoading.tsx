"use client"

import { cn } from "@/lib/utils"

interface ChatLoadingProps {
  className?: string
}

export function ChatLoading({ className }: ChatLoadingProps) {
  return (
    <div className={cn("flex justify-start", className)}>
      <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
        <div className="flex items-center gap-1">
          <span className="text-sm text-muted-foreground">Thinking</span>
          <span className="flex gap-1">
            <span
              className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce"
              style={{ animationDelay: "0ms" }}
            />
            <span
              className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce"
              style={{ animationDelay: "150ms" }}
            />
            <span
              className="h-1.5 w-1.5 rounded-full bg-muted-foreground/60 animate-bounce"
              style={{ animationDelay: "300ms" }}
            />
          </span>
        </div>
      </div>
    </div>
  )
}
