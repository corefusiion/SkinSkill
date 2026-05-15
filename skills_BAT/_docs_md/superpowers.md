---
name: superpowers
description: Metodologia avançada de engenharia para Agentes. Inclui TDD, debugging sistemático e guardrails de qualidade (Karpathy Style). Use sempre que iniciar uma tarefa de desenvolvimento complexa.
---

# 🚀 Engenharia de Elite (Superpowers)

Este é o padrão ouro de desenvolvimento do SkinSkill.

## 🛡️ Guardrails (Karpathy Style)
- **Think Before Code:** Sempre planeje a solução antes de escrever uma única linha.
- **Surgical Changes:** Faça alterações mínimas e precisas. Nunca reescreva arquivos inteiros se não for necessário.
- **Simplicity First:** Evite abstrações prematuras. Prefira código legível e direto.

## 🧪 Metodologia TDD (Red-Green-Refactor)
1.  **Red:** Escreva um teste que falha.
2.  **Green:** Escreva o código mínimo para o teste passar.
3.  **Refactor:** Melhore o código mantendo os testes passando.

## 🔍 Debugging Sistemático
- Capture logs detalhados.
- Use `skinskill_terminal_history` para entender o contexto do erro.
- Isole a causa raiz antes de tentar consertar.

## 🤖 Uso de Sub-Agentes
Para tarefas grandes, delegue sub-tarefas para agentes especialistas via `@generalist` ou ferramentas de delegação.
