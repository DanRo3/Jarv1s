# Git Workflow and Versioning Strategy - Jarv1s

## Overview

This document outlines the Git workflow, branching strategy, and versioning approach for the Jarv1s project. Following these guidelines ensures consistent development practices and maintainable code evolution.

## Branching Strategy

### Git Flow Simplified

We use a simplified Git Flow approach optimized for Jarv1s development:

```
main                    # Production-ready stable releases
├── develop            # Main development branch
├── feature/*          # New features and major changes
├── hotfix/*           # Critical bug fixes
└── release/*          # Release preparation
```

### Branch Types

#### **Main Branch**
- **Purpose**: Production-ready code
- **Protection**: Protected, requires PR reviews
- **Deployment**: Automatically deployed/tagged
- **Naming**: `main`

#### **Develop Branch**
- **Purpose**: Integration branch for features
- **Source**: Branched from `main`
- **Target**: Features merge here first
- **Naming**: `develop`

#### **Feature Branches**
- **Purpose**: New features, enhancements, major refactoring
- **Source**: Branched from `develop`
- **Target**: Merged back to `develop`
- **Naming**: `feature/description-of-feature`
- **Lifetime**: Short-lived (1-4 weeks)

#### **Release Branches**
- **Purpose**: Prepare releases, final testing, documentation
- **Source**: Branched from `develop`
- **Target**: Merged to both `main` and `develop`
- **Naming**: `release/v0.2.0`
- **Lifetime**: Short-lived (1-2 weeks)

#### **Hotfix Branches**
- **Purpose**: Critical bug fixes for production
- **Source**: Branched from `main`
- **Target**: Merged to both `main` and `develop`
- **Naming**: `hotfix/critical-bug-description`
- **Lifetime**: Very short-lived (hours to days)

## Semantic Versioning (SemVer)

### Version Format: MAJOR.MINOR.PATCH

```
v1.2.3
 │ │ │
 │ │ └── PATCH: Bug fixes, small improvements
 │ └──── MINOR: New features, backward compatible
 └────── MAJOR: Breaking changes, major rewrites
```

### Jarv1s Version Roadmap

```
v0.1.0 - Functional Prototype ✅
├── Basic voice conversation
├── STT + LLM + TTS pipeline
└── Web interface

v0.2.0 - Containerization & Cleanup ← CURRENT TARGET
├── Docker/Podman support
├── Code organization
├── Automated setup
└── Robust testing

v0.3.0 - Agent Framework Migration
├── Google ADK integration
├── Tool orchestration system
└── Plugin architecture

v0.4.0 - Essential Tools
├── Web search capability
├── PDF document processing
└── Calendar integration

v0.5.0 - Advanced Features
├── Multi-modal support
├── Performance optimizations
└── Enhanced UX

v1.0.0 - MVP Release
├── Complete tool ecosystem
├── Production-ready stability
├── Comprehensive documentation
└── Community features
```

### Version Increment Rules

#### **PATCH (0.1.1)**
- Bug fixes
- Performance improvements
- Documentation updates
- Dependency updates
- Small UI/UX improvements

#### **MINOR (0.2.0)**
- New features
- New tools/capabilities
- API additions (backward compatible)
- Significant improvements
- New configuration options

#### **MAJOR (1.0.0)**
- Breaking API changes
- Architecture rewrites
- Incompatible changes
- Major paradigm shifts

## Commit Message Convention

### Format: Conventional Commits

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(adk): integrate Google Agent Development Kit` |
| `fix` | Bug fix | `fix(whisper): resolve memory leak in STT service` |
| `docs` | Documentation | `docs(api): add endpoint documentation` |
| `style` | Code style/formatting | `style(services): apply black formatting` |
| `refactor` | Code refactoring | `refactor(services): reorganize service architecture` |
| `test` | Tests | `test(integration): add end-to-end conversation tests` |
| `chore` | Maintenance | `chore(docker): update base image to python:3.11` |
| `perf` | Performance | `perf(tts): optimize Piper TTS loading time` |
| `ci` | CI/CD | `ci(github): add automated testing workflow` |
| `build` | Build system | `build(docker): optimize container build process` |

### Scope Examples for Jarv1s

- `(stt)` - Speech-to-text related
- `(llm)` - Language model related  
- `(tts)` - Text-to-speech related
- `(api)` - Backend API changes
- `(ui)` - Frontend/UI changes
- `(docker)` - Containerization
- `(adk)` - Google ADK integration
- `(tools)` - Agent tools/plugins
- `(config)` - Configuration changes

## Workflow Commands

### Starting New Work

#### **1. Setup Development Environment**
```bash
# Clone and setup
git clone <repository-url>
cd jarv1s
git checkout develop

