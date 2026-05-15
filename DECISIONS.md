# ⚖️ Architectural Decisions (ADR)

## 001: Uso do FastMCP
- **Data:** 14/05/2026
- **Contexto:** Precisávamos de uma forma rápida e tipada de expor ferramentas para a IA.
- **Decisão:** Usar a biblioteca `mcp[fastmcp]` por ser a mais moderna e intuitiva.

## 002: Memória Neural Local
- **Data:** 14/05/2026
- **Contexto:** Usuários perdem contexto ao trocar de chat ou após desligar o PC.
- **Decisão:** Implementar um cache JSON local de 50 iterações em `.skinskill/`.

## 003: Playwright Auto-Install
- **Data:** 14/05/2026
- **Contexto:** A visão computacional depende de navegadores pesados.
- **Decisão:** Automatizar a instalação via subprocesso na primeira execução do MCP para garantir a experiência "Zero-Config".
