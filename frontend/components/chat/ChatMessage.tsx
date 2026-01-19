/**
 * ChatMessage component - displays a single message in the chat
 *
 * T037: Create ChatMessage component
 */

import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";

export interface ChatMessageProps {
  sender: "user" | "agent";
  text: string;
  timestamp: Date;
  actionPerformed?: "create" | "read" | "update" | "delete" | "query" | "none";
  todosAffected?: number[];
}

export function ChatMessage({
  sender,
  text,
  timestamp,
  actionPerformed,
  todosAffected,
}: ChatMessageProps) {
  const isUser = sender === "user";

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <Card
        className={cn(
          "max-w-[80%] px-4 py-3",
          isUser
            ? "bg-blue-600 text-white border-blue-600"
            : "bg-card text-card-foreground"
        )}
      >
        <div className="text-sm whitespace-pre-wrap">{text}</div>

        {/* Show action indicator if agent performed an action */}
        {!isUser && actionPerformed && actionPerformed !== "none" && (
          <div className="mt-2 text-xs opacity-80 flex items-center gap-2">
            {actionPerformed === "create" && "✓ Created"}
            {actionPerformed === "update" && "✓ Updated"}
            {actionPerformed === "delete" && "✓ Deleted"}
            {actionPerformed === "read" && "✓ Retrieved"}
            {actionPerformed === "query" && "✓ Queried"}
            {todosAffected && todosAffected.length > 0 && (
              <span className="ml-1">
                (Todo{todosAffected.length > 1 ? "s" : ""}: {todosAffected.join(", ")})
              </span>
            )}
          </div>
        )}

        <div className="text-xs opacity-60 mt-1">
          {timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </Card>
    </div>
  );
}
