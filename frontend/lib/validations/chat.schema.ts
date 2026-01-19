/**
 * Zod schemas for chat message validation
 *
 * T019: Create chat validation schemas
 */

import { z } from "zod";

/**
 * Schema for chat message input
 */
export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, "Message cannot be empty")
    .max(2000, "Message too long (max 2000 characters)"),
  session_id: z.string().uuid().optional(),
});

export type ChatMessageInput = z.infer<typeof chatMessageSchema>;

/**
 * Schema for chat message response from API
 */
export const chatResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  action_performed: z
    .enum(["create", "read", "update", "delete", "query", "none"])
    .nullable()
    .optional(),
  todos_affected: z.array(z.number()).nullable().optional(),
  clarification_needed: z.boolean().default(false),
  clarification_prompt: z.string().nullable().optional(),
  session_id: z.string(),
});

export type ChatResponse = z.infer<typeof chatResponseSchema>;

/**
 * Schema for chat error response
 */
export const chatErrorSchema = z.object({
  success: z.literal(false),
  error: z.string(),
  error_code: z.string(),
  session_id: z.string().nullable().optional(),
});

export type ChatError = z.infer<typeof chatErrorSchema>;
