'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Bot, 
  Activity, 
  CheckCircle, 
  XCircle, 
  Clock,
  Zap,
  Shield,
  Brain
} from 'lucide-react'
import { Agent } from '@/lib/schemas'

interface AgentCardProps {
  agent: Agent
  isSelected: boolean
  onSelect: () => void
}

export function AgentCard({ agent, isSelected, onSelect }: AgentCardProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'inactive':
        return <Clock className="h-4 w-4 text-gray-500" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'maintenance':
        return <Activity className="h-4 w-4 text-yellow-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500'
      case 'inactive':
        return 'bg-gray-500'
      case 'error':
        return 'bg-red-500'
      case 'maintenance':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-500'
    }
  }

  const formatLastHeartbeat = (heartbeat: string | null) => {
    if (!heartbeat) return 'Never'
    
    const date = new Date(heartbeat)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  const getCapabilityIcons = (capabilities: Record<string, any>) => {
    const icons = []
    
    if (capabilities.algebra) icons.push(<Calculator className="h-3 w-3" />)
    if (capabilities.calculus) icons.push(<Zap className="h-3 w-3" />)
    if (capabilities.trigonometry) icons.push(<Brain className="h-3 w-3" />)
    if (capabilities.statistics) icons.push(<Shield className="h-3 w-3" />)
    
    return icons
  }

  return (
    <Card 
      className={`card-hover cursor-pointer transition-all duration-200 ${
        isSelected ? 'ring-2 ring-primary shadow-lg' : ''
      }`}
      onClick={onSelect}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{agent.name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(agent.status)}
            <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
          </div>
        </div>
        <CardDescription className="flex items-center gap-2">
          <Badge variant="outline">{agent.agent_type}</Badge>
          <span className="text-xs text-muted-foreground">
            {formatLastHeartbeat(agent.last_heartbeat)}
          </span>
        </CardDescription>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Capabilities */}
          <div>
            <h4 className="text-sm font-medium mb-2">Capabilities</h4>
            <div className="flex flex-wrap gap-1">
              {Object.keys(agent.capabilities).slice(0, 4).map((capability) => (
                <Badge key={capability} variant="secondary" className="text-xs">
                  {capability}
                </Badge>
              ))}
              {Object.keys(agent.capabilities).length > 4 && (
                <Badge variant="secondary" className="text-xs">
                  +{Object.keys(agent.capabilities).length - 4} more
                </Badge>
              )}
            </div>
          </div>

          {/* Capability Icons */}
          {Object.keys(agent.capabilities).length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Features:</span>
              <div className="flex gap-1">
                {getCapabilityIcons(agent.capabilities)}
              </div>
            </div>
          )}

          {/* Agent Info */}
          <div className="text-xs text-muted-foreground space-y-1">
            <div>Created: {new Date(agent.created_at).toLocaleDateString()}</div>
            <div>Updated: {new Date(agent.updated_at).toLocaleDateString()}</div>
          </div>

          {/* Action Button */}
          <Button 
            variant={isSelected ? "default" : "outline"} 
            size="sm" 
            className="w-full"
            onClick={(e) => {
              e.stopPropagation()
              onSelect()
            }}
          >
            {isSelected ? 'Selected' : 'Select Agent'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
