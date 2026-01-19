/**
 * ChatWindow component - Main chat interface container
 *
 * T041: Create ChatWindow Client Component orchestrating all chat UI
 * T042: Style chat components with TailwindCSS
 */

"use client";

import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { useChat } from "@/hooks/useChat";
import { ChatInput } from "./ChatInput";
import { AgentStatus } from "./AgentStatus";
import { MessageList } from "./MessageList";
import { Bot, X, MessageSquare } from "lucide-react";

export interface ChatWindowProps {
  className?: string;
  maxHeight?: string;
}

export function ChatWindow({ className, maxHeight = "500px" }: ChatWindowProps) {
  const { messages, isLoading, error, sendMessage } = useChat();

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  return (
    <Card className={className}>
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-semibold">Todo Assistant</h3>
          </div>
          <MessageSquare className="h-4 w-4 text-gray-500" />
        </div>
      </CardHeader>

      <CardContent className="px-0" style={{ height: maxHeight }}>
        {error && (
          <div className="mx-4 mb-2 rounded-md border border-red-200 bg-red-50 p-3 text-red-700">
            <div className="flex items-start gap-2">
              <X className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        <AgentStatus isLoading={isLoading} />

        <MessageList
          messages={messages}
          className="overflow-y-auto px-4"
        />
      </CardContent>

      <CardFooter className="border-t p-4">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          placeholder={
            isLoading
              ? "Agent is responding..."
              : "Type a message (e.g., 'Add a task to buy groceries')"
          }
        />
      </CardFooter>
    </Card>
  );
}
