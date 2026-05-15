<div align="center">

<img src="https://raw.githubusercontent.com/corefusiion/SkinSkill/main/branding/banner.svg" alt="SkinSkill Banner" width="100%">

# 🧬 SKINSKILL
### **The Ultimate Agentic OS for Developers**

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-blueviolet?style=for-the-badge&logo=ai)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()
[![PyPI](https://img.shields.io/pypi/v/skinskill?style=for-the-badge&color=orange)]()

**Stop babysitting your AI. Start building products.**  
*SkinSkill is the modular agentic engine that turns any AI assistant into a Senior Engineer with a persistent brain, computer vision, and an infinite arsenal of skills.*

[Roadmap](ROADMAP.md) • [Architecture](DECISIONS.md) • [Memory](MEMORY.md) • [Community](#)

</div>

---

## 🔥 Why SkinSkill?

Standard AI assistants are **blind** to your local environment and **amnesic** between sessions. You waste half your day re-explaining context and fixing environment errors.

**SkinSkill transforms your AI from an "Assistant" into an "Autonomous Agent".** It injects a professional-grade operating system into your workflow via the **Model Context Protocol (MCP)**.

---

## 💎 The 7+ Elite Superpowers

SkinSkill v0.5.x comes "Batteries Included" with a modular engine that expands as you grow.

### 🧠 1. Neural Memory & Token Economy
The AI finally has a **long-term brain**. It remembers decisions, goals, and errors across sessions and different LLMs.
*   **Caveman Compression:** Save up to **70% of tokens** while preserving technical meaning.

### 🏥 2. Self-Healing Terminal (Zero Copy-Paste)
Build broke? Port 3000 in use? Zombie process? 
*   The AI intercepts terminal errors, identifies the root cause, and **fixes the environment autonomously** with your permission.

### 👁️ 3. Design DNA & Computer Vision
Your IA gains "Eyes" to see the internet like a Frontend Senior.
*   **UI Mirroring:** Extract exact CSS, colors, and fonts from any URL.
*   **Screenshot Debugging:** AI takes snapshots of your screen to fix visual bugs in real-time.

### 📄 4. Document & Office Engine
Turn your progress into professional artifacts instantly.
*   Generate **PDF** reports, **PPTX** pitch decks, and **DOCX** briefs directly from your code logic.

### 🚀 5. Engineering Superpowers (Karpathy Mode)
Forces the AI to work like the top 1% of engineers.
*   **Architecture Sniffing:** Instant mapping of legacy repos.
*   **TDD Enforcement:** Native Test-Driven Development flow.
*   **Karpathy Guardrails:** Surgical, minimal, and simple code changes only.

### 🛠️ 6. Skill Creator (Meta-Ability)
The OS is **self-evolving**. You can tell the IA to "learn a new trick," and it will autonomously write, test, and install a new "Skin" (tool) into your project.

### 📦 7. Batteries Included (`skills_BAT`)
Pre-loaded automation modules for:
*   **Communication:** Email (Send/Read) & Google Calendar integration.
*   **Orchestration:** Multi-agent workflows and smart-routing.

---

## ⚡ Installation & MCP Setup

SkinSkill connects to your AI via the Model Context Protocol (MCP). 

**1. Install the Engine Globally:**
```bash
uv add skinskill
# or
pip install skinskill
```

**2. Connect your IDE (Choose your setup):**

<details open>
<summary><b>🟦 Claude Desktop (Automatic Zero-Touch)</b></summary>
<br>
Run the following command in your terminal. SkinSkill will automatically detect and inject the MCP configuration into Claude Desktop.
<br><br>

```bash
tisc setup
```
*Restart Claude Desktop to activate the engine.*
</details>

<details>
<summary><b>🟧 Cursor / VS Code / Windsurf (Manual JSON Config)</b></summary>
<br>
For IDEs that support MCP via JSON configuration (or extensions like Claude Dev/RooCode), add the following block to your MCP Settings:
<br><br>

```json
{
  "mcpServers": {
    "skinskill": {
      "command": "python",
      "args": ["-m", "skinskill.mcp_server"]
    }
  }
}
```
</details>

<details>
<summary><b>✨ Gemini CLI / Terminal Agents</b></summary>
<br>
If you are using Gemini CLI, Copilot CLI, or other terminal-based agents, SkinSkill acts natively! As long as the package is installed in your environment, terminal agents can invoke the server module directly via `python -m skinskill.mcp_server`.
</details>

---

## 🛠️ Real-World Scenarios

### 📂 Scenario 1: The 2 AM Build Break
> **You:** *"The project won't start. Fix it."*
> **SkinSkill:** Detects a port conflict and a missing `.env` key. Frees the port, syncs the env, and restarts the server.

### 🎨 Scenario 2: Instant Component UI
> **You:** *"Clone the header style from `stripe.com` and create a React component."*
> **SkinSkill:** Opens a headless browser, captures the design tokens, and saves the file in `/skins`.

### 💼 Scenario 3: Automated Delivery
> **You:** *"We finished the Auth flow. Generate a PDF report and a PPTX presentation for the PO."*
> **SkinSkill:** Analyzes the work, writes the copy, and outputs the files.

---

<div align="center">
  <h3>The Agentic Revolution is here.</h3>
  Maintained by the <b>SkinSkill Community</b>.
</div>
