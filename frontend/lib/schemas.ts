import { z } from 'zod'

// API Response Schemas
export const AgentSchema = z.object({
  id: z.string(),
  name: z.string(),
  agent_type: z.string(),
  capabilities: z.record(z.any()),
  status: z.enum(['active', 'inactive', 'error', 'maintenance']),
  last_heartbeat: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const TaskSchema = z.object({
  id: z.string(),
  user_id: z.string().nullable(),
  agent_id: z.string(),
  directive_id: z.string(),
  input_data: z.record(z.any()),
  output_data: z.record(z.any()).nullable(),
  status: z.enum(['pending', 'in_progress', 'completed', 'failed', 'cancelled']),
  error_message: z.string().nullable(),
  created_at: z.string(),
  completed_at: z.string().nullable(),
})

export const DirectiveSchema = z.object({
  id: z.string(),
  task_type: z.string(),
  constraints: z.record(z.any()),
  source_values: z.array(z.string()),
  source_beliefs: z.array(z.string()),
  created_at: z.string(),
  expires_at: z.string().nullable(),
})

export const ValueSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const BeliefSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  related_values: z.array(z.string()),
  created_at: z.string(),
  updated_at: z.string(),
})

export const OntologySummarySchema = z.object({
  total_values: z.number(),
  total_beliefs: z.number(),
  ontology_size: z.number(),
})

// Request Schemas
export const CreateTaskSchema = z.object({
  user_id: z.string().optional(),
  agent_id: z.string(),
  directive_id: z.string(),
  input_data: z.record(z.any()),
})

export const CreateDirectiveSchema = z.object({
  task_description: z.string(),
  task_type: z.string(),
  user_context: z.record(z.any()).optional(),
})

export const CreateValueSchema = z.object({
  name: z.string(),
  description: z.string(),
})

export const CreateBeliefSchema = z.object({
  name: z.string(),
  description: z.string(),
  related_values: z.array(z.string()).default([]),
})

// Type exports
export type Agent = z.infer<typeof AgentSchema>
export type Task = z.infer<typeof TaskSchema>
export type Directive = z.infer<typeof DirectiveSchema>
export type Value = z.infer<typeof ValueSchema>
export type Belief = z.infer<typeof BeliefSchema>
export type OntologySummary = z.infer<typeof OntologySummarySchema>
export type CreateTask = z.infer<typeof CreateTaskSchema>
export type CreateDirective = z.infer<typeof CreateDirectiveSchema>
export type CreateValue = z.infer<typeof CreateValueSchema>
export type CreateBelief = z.infer<typeof CreateBeliefSchema>
