"use client"

import { useState } from "react"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import { ChatButton } from "./ChatButton"
import { ChatWindow } from "./ChatWindow"

export function ChatContainer() {
  const [isOpen, setIsOpen] = useState(false)

  const toggleChat = () => setIsOpen((prev) => !prev)

  return (
    <>
      {/* Floating Chat Button */}
      <ChatButton isOpen={isOpen} onClick={toggleChat} />

      {/* Chat Drawer */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent
          side="right"
          className="w-full sm:max-w-md p-0 flex flex-col bg-background/80 backdrop-blur-xl border-l border-border-subtle"
        >
          <SheetHeader className="sr-only">
            <SheetTitle>Chat Assistant</SheetTitle>
            <SheetDescription>
              Chat with our AI assistant to manage your todos.
            </SheetDescription>
          </SheetHeader>
          <ChatWindow className="h-full" />
        </SheetContent>
      </Sheet>
    </>
  )
}
