import { 
  Agent, 
  Task, 
  Directive, 
  Value, 
  Belief, 
  OntologySummary,
  CreateTask,
  CreateDirective,
  CreateValue,
  CreateBelief
} from './schemas'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // Agent endpoints
  async getAgents(agentType?: string): Promise<Agent[]> {
    const params = agentType ? `?agent_type=${agentType}` : ''
    return this.request<Agent[]>(`/api/agents${params}`)
  }

  async getAgent(agentId: string): Promise<Agent> {
    return this.request<Agent>(`/api/agents/${agentId}`)
  }

  // Task endpoints
  async getTasks(): Promise<Task[]> {
    return this.request<Task[]>('/api/tasks')
  }

  async getTask(taskId: string): Promise<Task> {
    return this.request<Task>(`/api/tasks/${taskId}`)
  }

  async getRecentTasks(limit: number = 10): Promise<Task[]> {
    return this.request<Task[]>(`/api/tasks/recent?limit=${limit}`)
  }

  async createTask(taskData: CreateTask): Promise<Task> {
    return this.request<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    })
  }

  // Directive endpoints
  async getDirective(directiveId: string): Promise<Directive> {
    return this.request<Directive>(`/api/directives/${directiveId}`)
  }

  async createDirective(
    taskDescription: string,
    taskType: string,
    userContext?: Record<string, any>
  ): Promise<Directive> {
    return this.request<Directive>('/api/directives', {
      method: 'POST',
      body: JSON.stringify({
        task_description: taskDescription,
        task_type: taskType,
        user_context: userContext,
      }),
    })
  }

  // Ontology endpoints
  async getValues(limit: number = 100, offset: number = 0): Promise<Value[]> {
    return this.request<Value[]>(`/api/ontology/values?limit=${limit}&offset=${offset}`)
  }

  async getBeliefs(limit: number = 100, offset: number = 0): Promise<Belief[]> {
    return this.request<Belief[]>(`/api/ontology/beliefs?limit=${limit}&offset=${offset}`)
  }

  async createValue(valueData: CreateValue): Promise<Value> {
    return this.request<Value>('/api/ontology/values', {
      method: 'POST',
      body: JSON.stringify(valueData),
    })
  }

  async createBelief(beliefData: CreateBelief): Promise<Belief> {
    return this.request<Belief>('/api/ontology/beliefs', {
      method: 'POST',
      body: JSON.stringify(beliefData),
    })
  }

  async getOntologySummary(): Promise<OntologySummary> {
    return this.request<OntologySummary>('/api/ontology/summary')
  }

  // Authentication endpoints
  async login(username: string, password: string): Promise<any> {
    return this.request<any>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  async logout(sessionToken: string): Promise<any> {
    return this.request<any>('/api/auth/logout', {
      method: 'POST',
      body: JSON.stringify({ session_token: sessionToken }),
    })
  }

  async validateSession(sessionToken: string): Promise<any> {
    return this.request<any>('/api/auth/validate', {
      method: 'POST',
      body: JSON.stringify({ session_token: sessionToken }),
    })
  }

  async getSecurityStatus(): Promise<any> {
    return this.request<any>('/api/auth/security-status')
  }

  async getAuditLog(limit: number = 100): Promise<any> {
    return this.request<any>(`/api/auth/audit-log?limit=${limit}`)
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request<{ status: string; service: string }>('/health')
  }

  async readinessCheck(): Promise<{ status: string; service: string }> {
    return this.request<{ status: string; service: string }>('/ready')
  }
}

export const apiClient = new ApiClient()