# Create feature branch
git checkout -b feature/your-feature-name
```

#### **2. Feature Development**
```bash
# Regular development cycle
git add .
git commit -m "feat(scope): add new functionality"
git push origin feature/your-feature-name

# Keep feature updated with develop
git checkout develop
git pull origin develop
git checkout feature/your-feature-name
git rebase develop
```

#### **3. Feature Completion**
```bash
# Final commits
git add .
git commit -m "feat(scope): complete feature implementation"
git push origin feature/your-feature-name

# Create Pull Request to develop
# After PR approval and merge:
git checkout develop
git pull origin develop
git branch -d feature/your-feature-name
```

### Release Process

#### **1. Prepare Release**
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v0.2.0

# Update version numbers, documentation
# Final testing and bug fixes
git commit -m "chore(release): prepare v0.2.0"
```

#### **2. Complete Release**
```bash
# Merge to main
git checkout main
git merge release/v0.2.0
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin main --tags

# Merge back to develop
git checkout develop
git merge release/v0.2.0
git push origin develop

# Clean up
git branch -d release/v0.2.0
```

### Hotfix Process

```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Fix the issue
git commit -m "fix(critical): resolve production bug"

# Merge to main
git checkout main
git merge hotfix/critical-bug-fix
git tag -a v0.1.1 -m "Hotfix version 0.1.1"
git push origin main --tags

# Merge to develop
git checkout develop
git merge hotfix/critical-bug-fix
git push origin develop

# Clean up
git branch -d hotfix/critical-bug-fix
```

## Branch Protection Rules

### Main Branch
- Require pull request reviews (1+ reviewers)
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to administrators only
- Require signed commits (recommended)

### Develop Branch
- Require pull request reviews (1+ reviewer)
- Require status checks to pass
- Allow force pushes for maintainers

## Development Phases and Branches

### Phase 1: Code Cleanup (Current)
```bash
feature/code-organization     # Restructure src/ directory
feature/automated-setup      # Installation scripts
feature/robust-testing       # Comprehensive test suite
feature/documentation        # Complete docs update
```

### Phase 2: ADK Migration
```bash
feature/adk-integration      # Google ADK implementation
feature/tool-interface       # Plugin system foundation
feature/agent-orchestration  # Decision-making logic
```

### Phase 3: Essential Tools
```bash
feature/web-search          # Local web search capability
feature/pdf-processor       # Document analysis
feature/calendar-integration # Basic productivity features
```

## Best Practices

### Commit Guidelines
1. **Atomic commits**: One logical change per commit
2. **Clear messages**: Descriptive and concise
3. **Test before commit**: Ensure code works
4. **Regular commits**: Don't let branches get stale

### Branch Guidelines
1. **Short-lived branches**: Merge frequently
2. **Descriptive names**: Clear purpose from name
3. **Regular updates**: Rebase with develop frequently
4. **Clean history**: Squash commits when appropriate

### Code Review Process
1. **Self-review first**: Check your own PR
2. **Test locally**: Verify functionality
3. **Documentation**: Update docs if needed
4. **Breaking changes**: Clearly communicate impacts

## Tools and Automation

### Recommended Git Aliases
```bash
# Add to ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    graph = log --oneline --graph --decorate --all
    feature = checkout -b feature/
    hotfix = checkout -b hotfix/
```

### Pre-commit Hooks (Future)
```bash
# Install pre-commit
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
```

## Troubleshooting

### Common Issues

#### **Merge Conflicts**
```bash
# During rebase/merge
git status                    # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git rebase --continue        # or git commit for merge
```

#### **Accidentally Committed to Wrong Branch**
```bash
# Move commits to correct branch
git log --oneline -n 5       # Find commit hash
git checkout correct-branch
git cherry-pick <commit-hash>
git checkout wrong-branch
git reset --hard HEAD~1      # Remove from wrong branch
```

#### **Need to Update Feature Branch**
```bash
# Rebase feature on latest develop
git checkout feature/branch-name
git fetch origin
git rebase origin/develop
```

This workflow ensures clean, maintainable development while supporting the collaborative nature of the Jarv1s project.