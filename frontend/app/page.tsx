'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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

export default function Dashboard() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

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
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm text-muted-foreground">
              Connected
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
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">
                5 total agents
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Tasks</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">127</div>
              <p className="text-xs text-muted-foreground">
                150 total tasks
              </p>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">85%</div>
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
              <div className="text-2xl font-bold">8</div>
              <p className="text-xs text-muted-foreground">
                5 beliefs
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
              <Card className="card-hover">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calculator className="h-5 w-5 text-primary" />
                    Math Solver
                  </CardTitle>
                  <CardDescription>Mathematical problem solving agent</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Badge variant="default">Active</Badge>
                    <p className="text-sm text-muted-foreground">
                      Capabilities: Algebra, Calculus, Trigonometry
                    </p>
                    <Button className="w-full" variant="outline">
                      Select Agent
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-hover">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-primary" />
                    Inventory Manager
                  </CardTitle>
                  <CardDescription>Inventory management agent</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Badge variant="secondary">Inactive</Badge>
                    <p className="text-sm text-muted-foreground">
                      Capabilities: Stock tracking, Order management
                    </p>
                    <Button className="w-full" variant="outline" disabled>
                      Coming Soon
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card className="card-hover">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-primary" />
                    Social Media Agent
                  </CardTitle>
                  <CardDescription>Social media automation agent</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Badge variant="secondary">Inactive</Badge>
                    <p className="text-sm text-muted-foreground">
                      Capabilities: Content creation, Scheduling
                    </p>
                    <Button className="w-full" variant="outline" disabled>
                      Coming Soon
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="tasks" className="space-y-6">
            <Card>
              <CardContent className="p-6 text-center">
                <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No tasks yet</h3>
                <p className="text-muted-foreground">
                  Submit a task to see it appear here
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ontology" className="space-y-6">
            <Card>
              <CardContent className="p-6 text-center">
                <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">Ontology Management</h3>
                <p className="text-muted-foreground">
                  Manage values and beliefs that guide agent behavior
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="submit" className="space-y-6">
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
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Task Type</label>
                  <select className="w-full p-2 border rounded-md">
                    <option>Math Problem</option>
                    <option>Inventory Management</option>
                    <option>Social Media</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Problem Description</label>
                  <textarea 
                    className="w-full p-2 border rounded-md min-h-[120px]"
                    placeholder="Describe the problem or task you want to solve..."
                  />
                </div>
                <Button className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Submit Task
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
