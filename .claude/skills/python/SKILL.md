---
name: python
description: Follow Python backend development standards with FastAPI and strict typing
---

# Skill: Python Backend Development

## Type Safety (Non-Negotiable)

```python
# ✅ Every function must have full annotations
def create_user(email: str, name: str) -> User:
    ...

# ✅ Modern syntax (Python 3.10+)
def process(items: list[str]) -> dict[str, int]:
    ...

def maybe_value() -> str | None:  # Not Optional[str]
    ...

# ❌ FORBIDDEN: typing.Any
# ❌ FORBIDDEN: bare except or except Exception
```

---

## Style (PEP 8)

- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Google-style docstrings on all public APIs

---

## Data Modeling

```python
# Prefer dataclasses or Pydantic over raw dicts
from dataclasses import dataclass

@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise InvalidEmailError(self.value)
```

Use Pydantic at system boundaries (API inputs, config).

---

## Code Quality

- Early returns (guard clauses) to reduce nesting
- Specific exceptions, not generic
- Named constants, not magic numbers
- `pathlib` over `os.path`
- f-strings for formatting
- `enum.StrEnum` for categorical options

---

## Observability

```python
# Structured logging with structlog (MANDATORY)
import structlog
logger = structlog.get_logger()

# Include trace context
logger.info("user_login", user_id=123, status="success")

# OpenTelemetry for tracing
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id: str) -> None:
    ...
```

**Logging rules:**
- JSON output in production
- stdout only—NEVER write to files
- NEVER log PII, tokens, or passwords

---

## Verification

Run before completing any Python task:

```bash
./scripts/verify.sh
```

**Must pass:**
1. `ruff check .` (linting)
2. `ruff format --check .` (formatting)
3. `mypy .` (type checking)
4. `pytest` with >80% coverage

Fix issues with:
```bash
ruff check --fix .
ruff format .
```

Only mark done when script prints "All Checks Passed!"
