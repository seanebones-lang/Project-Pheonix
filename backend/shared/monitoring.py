"""
Monitoring and observability configuration for Mothership AIs.
"""

import os
import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import structlog

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
class Metrics:
    """Prometheus metrics for monitoring."""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_count = Counter(
            'mothership_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'mothership_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Agent metrics
        self.active_agents = Gauge(
            'mothership_active_agents',
            'Number of active agents',
            ['agent_type'],
            registry=self.registry
        )
        
        self.agent_heartbeats = Counter(
            'mothership_agent_heartbeats_total',
            'Total agent heartbeats',
            ['agent_id', 'agent_type'],
            registry=self.registry
        )
        
        # Task metrics
        self.tasks_total = Counter(
            'mothership_tasks_total',
            'Total number of tasks',
            ['task_type', 'status'],
            registry=self.registry
        )
        
        self.task_duration = Histogram(
            'mothership_task_duration_seconds',
            'Task processing duration in seconds',
            ['task_type'],
            registry=self.registry
        )
        
        # Ontology metrics
        self.ontology_size = Gauge(
            'mothership_ontology_size',
            'Size of the ontology',
            ['type'],
            registry=self.registry
        )
        
        # AI provider metrics
        self.ai_requests = Counter(
            'mothership_ai_requests_total',
            'Total AI provider requests',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.ai_request_duration = Histogram(
            'mothership_ai_request_duration_seconds',
            'AI provider request duration',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # WebSocket metrics
        self.websocket_connections = Gauge(
            'mothership_websocket_connections',
            'Number of active WebSocket connections',
            ['connection_type'],
            registry=self.registry
        )
        
        self.websocket_messages = Counter(
            'mothership_websocket_messages_total',
            'Total WebSocket messages',
            ['message_type', 'direction'],
            registry=self.registry
        )
    
    def start_metrics_server(self, port: int = 8001):
        """Start Prometheus metrics server."""
        try:
            start_http_server(port, registry=self.registry)
            logger.info("Prometheus metrics server started", port=port)
        except Exception as e:
            logger.error("Failed to start metrics server", error=str(e))
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.request_count.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_agent_heartbeat(self, agent_id: str, agent_type: str):
        """Record agent heartbeat."""
        self.agent_heartbeats.labels(agent_id=agent_id, agent_type=agent_type).inc()
    
    def update_active_agents(self, agent_type: str, count: int):
        """Update active agents count."""
        self.active_agents.labels(agent_type=agent_type).set(count)
    
    def record_task(self, task_type: str, status: str, duration: Optional[float] = None):
        """Record task metrics."""
        self.tasks_total.labels(task_type=task_type, status=status).inc()
        if duration is not None:
            self.task_duration.labels(task_type=task_type).observe(duration)
    
    def update_ontology_size(self, ontology_type: str, size: int):
        """Update ontology size."""
        self.ontology_size.labels(type=ontology_type).set(size)
    
    def record_ai_request(self, provider: str, model: str, duration: float):
        """Record AI provider request."""
        self.ai_requests.labels(provider=provider, model=model).inc()
        self.ai_request_duration.labels(provider=provider, model=model).observe(duration)
    
    def update_websocket_connections(self, connection_type: str, count: int):
        """Update WebSocket connections count."""
        self.websocket_connections.labels(connection_type=connection_type).set(count)
    
    def record_websocket_message(self, message_type: str, direction: str):
        """Record WebSocket message."""
        self.websocket_messages.labels(message_type=message_type, direction=direction).inc()

# OpenTelemetry tracing
class Tracing:
    """OpenTelemetry tracing configuration."""
    
    def __init__(self):
        self.tracer = None
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing."""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": "mothership-ais",
                "service.version": "1.0.0",
                "deployment.environment": os.getenv("ENVIRONMENT", "development")
            })
            
            # Create tracer provider
            tracer_provider = TracerProvider(resource=resource)
            
            # Add OTLP exporter if configured
            otlp_endpoint = os.getenv("OTLP_ENDPOINT")
            if otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                span_processor = BatchSpanProcessor(otlp_exporter)
                tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)
            
            logger.info("OpenTelemetry tracing configured")
            
        except Exception as e:
            logger.error("Failed to setup tracing", error=str(e))
    
    def get_tracer(self):
        """Get tracer instance."""
        return self.tracer
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI app."""
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumented for tracing")
        except Exception as e:
            logger.error("Failed to instrument FastAPI", error=str(e))
    
    def instrument_sqlalchemy(self):
        """Instrument SQLAlchemy."""
        try:
            SQLAlchemyInstrumentor().instrument()
            logger.info("SQLAlchemy instrumented for tracing")
        except Exception as e:
            logger.error("Failed to instrument SQLAlchemy", error=str(e))
    
    def instrument_requests(self):
        """Instrument requests library."""
        try:
            RequestsInstrumentor().instrument()
            logger.info("Requests library instrumented for tracing")
        except Exception as e:
            logger.error("Failed to instrument requests", error=str(e))

# Health check utilities
class HealthChecker:
    """Health check utilities."""
    
    def __init__(self):
        self.checks = {}
    
    def add_check(self, name: str, check_func):
        """Add a health check."""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                duration = time.time() - start_time
                
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration_ms": round(duration * 1000, 2),
                    "timestamp": time.time()
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": time.time()
                }
        
        return results
    
    def get_overall_status(self, results: Dict[str, Any]) -> str:
        """Get overall health status."""
        if not results:
            return "unknown"
        
        statuses = [result["status"] for result in results.values()]
        
        if "error" in statuses:
            return "error"
        elif "unhealthy" in statuses:
            return "unhealthy"
        else:
            return "healthy"

# Global instances
metrics = Metrics()
tracing = Tracing()
health_checker = HealthChecker()

# Initialize monitoring
def initialize_monitoring(app=None):
    """Initialize monitoring components."""
    try:
        # Start metrics server
        metrics_port = int(os.getenv("METRICS_PORT", "8001"))
        metrics.start_metrics_server(metrics_port)
        
        # Setup tracing
        if app:
            tracing.instrument_fastapi(app)
        tracing.instrument_sqlalchemy()
        tracing.instrument_requests()
        
        # Add default health checks
        health_checker.add_check("database", lambda: True)  # Placeholder
        health_checker.add_check("redis", lambda: True)     # Placeholder
        health_checker.add_check("ai_providers", lambda: True)  # Placeholder
        
        logger.info("Monitoring initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize monitoring", error=str(e))

# Decorators for easy metrics collection
def track_request(func):
    """Decorator to track request metrics."""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Extract method and endpoint from request if available
            method = "unknown"
            endpoint = "unknown"
            
            if args and hasattr(args[0], 'method'):
                method = args[0].method
            if args and hasattr(args[0], 'url'):
                endpoint = str(args[0].url.path)
            
            metrics.record_request(method, endpoint, 200, duration)
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_request("unknown", "unknown", 500, duration)
            raise
    
    return wrapper

def track_task(task_type: str):
    """Decorator to track task metrics."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.record_task(task_type, "completed", duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_task(task_type, "failed", duration)
                raise
        return wrapper
    return decorator
