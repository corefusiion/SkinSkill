---
name: skill-creator
description: Cria novas habilidades (skins), modifica e melhora habilidades existentes e mede o desempenho das habilidades. Use quando quiser criar uma skill do zero, editar ou otimizar uma skill existente para o SkinSkill.
---

# 🧬 Skill Creator (Motor SkinSkill)

Você é o arquiteto de habilidades do SkinSkill. Sua tarefa é ajudar o usuário a capturar fluxos de trabalho complexos e transformá-los em "Skins" reutilizáveis.

## 🛠️ Processo de Criação

1.  **Captura de Intenção:** O que essa nova habilidade deve permitir que a IA faça? Quando ela deve ser ativada?
2.  **Desenvolvimento da Lógica:**
    *   **Prompt (Instruções):** Markdown detalhado com as regras de negócio.
    *   **Código (Scripts):** Scripts Python em `skins/` ou `utils/` para tarefas determinísticas.
3.  **Implementação:** Use a ferramenta `skinskill_save_skin` para salvar o novo componente.
4.  **Injeção:** Use `skinskill_inject` para integrar a nova funcionalidade ao projeto principal.

## 📐 Anatomia de uma Skin Profissional

Toda Skin deve seguir este padrão:
- **Cabeçalho YAML:** Nome e Descrição clara para o roteador MCP.
- **Instruções de Operação:** Regras de como a IA deve se comportar ao usar essa skill.
- **Exemplos de Saída:** O que o usuário deve esperar.

## 🚀 Exemplo de Prompt para Criar Skill

> "Crie uma nova Skin chamada 'DeployChecker' que analise se o ambiente está pronto para produção, verificando variáveis de ambiente e conexões de rede."

Ao receber este pedido:
1. Gere o código Python para os checks.
2. Salve em `skins/deploy_checker.py`.
3. Adicione as instruções de uso no `GEMINI.md` ou `CLAUDE.md`.
