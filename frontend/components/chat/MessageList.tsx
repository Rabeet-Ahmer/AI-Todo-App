/**
 * MessageList component - scrollable container for chat messages
 *
 * T040: Create MessageList component
 */

import { Card, CardContent } from "@/components/ui/card";
import { ChatMessage } from "./ChatMessage";

export interface ChatMessageData {
  id: string;
  sender: "user" | "agent";
  text: string;
  timestamp: Date;
  actionPerformed?: "create" | "read" | "update" | "delete" | "query" | "none";
  todosAffected?: number[];
}

export interface MessageListProps {
  messages: ChatMessageData[];
  className?: string;
}

export function MessageList({ messages, className }: MessageListProps) {
  return (
    <div className={className}>
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="mb-2">Start a conversation to manage your todos</p>
            <p className="text-sm opacity-70">Try: "Add a task to buy groceries"</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4 pb-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              sender={message.sender}
              text={message.text}
              timestamp={message.timestamp}
              actionPerformed={message.actionPerformed}
              todosAffected={message.todosAffected}
            />
          ))}
        </div>
      )}
    </div>
  );
}
