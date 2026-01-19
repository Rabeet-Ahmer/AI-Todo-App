/**
 * AgentStatus component - shows "Agent is thinking..." indicator
 *
 * T039: Create AgentStatus component using shadcn/ui Card
 */

import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

export interface AgentStatusProps {
  isLoading: boolean;
}

export function AgentStatus({ isLoading }: AgentStatusProps) {
  if (!isLoading) return null;

  return (
    <div className="animate-pulse">
      <Card className="border-blue-200 dark:border-blue-900 bg-blue-50 dark:bg-blue-950">
        <CardContent className="flex items-center gap-2 p-3">
          <Loader2 className="h-4 w-4 animate-spin text-blue-600 dark:text-blue-400" />
          <span className="text-sm text-blue-700 dark:text-blue-300">
            Agent is thinking...
          </span>
        </CardContent>
      </Card>
    </div>
  );
}
