import { type Todo } from "@/lib/types"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock, Calendar, Hash, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"

interface TodoDetailProps {
  todo: Todo
}

const priorityColors = {
  LOW: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  MEDIUM: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  HIGH: "bg-primary/10 text-primary border-primary/20",
}

export function TodoDetail({ todo }: TodoDetailProps) {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <Link
        href="/dashboard/todos"
        className="inline-flex items-center gap-2 text-xs font-mono text-gray-400 hover:text-primary transition-colors uppercase tracking-widest"
      >
        <ArrowLeft className="size-3" />
        Return to Objectives
      </Link>

      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="outline" className={cn(
            "text-[10px] font-mono px-2 py-0.5 rounded-none uppercase tracking-widest",
            priorityColors[todo.priority]
          )}>
            {todo.priority} Priority
          </Badge>
          <Badge variant="outline" className={cn(
            "text-[10px] font-mono px-2 py-0.5 rounded-none uppercase tracking-widest",
            todo.completed ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-blue-500/10 text-blue-500 border-blue-500/20"
          )}>
            Status: {todo.completed ? "Executed" : "Active"}
          </Badge>
        </div>

        <h2 className="text-4xl font-bold text-white uppercase tracking-tight font-display">
          {todo.title}
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-charcoal border border-border-subtle p-6 space-y-4">
            <h3 className="text-xs font-mono uppercase tracking-[0.2em] text-primary">Objective Description</h3>
            <p className="text-gray-300 leading-relaxed font-mono text-sm">
              {todo.description || "No tactical data provided for this objective."}
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-charcoal border border-border-subtle p-6 space-y-4">
            <h3 className="text-xs font-mono uppercase tracking-[0.2em] text-primary">Metadata</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-gray-400">
                <Hash className="size-4" />
                <span className="text-xs font-mono uppercase tracking-wider">ID: {todo.id}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-400">
                <Calendar className="size-4" />
                <span className="text-xs font-mono uppercase tracking-wider">Created: {new Date(todo.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-400">
                <Clock className="size-4" />
                <span className="text-xs font-mono uppercase tracking-wider">Last Sync: {new Date(todo.updated_at).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
