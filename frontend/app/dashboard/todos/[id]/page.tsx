import { notFound } from "next/navigation"
import { TodoDetail } from "@/components/todos/TodoDetail"
import { type Todo } from "@/lib/types"

// Mock data for UI demonstration
const mockTodos: Todo[] = [
  {
    id: 1,
    title: "Infiltrate target database",
    description: "Access core systems and extract encrypted payloads. Ensure all entry points are masked and no digital fingerprints are left behind.",
    completed: false,
    priority: "HIGH",
    user_id: "mock-user",
    created_at: "2026-01-02T10:00:00Z",
    updated_at: "2026-01-02T12:00:00Z",
  },
  {
    id: 2,
    title: "Secure communication uplink",
    description: "Establish encrypted VPN tunnel between local node and HQ. Verify signal strength and packet integrity.",
    completed: true,
    priority: "MEDIUM",
    user_id: "mock-user",
    created_at: "2026-01-01T08:30:00Z",
    updated_at: "2026-01-02T09:15:00Z",
  },
  {
    id: 3,
    title: "Scrub system logs",
    description: "Remove traces of operative presence from edge servers. Automated scripts may be deployed, but manual verification is mandatory.",
    completed: false,
    priority: "LOW",
    user_id: "mock-user",
    created_at: "2026-01-02T11:00:00Z",
    updated_at: "2026-01-02T11:00:00Z",
  },
]

type Params = Promise<{ id: string }>

export default async function TodoDetailPage({ params }: { params: Params }) {
  const { id } = await params
  const todo = mockTodos.find((t) => t.id === Number(id))

  if (!todo) {
    notFound()
  }

  return (
    <div className="max-w-5xl mx-auto py-4">
      <TodoDetail todo={todo} />
    </div>
  )
}
