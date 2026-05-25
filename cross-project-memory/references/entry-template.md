# Shared Memory Entry Template

## When to Save

Save a knowledge entry when you:
- Solve a tricky bug with a non-obvious solution
- Make an architectural decision with trade-offs
- Discover a useful pattern, library, or configuration
- Figure out environment-specific setup steps
- Learn something that would be useful in future projects

## Entry Format

Each entry is a Markdown file with YAML frontmatter.

### Frontmatter Fields

| Field    | Description                                      | Example                      |
|----------|--------------------------------------------------|------------------------------|
| date     | ISO date when saved                              | 2026-05-26                   |
| project  | Source project path                              | /Users/me/projects/my-api    |
| tags     | Searchable keywords (JSON array)                 | ["docker","compose","devops"]|
| category | Broad classification                             | devops / frontend / backend / database / api / testing / general |
| title    | Short descriptive title (quoted)                 | "Docker Compose multi-service setup" |

### Body

Write in natural language. Include:
1. **Context** - What were you doing?
2. **Problem/Solution** - What did you figure out?
3. **Key Takeaways** - The reusable insight
4. **Code/Config snippets** if applicable

### Example Entry

```markdown
---
date: 2026-05-26
project: /Users/me/projects/ecommerce-api
tags: ["docker","compose","postgres","redis","devops"]
category: devops
title: "Docker Compose with Postgres + Redis health checks"
---

## Context
Setting up local dev environment for the ecommerce API microservices.

## Solution
Used `depends_on` with `condition: service_healthy` in docker-compose.yml
to ensure Postgres and Redis are ready before the API starts.

## Key Takeaways
- Always add healthcheck blocks for database services
- Use `pg_isready` for Postgres and `redis-cli ping` for Redis
- The `depends_on` with condition prevents race conditions on startup
- Set `POSTGRES_HOST_AUTH_METHOD=trust` only for local dev, never production

## Code
```yaml
services:
  postgres:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 5s
      retries: 5
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
  api:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```
```
