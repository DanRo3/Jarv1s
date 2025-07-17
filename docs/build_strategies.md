# Build Strategies and Development Workflows - Jarv1s

## Overview

This document outlines the different build strategies and development workflows available for Jarv1s, optimized for bandwidth efficiency and development speed.

## Build Strategies Comparison

| Strategy | Use Case | Bandwidth | Speed | Hot Reload |
|----------|----------|-----------|-------|------------|
| **Fast Development** | Daily development | Low | Very Fast | ✅ |
| **Clean Rebuild** | Major changes | High | Slow | ✅ |
| **Local Development** | Debugging | Minimal | Fast | ✅ |
| **Production Build** | Deployment | Medium | Medium | ❌ |

## 1. Fast Development Build

### Purpose
Optimized for daily development with minimal bandwidth usage and maximum speed.

### Command
```bash
./scripts/dev-fast.sh
```

### How it Works
1. **Dependency Caching**: Checks SHA256 hashes of `pyproject.toml` and `requirements.txt`
2. **Image Reuse**: Only rebuilds if dependencies changed
3. **Volume Mounting**: Code changes reflect immediately without rebuild
4. **Persistent Models**: TTS models stored in named volumes

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Host Code     │    │  Container       │    │  Persistent     │
│   ./src/        │◄──►│  /app/src/       │    │  Volumes        │
│   ./tests/      │    │  /app/tests/     │    │  - Models       │
│   ./scripts/    │    │  /app/scripts/   │    │  - Node Modules │
└─────────────────┘    └──────────────────┘    │  - Ollama Data  │
                                               └─────────────────┘
```

### Bandwidth Usage
- **First run**: ~500MB (base images + models)
- **Code changes**: **0MB** (volumes only)
- **Dependency changes**: ~50MB (pip packages only)

### Performance Metrics
- **Cold start**: 2-3 minutes
- **Warm start**: 10-15 seconds
- **Code change reflection**: Instant

## 2. Clean Rebuild Strategy

### Purpose
Complete rebuild for major changes, dependency conflicts, or corrupted cache.

### Command
```bash
./scripts/rebuild-clean.sh
```

### Process
1. **Stop all containers**
2. **Remove all Jarv1s images**
3. **Clear dependency cache**
4. **Rebuild from scratch with --no-cache**
5. **Update dependency hashes**

### When to Use
- Major dependency updates
- Docker cache corruption
- Model updates
- After significant architecture changes
- Weekly maintenance

### Bandwidth Usage
- **Always**: ~500MB (full rebuild)

## 3. Local Development (No Containers)

### Purpose
Native development without containerization overhead.

### Command
```bash
./scripts/dev-local.sh
```

### Process
1. **Create/activate virtual environment**
2. **Install dependencies with pip**
3. **Download models if missing**
4. **Start development server**

### Advantages
- Fastest startup time
- Direct debugging access
- Lower resource usage
- Native IDE integration

### Requirements
- Python 3.11+
- FFmpeg installed
- LM Studio running locally

### Bandwidth Usage
- **First run**: ~100MB (Python packages + models)
- **Updates**: ~10-50MB (packages only)

## 4. Production Build Strategy

### Purpose
Optimized multi-stage build for production deployment.

### Dockerfile Structure
```dockerfile
# Stage 1: Base system dependencies
FROM python:3.11-slim as base
RUN apt-get update && apt-get install -y ffmpeg espeak-ng

# Stage 2: Model downloads (cached separately)
FROM base as models
RUN wget -q [model-urls] -O models/

# Stage 3: Python dependencies (cached separately)
FROM base as dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 4: Final application
FROM dependencies as final
COPY --from=models /app/models ./models
COPY src/ ./src/
```

### Benefits
- **Layer caching**: Each stage cached independently
- **Minimal rebuilds**: Only changed layers rebuild
- **Optimized size**: Multi-stage reduces final image size

## Development Workflows

### Daily Development Workflow

```bash
# Morning startup (or after git pull)
./scripts/dev-fast.sh

# Development cycle
# 1. Edit code in ./src/
# 2. Changes reflect automatically
# 3. Test in browser: http://localhost:5173

# View logs if needed
podman logs -f jarvis-backend-dev

# Stop when done
podman stop jarvis-backend-dev jarvis-frontend-dev
```

### Weekly Maintenance Workflow

```bash
# Clean rebuild (weekly or after major changes)
./scripts/rebuild-clean.sh

