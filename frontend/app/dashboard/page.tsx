import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, CheckCircle2, Clock, AlertCircle, CheckCircle } from "lucide-react"
import { requireAuth } from "@/actions/auth.actions"
import { issueBackendJwt } from "@/lib/backend-jwt"
import { type Todo } from "@/lib/types"

// Force dynamic rendering since we use headers() for auth
export const dynamic = 'force-dynamic'

type TodoStats = {
  total: number
  pending: number
  completed: number
}

export default async function DashboardPage() {
  // Ensure user is authenticated
  const session = await requireAuth()
  const userId = (session as any)?.user?.id as string | undefined

  if (!userId) {
    throw new Error("Authenticated session is missing user id")
  }

  const token = await issueBackendJwt(userId)
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

  let statsData: TodoStats = {
    total: 0,
    pending: 0,
    completed: 0,
  }

  let todos: Todo[] = []

  try {
    const statsResponse = await fetch(`${baseUrl}/users/me/todos/stats`, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    })

    if (statsResponse.ok) {
      statsData = await statsResponse.json()
    } else {
      console.error("Failed to fetch todo stats:", await statsResponse.text())
    }

    const todosResponse = await fetch(`${baseUrl}/todos`, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      cache: "no-store",
    })

    if (todosResponse.ok) {
      todos = await todosResponse.json()
    } else {
      console.error("Failed to fetch todos:", await todosResponse.text())
    }
  } catch (error) {
    console.error("Failed to fetch dashboard data:", error)
  }

  const stats = [
    {
      title: "Total Operations",
      description: "All tracked objectives",
      value: statsData.total.toString(),
      icon: Activity,
      color: "text-primary",
    },
    {
      title: "Tactical Execution",
      description: "Missions completed",
      value: statsData.completed.toString(),
      icon: CheckCircle2,
      color: "text-green-500",
    },
    {
      title: "Active Engagements",
      description: "Immediate priority",
      value: statsData.pending.toString(),
      icon: Clock,
      color: "text-blue-500",
    },
  ]

  // Get recent todos for briefing section
  const recentTodos = todos
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)

  const highPriorityTodos = todos
    .filter(todo => !todo.completed && todo.priority === "HIGH")
    .slice(0, 2)

  return (
    <div className="space-y-8 max-w-6xl mx-auto animate-fade-in">
      <div className="space-y-2 animate-slide-down">
        <h2 className="text-3xl font-bold text-white uppercase tracking-tight font-display">
          Mission Overview
        </h2>
        <p className="text-gray-400 font-mono text-xs uppercase tracking-widest">
          Synchronizing operative data with central command
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, index) => (
          <div
            key={stat.title}
            className="animate-slide-up"
            style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
          >
            <Card className="bg-charcoal border-border-subtle hover:border-primary/50 transition-all-fast rounded-none h-full">
              <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                <CardTitle className="text-[10px] font-mono uppercase tracking-[0.2em] text-gray-400">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`size-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white mb-1 font-display uppercase tracking-widest">{stat.value}</div>
                <p className="text-[10px] text-gray-500 font-mono uppercase tracking-wider italic">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>

      <div className="">
        {/* Left Column - Tactical Briefing */}
        <div className="space-y-4 animate-slide-up" style={{ animationDelay: '400ms', animationFillMode: 'both' }}>
          <h3 className="text-xs font-mono uppercase tracking-[0.2em] text-primary border-l-2 border-primary pl-3">
            Tactical Briefing
          </h3>
          <Card className="bg-charcoal border-border-subtle rounded-none p-6 transition-all-fast hover:border-primary/30 h-full w-fullrtha">
          <div className="space-y-6">
            {/* High Priority Section */}
            {highPriorityTodos.length > 0 && (
              <>
                <div className="flex gap-4 items-start">
                  <div className="mt-1 h-3 w-3 bg-primary animate-pulse" />
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-2">Critical Objectives</h4>
                    <div className="space-y-2">
                      {highPriorityTodos.map(todo => (
                        <p key={todo.id} className="text-xs text-gray-400 font-mono leading-relaxed max-w-2xl">
                          {todo.title}
                          {todo.description && <span className="text-gray-500 ml-2">— {todo.description}</span>}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="h-px bg-border-subtle w-full" />
              </>
            )}

            {/* Recent Activity Section */}
            <div className="flex gap-4 items-start">
              <div className="mt-1 h-3 w-3 bg-blue-500" />
              <div>
                <h4 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">Recent Activity</h4>
                {recentTodos.length > 0 ? (
                  <div className="space-y-2">
                    {recentTodos.map(todo => (
                      <div key={todo.id} className="flex items-center gap-2">
                        {todo.completed ? (
                          <CheckCircle className="size-3 text-green-500 shrink-0" />
                        ) : (
                          <AlertCircle className="size-3 text-yellow-500 shrink-0" />
                        )}
                        <p className="text-xs text-gray-400 font-mono leading-relaxed max-w-2xl">
                          {todo.title}
                          <span className="text-gray-500 ml-2">
                            — {new Date(todo.created_at).toLocaleDateString()}
                          </span>
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 font-mono leading-relaxed max-w-2xl">
                    No recent activity. Initialize new objectives to begin tracking.
                  </p>
                )}
              </div>
            </div>

            {/* Empty State */}
            {todos.length === 0 && (
              <>
                <div className="h-px bg-border-subtle w-full" />
                <div className="flex gap-4 items-start opacity-70">
                  <div className="mt-1 h-3 w-3 bg-gray-600" />
                  <div>
                    <h4 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-2">System Ready</h4>
                    <p className="text-xs text-gray-500 font-mono leading-relaxed max-w-2xl">
                      No objectives in database. Navigate to the operations terminal to initialize your first task.
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </Card>
        </div>

        {/* Right Column - Agent Chat Interface
        <div className="space-y-4 animate-slide-up" style={{ animationDelay: '500ms', animationFillMode: 'both' }}>
          <h3 className="text-xs font-mono uppercase tracking-[0.2em] text-blue-400 border-l-2 border-blue-400 pl-3">
            Agent Interface
          </h3>
          <div className="h-full">
            {/* ChatInterface is a Client Component wrapper 
            <div className="h-full">
              {/* Placeholder will be replaced by dynamic import 
              <div className="text-xs text-gray-600 text-center p-8 italic font-mono">
                Loading AI assistant...
              </div>
            </div>
          </div>
        </div> */}
      </div>
    </div>
  )
}
