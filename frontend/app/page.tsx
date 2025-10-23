'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Bot, 
  Brain, 
  Calculator, 
  Send, 
  Activity, 
  CheckCircle, 
  XCircle, 
  Clock,
  Zap,
  Target,
  Shield
} from 'lucide-react'
import { useWebSocket } from '@/lib/websocket-provider'
import { apiClient } from '@/lib/api-client'
import { TaskForm } from '@/components/task-form'
import { AgentCard } from '@/components/agent-card'
import { OntologyGraph } from '@/components/ontology-graph'

interface Agent {
  id: string
  name: string
  agent_type: string
  capabilities: Record<string, any>
  status: 'active' | 'inactive' | 'error' | 'maintenance'
  last_heartbeat: string | null
  created_at: string
  updated_at: string
}

interface Task {
  id: string
  user_id: string | null
  agent_id: string
  directive_id: string
  input_data: Record<string, any>
  output_data: Record<string, any> | null
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled'
  error_message: string | null
  created_at: string
  completed_at: string | null
}

interface Directive {
  id: string
  task_type: string
  constraints: Record<string, any>
  source_values: string[]
  source_beliefs: string[]
  created_at: string
  expires_at: string | null
}

export default function Dashboard() {
  const { socket, isConnected } = useWebSocket()
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [taskInput, setTaskInput] = useState('')

  // Fetch agents
  const { data: agents = [], isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => apiClient.getAgents(),
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  // Fetch recent tasks
  const { data: recentTasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks', 'recent'],
    queryFn: () => apiClient.getRecentTasks(),
    refetchInterval: 3000, // Refetch every 3 seconds
  })

  // Fetch ontology summary
  const { data: ontologySummary } = useQuery({
    queryKey: ['ontology', 'summary'],
    queryFn: () => apiClient.getOntologySummary(),
  })

  const activeAgents = agents.filter(agent => agent.status === 'active')
  const completedTasks = recentTasks.filter(task => task.status === 'completed')
  const failedTasks = recentTasks.filter(task => task.status === 'failed')

  const handleTaskSubmit = async (taskData: { problem: string; type: string }) => {
    if (!selectedAgent || !taskData.problem.trim()) return

    try {
      // Generate directive first
      const directive = await apiClient.createDirective(
        taskData.problem,
        taskData.type
      )

      // Create task
      const task = await apiClient.createTask({
        user_id: 'user-123', // In real app, get from auth context
        agent_id: selectedAgent,
        directive_id: directive.id,
        input_data: taskData
      })

      // Send task via WebSocket
      socket?.emit('task_request', {
        user_id: 'user-123',
        task_type: taskData.type,
        input_data: taskData
      })

      setTaskInput('')
    } catch (error) {
      console.error('Failed to submit task:', error)
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold gradient-text">
            Mothership AIs
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Central AI with ontological library for specialized agents
          </p>
          <div className="flex items-center justify-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeAgents.length}</div>
              <p className="text-xs text-muted-foreground">
                {agents.length} total agents
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Tasks</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{completedTasks.length}</div>
              <p className="text-xs text-muted-foreground">
                {recentTasks.length} total tasks
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {recentTasks.length > 0 
                  ? Math.round((completedTasks.length / recentTasks.length) * 100)
                  : 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Task completion rate
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Ontology</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {ontologySummary?.total_values || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                {ontologySummary?.total_beliefs || 0} beliefs
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="ontology">Ontology</TabsTrigger>
            <TabsTrigger value="submit">Submit Task</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agentsLoading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardHeader>
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="h-3 bg-muted rounded"></div>
                        <div className="h-3 bg-muted rounded w-5/6"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                agents.map((agent) => (
                  <AgentCard
                    key={agent.id}
                    agent={agent}
                    isSelected={selectedAgent === agent.id}
                    onSelect={() => setSelectedAgent(agent.id)}
                  />
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="tasks" className="space-y-6">
            <div className="space-y-4">
              {tasksLoading ? (
                <div className="space-y-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Card key={i} className="animate-pulse">
                      <CardContent className="p-6">
                        <div className="space-y-2">
                          <div className="h-4 bg-muted rounded w-1/4"></div>
                          <div className="h-3 bg-muted rounded w-3/4"></div>
                          <div className="h-3 bg-muted rounded w-1/2"></div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : recentTasks.length > 0 ? (
                recentTasks.map((task) => (
                  <Card key={task.id} className="card-hover">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Badge variant={
                              task.status === 'completed' ? 'default' :
                              task.status === 'failed' ? 'destructive' :
                              task.status === 'in_progress' ? 'secondary' : 'outline'
                            }>
                              {task.status}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {new Date(task.created_at).toLocaleString()}
                            </span>
                          </div>
                          <p className="font-medium">
                            {task.input_data.problem || 'Task'}
                          </p>
                          {task.output_data && (
                            <div className="text-sm text-muted-foreground">
                              <strong>Result:</strong> {JSON.stringify(task.output_data)}
                            </div>
                          )}
                          {task.error_message && (
                            <Alert variant="destructive">
                              <XCircle className="h-4 w-4" />
                              <AlertDescription>
                                {task.error_message}
                              </AlertDescription>
                            </Alert>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {task.status === 'in_progress' && (
                            <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
                          )}
                          {task.status === 'completed' && (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          )}
                          {task.status === 'failed' && (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card>
                  <CardContent className="p-6 text-center">
                    <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No tasks yet</h3>
                    <p className="text-muted-foreground">
                      Submit a task to see it appear here
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          <TabsContent value="ontology" className="space-y-6">
            <OntologyGraph />
          </TabsContent>

          <TabsContent value="submit" className="space-y-6">
            <TaskForm
              selectedAgent={selectedAgent}
              onSubmit={handleTaskSubmit}
              agents={activeAgents}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
