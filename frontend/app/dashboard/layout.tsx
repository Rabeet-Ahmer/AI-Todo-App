import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/dashboard/AppSidebar"
import { cookies } from "next/headers"
import { requireAuth } from "@/actions/auth.actions"
import { redirect } from "next/navigation"

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get("sidebar_state")?.value === "true"

  // Get user session data
  const session = await requireAuth()
  const user = (session as any)?.user || null

  // If no user data, redirect to login
  if (!user) {
    redirect('/login')
  }

  return (
    <SidebarProvider defaultOpen={defaultOpen}>
      <AppSidebar user={user} />
      <SidebarInset>
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-2 border-b border-border-subtle px-4 bg-charcoal">
          <SidebarTrigger className="-ml-1 text-primary" />
          <div className="h-4 w-px bg-border-subtle mx-2" />
          <h1 className="font-display text-sm font-bold uppercase tracking-widest text-white">
            System Dashboard
          </h1>
        </header>
        <main className="flex-1 overflow-y-auto p-6 bg-obsidian text-white animate-fade-in">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
