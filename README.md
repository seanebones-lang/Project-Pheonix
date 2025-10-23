# Mothership AIs - Proprietary Software

## ⚠️ PROPRIETARY SOFTWARE NOTICE

**This software is proprietary and confidential to Sean McDonnell. All rights reserved.**

This repository contains proprietary software developed by Sean McDonnell. The software, documentation, and all associated materials are protected by copyright laws and international treaties.

## License Information

This software is licensed under a proprietary license. See [LICENSE](LICENSE) for complete terms and conditions.

## Commercial Use

For commercial licensing, partnership opportunities, or enterprise use, please contact:

**Sean McDonnell**  
Email: sean@mothership-ais.com  
Website: https://mothership-ais.com

## What is Mothership AIs?

Mothership AIs is a cloud-native AI system where a central AI (Mothership) with an ontological library of values and beliefs generates directives for specialized AI agents to perform tasks like inventory management, social media automation, or math homework assistance.

### Key Features

- **Ontological AI**: Central AI with values and beliefs library
- **Specialized Agents**: Math, inventory, social media, and general-purpose agents
- **Real-time Communication**: WebSocket-based agent coordination
- **Cloud-Native**: Kubernetes deployment with auto-scaling
- **Modern Stack**: FastAPI, Next.js 14, PostgreSQL with pgvector
- **Production Ready**: Monitoring, security, and DevOps best practices

### Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy 2.0, Langchain
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, TanStack Query
- **Infrastructure**: Kubernetes, Helm, Docker, PostgreSQL, Redis
- **AI**: OpenAI, Claude, Gemini APIs with fallback support
- **Monitoring**: Prometheus, Grafana, OpenTelemetry

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (minikube, kind, or cloud)
- kubectl and helm installed
- OpenAI API key and Claude API key

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/seanebones-lang/Project-Pheonix.git
   cd Project-Pheonix
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Deployment

```bash
./deploy.sh deploy
```

## Architecture

The system uses a microservices architecture with:

- **Mothership Core**: Ontology management and directive generation
- **Agent Framework**: Base classes for specialized AI agents
- **WebSocket Communication**: Real-time agent coordination
- **Vector Database**: PostgreSQL with pgvector for semantic search
- **Monitoring Stack**: Prometheus, Grafana, and OpenTelemetry

## Security

- JWT authentication with refresh tokens
- API rate limiting per user/agent
- Input validation and sanitization
- Network policies in Kubernetes
- Secrets management with Kubernetes secrets

## Contributing

This is proprietary software. Contributions are by invitation only. For partnership opportunities or commercial licensing, please contact Sean McDonnell.

## Support

For technical support, licensing inquiries, or partnership opportunities:

**Sean McDonnell**  
Email: sean@mothership-ais.com  
Website: https://mothership-ais.com

---

**© 2025 Sean McDonnell. All rights reserved. This software is proprietary and confidential.**