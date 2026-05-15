# 🧠 Memory & Context Index

## 📌 Contexto Atual do Projeto
SkinSkill é um "Agentic OS" baseado em MCP. O objetivo é dar autonomia para assistentes de IA realizarem tarefas complexas de desenvolvimento local, com foco em estabilidade, segurança e modularidade.

## 📁 Estrutura de Conhecimento
- **MCP Server:** Localizado em `skinskill/mcp_server.py`. (Core de habilidades).
- **CLI Logic:** Localizado em `skinskill/cli.py`. (Interface de comando e setup).
- **Memória Persistente:** Armazenada em `.skinskill/memory_graph.json`.
- **Habilidades BAT:** Localizado em `skills_BAT/`. (Arsenal de automação inclusa).

## 🔄 Últimas Alterações Importantes
- **v0.5.0:** Integração massiva de habilidades externas (PDF, PPTX, Copywriting).
- **v0.5.6:** Polimento de estabilidade e segurança. Refatoração do `heal` com `shlex`, melhoria no tratamento de erros de injeção e remoção de limites na extração de DNA visual.
