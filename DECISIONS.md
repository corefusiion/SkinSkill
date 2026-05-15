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

## 004: Segurança no Comando Heal (shlex)
- **Data:** 15/05/2026
- **Contexto:** Executar comandos sugeridos pela IA via `shell=True` era arriscado.
- **Decisão:** Refatorar para usar `shlex.split` e avisos de segurança explícitos, minimizando riscos de injeção de comando.

## 005: Extração Visual Completa
- **Data:** 15/05/2026
- **Contexto:** O truncamento de HTML/CSS impedia a clonagem de UIs complexas.
- **Decisão:** Remover limites de caracteres no `get_web_dna` para permitir captura total de design tokens.
