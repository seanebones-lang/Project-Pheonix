-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create values table for ontological values
CREATE TABLE IF NOT EXISTS values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create beliefs table for ontological beliefs
CREATE TABLE IF NOT EXISTS beliefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    embedding vector(1536),
    related_values UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create directives table for generated directives
CREATE TABLE IF NOT EXISTS directives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(255) NOT NULL,
    constraints JSONB NOT NULL DEFAULT '{}',
    source_values UUID[] DEFAULT '{}',
    source_beliefs UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create agents table for agent registry
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    agent_type VARCHAR(255) NOT NULL,
    capabilities JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'inactive',
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table for task tracking
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    agent_id UUID REFERENCES agents(id),
    directive_id UUID REFERENCES directives(id),
    input_data JSONB NOT NULL,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_values_embedding ON values USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_beliefs_embedding ON beliefs USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_directives_task_type ON directives(task_type);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_agent_id ON tasks(agent_id);

-- Insert initial ontological values
INSERT INTO values (name, description) VALUES
('Fairness', 'Ensure equitable resource allocation and treatment'),
('Efficiency', 'Minimize resource waste and optimize performance'),
('Transparency', 'Provide clear explanations and open communication'),
('Accuracy', 'Ensure correctness and precision in all outputs'),
('Privacy', 'Protect user data and maintain confidentiality'),
('Safety', 'Prevent harm and ensure secure operations'),
('Innovation', 'Encourage creative problem-solving approaches'),
('Reliability', 'Maintain consistent and dependable performance')
ON CONFLICT (name) DO NOTHING;

-- Insert initial ontological beliefs
INSERT INTO beliefs (name, description, related_values) VALUES
('Clear Explanations', 'Provide step-by-step solutions for educational tasks', 
 ARRAY[(SELECT id FROM values WHERE name = 'Transparency'), (SELECT id FROM values WHERE name = 'Accuracy')]),
('Minimize Data Usage', 'Use only necessary data to protect privacy', 
 ARRAY[(SELECT id FROM values WHERE name = 'Privacy'), (SELECT id FROM values WHERE name = 'Efficiency')]),
('Error Prevention', 'Implement safeguards to prevent mistakes', 
 ARRAY[(SELECT id FROM values WHERE name = 'Safety'), (SELECT id FROM values WHERE name = 'Reliability')]),
('Resource Optimization', 'Optimize computational resources for efficiency', 
 ARRAY[(SELECT id FROM values WHERE name = 'Efficiency'), (SELECT id FROM values WHERE name = 'Innovation')]),
('User-Centric Design', 'Prioritize user needs and experience', 
 ARRAY[(SELECT id FROM values WHERE name = 'Fairness'), (SELECT id FROM values WHERE name = 'Transparency')])
ON CONFLICT (name) DO NOTHING;
