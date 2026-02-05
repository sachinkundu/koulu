---
name: observability
description: Implement OpenTelemetry tracing and structured logging for distributed systems
---

# Skill: Observability

## Core Principles
- **Structured Logging**: JSON in production
- **Distributed Tracing**: W3C Trace Context propagation
- **Correlation**: Logs include `trace_id` and `span_id`

---

## Distributed Tracing (OpenTelemetry)

### Setup
```python
# Python - auto-instrumentation preferred
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
FastAPIInstrumentor.instrument()

# Manual spans for critical logic
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_payment")
def process_payment(order_id: str) -> None:
    ...
```

```typescript
// Frontend - initialize at entry point
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';

// Ensure traceparent header injected into all API calls
```

### Propagation
- Header: `traceparent` (W3C standard)
- Frontend MUST generate initial trace and propagate to backend

---

## Logging

### Python (structlog)
```python
import structlog

# Configure once at startup
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        # Add trace context
        structlog.processors.JSONRenderer(),  # production
    ],
)

logger = structlog.get_logger()
logger.info("order_placed", order_id="123", total=99.99)
```

### Output Format (Production)
```json
{
  "timestamp": "2025-02-05T12:00:00Z",
  "level": "info",
  "message": "order_placed",
  "order_id": "123",
  "trace_id": "abc123",
  "span_id": "def456",
  "service": "koulu-api"
}
```

### Log Levels
| Level | Use |
|-------|-----|
| DEBUG | Granular diagnostics (variables, steps) |
| INFO | Milestones (startup, request received, job done) |
| WARN | Handled unexpected events (retries, fallbacks) |
| ERROR | Exceptions requiring attention |

---

## Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Write to stdout | Write to files |
| Include trace context | Log without correlation |
| Structured JSON (prod) | Unstructured strings |
| Mask sensitive data | Log PII, tokens, passwords |

---

## Local Development
- Run Jaeger locally to view traces
- Use colorful/human-readable formatters for stdout
