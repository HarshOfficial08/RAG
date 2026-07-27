# Deployment (Local / Docker Compose)

## Depends on
All modules — this is the assembly point.

## `docker-compose.yml` services
```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]

  backend:
    build: ./backend
    env_file: .env
    depends_on: [qdrant]
    ports: ["8000:8000"]
    volumes: ["doc_storage:/data/documents"]

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

volumes:
  qdrant_data:
  doc_storage:
```

## `.env` (prototype scope — see `06-auth.md` for why a full secrets manager isn't
built here)
```
JWT_SECRET=change-me
OLLAMA_API_KEY=...
QDRANT_URL=http://qdrant:6333
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
```

## Run instructions (goes in root README, per `11-documentation-standards.md`)
```
cp .env.example .env   # fill in OLLAMA_API_KEY
docker compose up --build
# seed demo tenants/documents
docker compose exec backend python -m app.scripts.seed_demo_data
```

## Production-hardening notes (documented, not built — keep scope honest)
- Object storage: swap local volume for SeaweedFS/Garage (S3-compatible) behind the
  same file-storage interface.
- Secrets: HashiCorp Vault instead of `.env`.
- Auth: Keycloak instead of the hand-rolled JWT issuer.
- Multiple backend replicas behind a load balancer (stateless FastAPI already supports
  this, per `01-architecture.md` scalability notes).

## Definition of done
- `docker compose up --build` from a clean clone gets a working app with no manual
  steps beyond filling in `.env`.
