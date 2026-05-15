# 🧬 Análise Técnica de Adaptação: Skill Engine

Este documento detalha o plano de integração e universalização das habilidades externas para o ecossistema **SkinSkill**.

## 1. Mapeamento de Habilidades

| Habilidade | Origem | Função Principal | Adaptação SkinSkill |
| :--- | :--- | :--- | :--- |
| **skill-creator** | Anthropic | Criação/Melhoria de Skills | Tool `skinskill_create_skill` + Prompt |
| **pdf** | Anthropic | Geração/Edição de PDF | Tool `skinskill_pdf_engine` |
| **pptx** | Anthropic | Geração de Slides | Tool `skinskill_pptx_engine` |
| **docx** | Anthropic | Manipulação de DOCX | Tool `skinskill_docx_engine` |
| **copywriting** | MarketingSkills | Frameworks de Venda | Resource `skills_BAT/marketing` |
| **design-system**| arvindrk | Extração de Design Tokens | Tool `skinskill_get_web_dna` (Expandida) |
| **superpowers** | obra | Metodologia TDD/Agente | Injection em `GEMINI.md`/`CLAUDE.md` |
| **caveman** | JuliusBrussee | Compressão de Contexto | Tool `skinskill_compress` |
| **deer-flow** | bytedance | Orquestração Sub-Agentes | Tool `skinskill_delegate` |
| **karpathy** | multica-ai | Guardrails de Código | Prompt `karpathy_rules` |
| **ui-ux-pro** | nextlevelbuilder| Raciocínio de Design | Tool `skinskill_design_logic` |

## 2. Estratégia de Universalização (LLM/IDE Agnostic)

Para garantir que as habilidades funcionem em qualquer lugar (não apenas Claude):

1.  **Abstração de Ferramentas:** Mapear nomes genéricos (Read/Write) para as ferramentas nativas de cada plataforma (ex: `read_file` no Gemini, `ReadFile` no Claude Code).
2.  **MCP como Middleware:** Usar o servidor MCP como o único ponto de verdade. A lógica pesada (Python) fica no servidor; as instruções leves (Markdown) ficam nos recursos MCP.
3.  **Self-Correction:** As instruções injetadas (`GEMINI.md`/`CLAUDE.md`) ensinarão a IA a detectar o ambiente e adaptar os nomes das ferramentas on-the-fly.

## 3. Próximos Passos (Execução)

1.  Portar scripts de geração de arquivos (PDF/DOCX/PPTX).
2.  Criar a estrutura de diretórios `skills_BAT` categorizada.
3.  Implementar o "Meta-Prompt" de criação de habilidades.
4.  Atualizar o `mcp_server.py` com as novas capacidades.
