# 🧬 SkinSkill: The Universal MCP Server

To make SkinSkill accessible to **Claude Code, Cursor, GitHub Copilot, and any other AI tool**, it must be built as a **Model Context Protocol (MCP) Server**.

This allows external AI assistants to call SkinSkill's "God Mode" capabilities as native tools.

## Architecture

1.  **The Core Engine:** The Python logic we've built (sniffing, hunting, injecting, healing).
2.  **The MCP Interface:** A server that exposes these core functions as standardized tools.
3.  **The Clients:** Claude Code, Cursor, etc., connect to the SkinSkill MCP Server.

## The Tools Exposed via MCP

When an AI assistant connects to SkinSkill, it gains these superpowers:

### 1. `skinskill_sniff_context`
*   **What it does:** Reads the entire project DNA (frameworks, architecture, dependencies) and returns a hyper-dense summary.
*   **Use Case:** An AI assistant uses this *before* writing code to ensure it perfectly matches the project's style.

### 2. `skinskill_apply_skin` (The Auto-Expander)
*   **What it does:** Accepts an intent (e.g., "add redis caching"), hunts for the best implementation, generates the code, and **surgically injects it** into the project.
*   **Use Case:** You tell Claude Code "Make this faster." Claude Code calls this tool, and SkinSkill handles the entire Redis setup and injection.

### 3. `skinskill_heal_environment` (The Immortal Hook)
*   **What it does:** Analyzes a runtime error log and automatically fixes the OS/environment (e.g., kills a blocking port, starts Docker).
*   **Use Case:** Claude Code tries to run a test that fails due to a missing DB. Claude calls `heal_environment`, SkinSkill starts the DB, and the test passes.

### 4. `skinskill_audit_commit` (The Shadow Maintainer)
*   **What it does:** Analyzes a diff, detects security flaws or 'slop', and autonomously applies a corrective 'Skin'.
*   **Use Case:** You ask Cursor to commit. A pre-commit hook triggers SkinSkill to sanitize the code before it hits the repo.

## Implementation Plan

We will use the official `mcp` Python SDK to wrap our existing logic into a local server that Claude Code or any other tool can connect to via `stdio`.