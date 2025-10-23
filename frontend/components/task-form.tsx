'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Send, Calculator, Bot, AlertCircle } from 'lucide-react'
import { Agent } from '@/lib/schemas'

const taskFormSchema = z.object({
  problem: z.string().min(1, 'Problem is required'),
  type: z.string().min(1, 'Task type is required'),
})

type TaskFormData = z.infer<typeof taskFormSchema>

interface TaskFormProps {
  selectedAgent: string | null
  onSubmit: (data: TaskFormData) => void
  agents: Agent[]
}

export function TaskForm({ selectedAgent, onSubmit, agents }: TaskFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskFormSchema),
  })

  const watchedType = watch('type')

  const handleFormSubmit = async (data: TaskFormData) => {
    if (!selectedAgent) {
      return
    }

    setIsSubmitting(true)
    try {
      await onSubmit(data)
      reset()
    } catch (error) {
      console.error('Failed to submit task:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getTaskTypeDescription = (type: string) => {
    const descriptions: Record<string, string> = {
      math: 'Mathematical problem solving including algebra, calculus, and more',
      inventory: 'Inventory management and stock tracking tasks',
      social_media: 'Social media content creation and scheduling',
      general: 'General purpose tasks and problem solving',
    }
    return descriptions[type] || 'Custom task type'
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="h-5 w-5" />
            Submit New Task
          </CardTitle>
          <CardDescription>
            Submit a task to be processed by an available agent
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!selectedAgent && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Please select an agent from the Agents tab before submitting a task.
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="type" className="text-sm font-medium">
                Task Type
              </label>
              <Select {...register('type')}>
                <SelectTrigger>
                  <SelectValue placeholder="Select task type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="math">
                    <div className="flex items-center gap-2">
                      <Calculator className="h-4 w-4" />
                      Math Problem
                    </div>
                  </SelectItem>
                  <SelectItem value="inventory">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      Inventory Management
                    </div>
                  </SelectItem>
                  <SelectItem value="social_media">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      Social Media
                    </div>
                  </SelectItem>
                  <SelectItem value="general">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4" />
                      General Task
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
              {errors.type && (
                <p className="text-sm text-red-500">{errors.type.message}</p>
              )}
              {watchedType && (
                <p className="text-sm text-muted-foreground">
                  {getTaskTypeDescription(watchedType)}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="problem" className="text-sm font-medium">
                Problem Description
              </label>
              <Textarea
                {...register('problem')}
                placeholder="Describe the problem or task you want to solve..."
                className="min-h-[120px]"
              />
              {errors.problem && (
                <p className="text-sm text-red-500">{errors.problem.message}</p>
              )}
            </div>

            {selectedAgent && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Selected Agent</label>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">
                    {agents.find(a => a.id === selectedAgent)?.name || 'Unknown Agent'}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {agents.find(a => a.id === selectedAgent)?.agent_type}
                  </span>
                </div>
              </div>
            )}

            <Button 
              type="submit" 
              disabled={!selectedAgent || isSubmitting}
              className="w-full"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Submit Task
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Example Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>Example Tasks</CardTitle>
          <CardDescription>
            Click on an example to populate the form
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div 
              className="p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => {
                reset({
                  type: 'math',
                  problem: 'Solve the equation: 2x + 3 = 7'
                })
              }}
            >
              <h4 className="font-medium mb-2">Math Problem</h4>
              <p className="text-sm text-muted-foreground">
                Solve the equation: 2x + 3 = 7
              </p>
            </div>

            <div 
              className="p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => {
                reset({
                  type: 'math',
                  problem: 'Find the derivative of x^2 + 3x + 1'
                })
              }}
            >
              <h4 className="font-medium mb-2">Calculus</h4>
              <p className="text-sm text-muted-foreground">
                Find the derivative of x^2 + 3x + 1
              </p>
            </div>

            <div 
              className="p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => {
                reset({
                  type: 'math',
                  problem: 'Simplify the expression: (x + 2)(x - 3)'
                })
              }}
            >
              <h4 className="font-medium mb-2">Algebra</h4>
              <p className="text-sm text-muted-foreground">
                Simplify the expression: (x + 2)(x - 3)
              </p>
            </div>

            <div 
              className="p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => {
                reset({
                  type: 'general',
                  problem: 'Help me understand the concept of machine learning'
                })
              }}
            >
              <h4 className="font-medium mb-2">General</h4>
              <p className="text-sm text-muted-foreground">
                Help me understand the concept of machine learning
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
