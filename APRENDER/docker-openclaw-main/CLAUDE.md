# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Docker OpenClaw is a Docker-based deployment of OpenClaw, a personal AI assistant that runs locally with security hardening built-in. This repository provides a production-ready Docker setup with:
- Security hardening by default (non-root user, loopback binding, pairing-based authentication)
- Multi-channel support (Telegram, WhatsApp, Discord, Slack, Signal, iMessage, Google Chat, Teams, Matrix, Webchat)
- Multi-LLM support via OpenRouter (Claude, GPT, Gemini, and 200+ models)
- Voice Wake + Talk Mode support
- Live Canvas with A2UI
- Browser control with CDP
- Skills platform
- Persistent storage with Docker volumes
- Automated configuration via environment variables

## Build and Run Commands

### Basic Commands
```bash
# Build and start container
docker compose up -d

# Rebuild from scratch (pulls latest openclaw)
docker compose build --no-cache
docker compose up -d

# View logs
docker compose logs -f              # Follow logs
docker compose logs --tail 100      # Last 100 lines

# Container lifecycle
docker compose restart              # Restart container
docker compose stop                 # Stop without removing
docker compose down                 # Stop and remove container
docker compose down -v              # Remove container + volumes (deletes all data)

# Access container shell
docker compose exec openclaw bash
```

### OpenClaw CLI Commands
```bash
# Configuration and status
docker exec openclaw openclaw doctor              # Check for issues
docker exec openclaw openclaw gateway --verbose   # Start gateway with verbose logging
docker exec openclaw openclaw update --channel stable  # Update to latest stable

# Channel management
docker exec -it openclaw openclaw channels login whatsapp   # Login to WhatsApp
docker exec openclaw openclaw pairing approve telegram <code>  # Approve Telegram pairing
```

## Architecture

### Docker Architecture
- **Base image**: `node:22-slim`
- **Runtime**: Installs `openclaw` npm package
- **User**: Non-root user `openclaw` (UID/GID created during build)
- **Entry point**: `entrypoint.sh` — performs config generation and env var injection
- **Security**: no-new-privileges, read-only tmpfs where applicable

### Directory Structure
```
/home/openclaw/
├── .openclaw/              # Config directory
│   ├── openclaw.json       # Generated config (secrets injected from env vars)
│   └── openclaw.json.template  # Template copied during build
├── workspace/              # Agent workspace (AGENTS.md, SOUL.md, TOOLS.md, skills, memory)
└── logs/                   # Log files (persistent)
```

### Docker Volumes
| Volume | Mount Path | Purpose |
|--------|-----------|---------|
| `openclaw-data` | `/home/openclaw/.openclaw` | Config, session data, auth tokens, pairing info |
| `openclaw-workspace` | `/home/openclaw/workspace` | Workspace files, AGENTS.md, SOUL.md, skills |
| `openclaw-logs` | `/home/openclaw/logs` | Log files (persistent) |

### Configuration Flow
1. **Build time**: Dockerfile copies `openclaw.json.template` to container
2. **Runtime**: `entrypoint.sh` generates config from template on first run
3. **Env var injection**: `entrypoint.sh` injects secrets (API keys, tokens) from environment variables into config JSON
4. **Provider detection**: Auto-detects LLM provider from env vars
5. **Config written**: Final config saved as `~/.openclaw/openclaw.json` with `chmod 600`
6. **Gateway starts**: `openclaw gateway` command executes

### Network & Security
- **Gateway bind**: Container binds to `0.0.0.0:18789` internally (required for Docker port mapping)
- **Host access**: `docker-compose.yml` restricts host-side access to `127.0.0.1:18789` (loopback only)
- **Network**: Bridge network `openclaw-net` with `internal: false` (allows outbound internet for API calls)
- **Security options**: `no-new-privileges:true`, user isolation
- **DM policy**: Defaults to `pairing` (users must be approved before chatting)

## Key Files

### Dockerfile
- Installs system dependencies: `ffmpeg`, `python3`, `git`, `curl`
- Installs `openclaw` globally via npm
- Optionally installs `faster-whisper` for audio transcription
- Creates non-root user `openclaw`
- Fixes Windows CRLF line endings with `sed -i 's/\r$//'` on entrypoint.sh

### entrypoint.sh
Bash script that runs before OpenClaw starts. Key responsibilities:
- Creates config directory if missing
- Generates config from template on first run
- Injects environment variables into JSON config using Node.js
- Auto-detects and configures LLM provider
- Sets gateway bind to `lan` (required for Docker)
- Configures logging level
- Sets `chmod 600` on config file (protect secrets)
- Executes CMD (openclaw gateway)

### docker-compose.yml
- Service name: `openclaw`
- Build context: current directory (uses Dockerfile)
- Restart policy: `unless-stopped`
- Port binding: `127.0.0.1:18789:18789` (loopback only on host)
- Three volumes for data, workspace, logs
- Bridge network with internet access
- Security: `no-new-privileges:true`

## Environment Variables Reference

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `GATEWAY_AUTH_TOKEN` | Yes | Protects gateway API | `openssl rand -hex 24` |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key | `sk-or-v1-...` |
| `DEFAULT_MODEL` | No | Default LLM model | `openrouter/anthropic/claude-sonnet-4.5` |
| `TELEGRAM_BOT_TOKEN` | No | Telegram channel | `123456:ABC...` |
| `DISCORD_BOT_TOKEN` | No | Discord channel | `...` |
| `SLACK_BOT_TOKEN` | No | Slack bot token | `xoxb-...` |
| `SLACK_APP_TOKEN` | No | Slack app token | `xapp-...` |
| `BRAVE_API_KEY` | No | Web search tool | `...` |
| `LOG_LEVEL` | No | Logging verbosity | `info` (default) |
| `GATEWAY_PORT` | No | Gateway port | `18789` (default) |

## Additional Documentation

- **README.md**: User-facing documentation, setup instructions, channel configuration
- **SECURITY.md**: Detailed security hardening guide for local and cloud deployments
- **SETUP-OPENROUTER.md**: OpenRouter configuration and troubleshooting
- **Official docs**: https://docs.openclaw.ai
- **Discord community**: https://discord.gg/clawd
