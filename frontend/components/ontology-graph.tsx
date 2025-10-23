'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Brain, 
  Target, 
  Shield, 
  Zap, 
  Network,
  Plus,
  Search
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { Value, Belief } from '@/lib/schemas'

export function OntologyGraph() {
  const { data: values = [], isLoading: valuesLoading } = useQuery({
    queryKey: ['ontology', 'values'],
    queryFn: () => apiClient.getValues(50),
  })

  const { data: beliefs = [], isLoading: beliefsLoading } = useQuery({
    queryKey: ['ontology', 'beliefs'],
    queryFn: () => apiClient.getBeliefs(50),
  })

  const { data: summary } = useQuery({
    queryKey: ['ontology', 'summary'],
    queryFn: () => apiClient.getOntologySummary(),
  })

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Values</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary?.total_values || 0}</div>
            <p className="text-xs text-muted-foreground">
              Core ontological values
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Beliefs</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary?.total_beliefs || 0}</div>
            <p className="text-xs text-muted-foreground">
              Operational beliefs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary?.ontology_size || 0}</div>
            <p className="text-xs text-muted-foreground">
              Ontology elements
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Ontology Content */}
      <Tabs defaultValue="values" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="values">Values</TabsTrigger>
          <TabsTrigger value="beliefs">Beliefs</TabsTrigger>
        </TabsList>

        <TabsContent value="values" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Ontological Values</h3>
            <Button size="sm" variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Add Value
            </Button>
          </div>

          {valuesLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
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
              ))}
            </div>
          ) : values.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {values.map((value) => (
                <Card key={value.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-primary" />
                      <CardTitle className="text-base">{value.name}</CardTitle>
                    </div>
                    <CardDescription className="text-sm">
                      Created {new Date(value.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-muted-foreground">
                      {value.description}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No values found</h3>
                <p className="text-muted-foreground">
                  Add some ontological values to guide agent behavior
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="beliefs" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Operational Beliefs</h3>
            <Button size="sm" variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Add Belief
            </Button>
          </div>

          {beliefsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
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
              ))}
            </div>
          ) : beliefs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {beliefs.map((belief) => (
                <Card key={belief.id} className="card-hover">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-primary" />
                      <CardTitle className="text-base">{belief.name}</CardTitle>
                    </div>
                    <CardDescription className="text-sm">
                      Created {new Date(belief.created_at).toLocaleDateString()}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-muted-foreground mb-3">
                      {belief.description}
                    </p>
                    {belief.related_values.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-xs font-medium">Related Values:</span>
                        <div className="flex flex-wrap gap-1">
                          {belief.related_values.slice(0, 3).map((valueId) => (
                            <Badge key={valueId} variant="outline" className="text-xs">
                              {valueId.slice(0, 8)}...
                            </Badge>
                          ))}
                          {belief.related_values.length > 3 && (
                            <Badge variant="outline" className="text-xs">
                              +{belief.related_values.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-6 text-center">
                <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No beliefs found</h3>
                <p className="text-muted-foreground">
                  Add some operational beliefs to guide agent behavior
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