# Resume fast development
./scripts/dev-fast.sh
```

### Debugging Workflow

```bash
# Switch to local development for debugging
podman stop jarvis-backend-dev  # Stop container if running
./scripts/dev-local.sh          # Start local development

# Debug with IDE, add breakpoints, etc.
# When done, switch back to containers
./scripts/dev-fast.sh
```

## Container Architecture

### Network Configuration
```yaml
networks:
  jarvis-dev-network:
    driver: bridge
```

### Service Communication
```
Frontend (5173) ──HTTP──► Backend (8000) ──HTTP──► LM Studio (1234)
     │                        │                        │
     └── Volume Mount ────────┼── Volume Mount ────────┘
         ./frontend/src       ./src/                Ollama Data
```

### Volume Strategy
```yaml
volumes:
  # Persistent across rebuilds
  jarvis-models:        # TTS models (~100MB)
  jarvis-ollama-data:   # LLM models (~1-4GB)
  jarvis-node-modules:  # NPM packages (~200MB)
  
  # Development mounts (live sync)
  ./src:/app/src:Z                    # Backend code
  ./frontend/src:/app/src:Z           # Frontend code
  ./.env:/app/.env:Z                  # Configuration
```

## Optimization Techniques

### 1. Dependency Caching
```bash
# Hash-based cache invalidation
sha256sum pyproject.toml requirements.txt > .dev-cache/backend-deps.hash

# Only rebuild if hash changed
if ! sha256sum -c .dev-cache/backend-deps.hash; then
    rebuild_backend
fi
```

### 2. Layer Optimization
```dockerfile
# Dependencies first (changes less frequently)
COPY pyproject.toml requirements.txt ./
RUN pip install -r requirements.txt

# Code last (changes frequently)
COPY src/ ./src/
```

### 3. Volume Persistence
```bash
# Named volumes persist across container recreation
-v jarvis-models:/app/models        # Models don't re-download
-v jarvis-node-modules:/app/node_modules  # NPM packages persist
```

## Troubleshooting

### Common Issues and Solutions

#### "Image not found" Error
```bash
# Solution: Run clean rebuild
./scripts/rebuild-clean.sh
```

#### "Port already in use" Error
```bash
# Solution: Stop existing containers
podman stop $(podman ps -q --filter "name=jarvis")
```

#### "Permission denied" on volumes
```bash
# Solution: Add :Z flag for SELinux
-v ./src:/app/src:Z
```

#### "Models not downloading"
```bash
# Solution: Check internet connection and run
podman volume rm jarvis-models
./scripts/rebuild-clean.sh
```

### Performance Monitoring

#### Check Container Resource Usage
```bash
# CPU and memory usage
podman stats jarvis-backend-dev

# Disk usage
podman system df
```

#### Check Build Cache Efficiency
```bash
# View layer cache
podman history jarvis-backend-dev

# Check volume sizes
podman volume ls --format "table {{.Name}}\t{{.Size}}"
```

## Best Practices

### Development
1. **Use fast development** for daily work
2. **Mount only necessary directories** as volumes
3. **Keep .env file updated** with local settings
4. **Monitor resource usage** regularly

### Maintenance
1. **Clean rebuild weekly** or after major changes
2. **Prune unused images** regularly: `podman image prune`
3. **Backup important volumes** before major changes
4. **Update base images** monthly

### Performance
1. **Use SSD storage** for better I/O performance
2. **Allocate sufficient RAM** (8GB+ recommended)
3. **Close unused containers** to free resources
4. **Monitor bandwidth usage** on metered connections

## Scripts Reference

### Available Scripts

| Script | Purpose | Bandwidth | Time |
|--------|---------|-----------|------|
| `dev-fast.sh` | Daily development | 0-50MB | 10s-2m |
| `rebuild-clean.sh` | Clean rebuild | 500MB | 5-10m |
| `dev-local.sh` | Local development | 0-100MB | 30s-2m |
| `podman-dev.sh` | Full stack with compose | 500MB | 5-10m |

### Script Locations
```
scripts/
├── dev-fast.sh          # Fast development
├── rebuild-clean.sh     # Clean rebuild
├── dev-local.sh         # Local development
├── podman-dev.sh        # Full stack
└── setup.py             # Initial setup
```

This build strategy documentation ensures efficient development while minimizing bandwidth usage and maximizing developer productivity.