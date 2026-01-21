"use client"

import { MessageCircleIcon, XIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ChatButtonProps {
  isOpen: boolean
  onClick: () => void
  className?: string
}

export function ChatButton({ isOpen, onClick, className }: ChatButtonProps) {
  return (
    <Button
      onClick={onClick}
      size="icon"
      className={cn(
        "fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full shadow-lg",
        "transition-all duration-300 ease-in-out",
        "hover:scale-110 hover:shadow-xl",
        isOpen && "rotate-90",
        className
      )}
    >
      {isOpen ? (
        <XIcon className="h-6 w-6" />
      ) : (
        <MessageCircleIcon className="h-6 w-6" />
      )}
      <span className="sr-only">
        {isOpen ? "Close chat" : "Open chat"}
      </span>
    </Button>
  )
}
