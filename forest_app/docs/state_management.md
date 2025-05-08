# State Management in Forest

## Overview

Forest uses a request-scoped state management approach to ensure thread safety and prevent state bleed between concurrent requests. This document outlines the key components and patterns used for state management.

## Key Components

### 1. MemorySnapshot

The `MemorySnapshot` class serves as the primary container for user journey state. It includes:
- Feature flags
- Component states
- Task backlog
- Withering level
- Current path
- Other session-specific data

Each request gets its own instance of `MemorySnapshot`, ensuring isolation between concurrent users.

### 2. ForestOrchestrator

The `ForestOrchestrator` is instantiated per request using a `Factory` provider in the DI container. This ensures that:
- Each request gets a fresh orchestrator instance
- No state is shared between concurrent requests
- All state transitions are isolated to the current request

### 3. ComponentStateManager

The `ComponentStateManager` handles loading and saving component states within a snapshot. It:
- Manages state for various application components
- Ensures proper serialization/deserialization
- Maintains state isolation through the snapshot

### 4. WitheringManager

The `WitheringManager` is a pure functional class that:
- Calculates withering levels based on user activity
- Has no internal state
- Takes a snapshot as input and updates it in place
- Uses coefficients specific to different user paths

## State Isolation Patterns

### 1. Request Scoping

All stateful components are scoped to individual requests:
```python
@inject
def get_orchestrator(container: Container) -> ForestOrchestrator:
    return container.orchestrator()  # Returns a fresh instance per request
```

### 2. Pure Functions

Where possible, we use pure functions that:
- Take all required state as parameters
- Return new state rather than modifying existing state
- Have no side effects
- Are easily testable

### 3. Immutable State

We prefer immutable state patterns where:
- State changes create new instances rather than modifying existing ones
- State transitions are explicit and traceable
- Side effects are minimized

## Testing State Isolation

We have comprehensive tests that verify:
- Orchestrator instances are isolated between requests
- No shared state exists between concurrent users
- State transitions are properly contained
- Withering calculations are accurate and isolated

## Best Practices

1. Always use the DI container to get fresh instances of stateful components
2. Keep state in the `MemorySnapshot` rather than component instances
3. Use pure functions for state transformations
4. Write tests that verify state isolation
5. Document state dependencies and transitions
6. Use type hints to make state requirements explicit

## Common Pitfalls

1. Storing state in class attributes instead of the snapshot
2. Using global variables or singletons for state
3. Modifying state outside of the orchestrator
4. Not properly scoping stateful components
5. Mixing concerns between state management and business logic 