<div align="center">

<img src="https://raw.githubusercontent.com/corefusiion/SkinSkill/main/branding/banner.svg" alt="SkinSkill Banner" width="100%">

# SkinSkill 2.0: The Agentic OS for AI (v0.5.6)
**The Ultimate Modular Engine for Autonomous Developers**

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-blueviolet?style=for-the-badge&logo=ai)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()
[![PyPI](https://img.shields.io/pypi/v/skinskill?style=for-the-badge&color=orange)]()

**Stop babysitting your AI. Start building products.**  
*SkinSkill is the modular agentic engine that transforms standard AI assistants into Senior Engineers with a persistent brain, computer vision, local security, and an infinite, self-evolving arsenal of skills.*

</div>

---

## ⚡ O que há de novo na v0.5.6 (A Revolução do "Boom" Tecnológico)

Nesta versão, integramos o poder das ferramentas mais avançadas do mercado (SigMap, FoxGuard, Memanto, NpxSkillUI) diretamente na arquitetura do nosso MCP:

### 1. 🛡️ Skill-Forge (Auto-Evolução Segura)
A IA agora não apenas "gera código" para novas habilidades. Ela escreve o script, **gera os testes unitários**, executa-os em um sandbox e só injeta a ferramenta no seu ambiente se ela for validada como 100% funcional.

### 2. 🧠 Neural Indexer (SigMap/CodeGraph)
*Adeus ao desperdício de tokens!* O novo comando `tisc neural-index` mapeia semanticamente todo o seu projeto em um grafo local. Quando a IA precisa de contexto, ela faz consultas cirúrgicas (`skinskill_sigmap_search`) em vez de ler o repositório inteiro. **Até 80% de economia de tokens.**

### 3. 🔐 Security Audit (FoxGuard)
A ferramenta `skinskill_security_audit` fornece um escudo local de varredura de segurança ultra-rápido, rastreando chaves da AWS, senhas e APIs vazadas no código antes mesmo de você realizar um commit.

### 4. 🗃️ Memória de Longo Prazo (Memanto)
O histórico do agente não é mais um "texto morto". Com `skinskill_memory_query`, a IA pode perguntar: "O que já tentamos sobre autenticação ontem?" e recuperar apenas os eventos cruciais daquele tópico.

### 5. 🎨 Design Engine Nativa
- **UI Estática:** Extração super rápida de CSS/Tailwind (NpxSkillUI) usando `skinskill_static_ui_extract`.
- **Visão Avançada:** Screenshots adaptativos que suportam modo Headless em servidores usando Playwright via `skinskill_screenshot`.

### 6. 📄 Arsenal Office Universal
Seu agente de código agora também é seu executivo. Ele pode criar relatórios não apenas em **PDF**, mas em **Word (.docx)**, **PowerPoint (.pptx)** e **Excel (.xlsx)** usando ferramentas MCP nativas.

### 7. 🏥 Self-Healing Autônomo
A famosa capacidade de auto-correção de terminal agora é um recurso MCP direto (`skinskill_heal`), permitindo que a IA tente resolver problemas de ambiente e porta ocupada completamente sozinha.

---

## ⚡ Quick Start & Setup

**1. Install Global:**
```bash
pip install skinskill --upgrade
```

**2. Otimize seu Projeto (Novo!):**
Mapeie a "mente" do seu repositório para economizar tokens:
```bash
tisc neural-index
```

**3. Auto-Connect (Zero-Touch):**
```bash
tisc setup
```
*Reinicie seu Assistente de IA (Claude Desktop, Cursor, etc) e comece a criar.*

---

## 🟧 Configuração Manual do MCP

Para IDEs que suportam configuração via JSON (Cursor, VS Code, Windsurf), utilize:

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

---

<div align="center">
  Feito com ❤️ por <b>SkinSkill | Agente0</b><br>
  <a href="ROADMAP.md">Roadmap</a> • <a href="DECISIONS.md">Architecture</a> • <a href="MEMORY.md">Brain</a>
</div>