---
name: agno_agent_creator
description: Skill de elite para criação e configuração de agentes usando o framework Agno (evolução do Phidata), com suporte a CLI e AgentOS Playground.
---

# 🚀 Agno Agent Creator Skill

Este guia define o padrão ouro para a criação de agentes autônomos utilizando o framework **Agno**. Siga este protocolo para garantir consistência, persistência e conectividade com a interface visual.

## 🏗️ Estrutura Básica de um Agente
Todo agente de elite no Agno deve conter quatro pilares: **Modelo**, **Memória**, **Ferramentas** e **Instruções**.

### 1. Importações Essenciais
```python
from agno.agent import Agent
from agno.models.openrouter import OpenRouter # Ou OpenAI, Gemini, etc.
from agno.db.sqlite import SqliteDb
from agno.os.app import AgentOS
from dotenv import load_dotenv

load_dotenv()
```

### 2. Configuração do Agente (O "Corpo")
```python
agent = Agent(
    name="nome_do_agente",
    model=OpenRouter(id="seu-modelo-favorito"),
    instructions="Seu prompt de sistema ou caminho para arquivo .md",
    db=SqliteDb(session_table="agent_sessions", db_file="tmp/storage.db"),
    add_history_to_context=True,
    num_history_runs=10,
    markdown=True,
    tools=[...], # Adicione suas ferramentas aqui
)
```

## 🕹️ Modos de Execução

### Modo A: Terminal Interativo (CLI)
Ideal para testes rápidos e desenvolvimento local.
```python
if __name__ == "__main__":
    agent.cli_app()
```
*   **Como rodar:** `python seu_arquivo.py`
*   **Vantagem:** Resposta instantânea no terminal.

### Modo B: AgentOS (Playground Web)
Ideal para visualização de ferramentas, histórico persistente e interface gráfica.
```python
agent_os = AgentOS(agents=[agent])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve("seu_arquivo:app", port=7777, reload=True)
```
*   **Como rodar:** `python seu_arquivo.py`
*   **Acesso:** Vá para [app.agno.com/playground](https://app.agno.com/playground) e conecte em `http://localhost:7777/v1`.

## 🛠️ Melhores Práticas de Elite

1.  **Persistência:** Sempre utilize `SqliteDb` para que o agente não "esqueça" quem é o usuário entre as sessões.
2.  **Contexto Externo:** Utilize arquivos `.md` para as instruções (instruções longas em strings Python tornam o código difícil de manter).
3.  **Segurança de Caminhos:** Ao criar ferramentas de arquivo, sempre utilize a biblioteca `pathlib` para garantir compatibilidade entre Windows e Linux.
4.  **Variáveis de Ambiente:** Nunca coloque chaves de API diretamente no código. Use um arquivo `.env`.

## 🚦 Troubleshooting Comum
- **Erro de Importação:** Certifique-se de que instalou as dependências com `pip install agno openai python-dotenv`.
- **Endpoint no Playground:** Se o Playground não conectar, verifique se adicionou o `/v1` ao final da URL do localhost.
- **Porta Ocupada:** Se a porta 7777 estiver em uso, mude no comando `agent_os.serve(port=8888)`.

---
*Skill gerada para o ecossistema Agente0. Integridade e Performance em primeiro lugar.*
