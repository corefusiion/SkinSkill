<div align="center">

# 🧬 SkinSkill
**The Agentic OS for Developers**

[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-blueviolet?style=for-the-badge&logo=ai)]()
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()
[![PyPI](https://img.shields.io/pypi/v/skinskill?style=for-the-badge&color=orange)]()

**Menos configuração. Mais produto.**  
*SkinSkill é o sistema operacional em background que transforma seu Claude, Cursor ou Gemini em um engenheiro sênior com acesso real ao seu ambiente local.*

</div>

---

## ⚡ O Problema

Assistentes de IA são ótimos para gerar código, mas falham no mundo real. Eles não sabem quais dependências você usa, não conseguem ver erros na tela, esquecem o contexto quando a janela fecha e não podem consertar um container Docker travado.

O **SkinSkill** resolve isso. Integrado via **MCP (Model Context Protocol)**, ele dá à sua IA as ferramentas para **analisar**, **lembrar**, **ver** e **executar ações** na sua máquina.

---

## 🔥 Capacidades Autônomas

Quando conectado, sua IA ganha as seguintes habilidades silenciosas:

- 🛰️ **Mapeamento de Arquitetura:** Antes de sugerir código, a IA varre seus diretórios, lê seus arquivos de configuração (`pyproject.toml`, `package.json`) e descobre quais frameworks você usa.
- 🧠 **Memória Persistente:** O histórico do projeto é salvo localmente. Se você fechar a IDE ou trocar de modelo de IA, o contexto não é perdido.
- 👁️ **Visão Computacional Automática:** A IA pode abrir navegadores invisíveis (Playwright) para clonar o CSS de uma URL que você enviar, ou tirar um print da sua tela para debugar um erro visual.
- 🏥 **Cura de Ambiente:** Se um comando de terminal falhar, a IA pode interceptar o erro, descobrir a causa (ex: porta 8080 em uso) e executar o comando de correção automaticamente.
- 📦 **Baterias Inclusas:** Já vem com scripts internos (`skills_BAT`) para manipulação avançada de arquivos, fluxos de trabalho e integrações.

---

## 🚀 Instalação Rápida

**1. Instale globalmente na sua máquina:**
```bash
uv add skinskill
# ou
pip install skinskill
```

**2. Conecte ao seu Assistente de IA:**

<details>
<summary><b>🟦 Claude Desktop (Setup Automático)</b></summary>
<br>
Abra seu terminal e digite:
<code>tisc setup</code>
<br>Isso injetará a configuração necessária. Apenas reinicie o Claude Desktop e comece a usar.
</details>

<details>
<summary><b>🟧 Cursor, VS Code, Gemini CLI e outros (Manual)</b></summary>
<br>
O SkinSkill funciona com <b>qualquer</b> ferramenta compatível com MCP. Basta adicionar um novo servidor MCP nas configurações da sua IDE com os seguintes parâmetros:
<br><b>Nome:</b> skinskill
<br><b>Comando:</b> <code>python</code>
<br><b>Argumentos:</b> <code>["-m", "skinskill.mcp_server"]</code>
</details>

---

## 🛠️ Como usar (Fale Naturalmente)

Você não precisa saber o nome das ferramentas internas. Apenas converse com a sua IA normalmente.

### 📂 Cenário 1: Refatoração com Contexto
**Você digita:** *"Analise este projeto. Entenda como estamos estruturando as rotas da API e crie um novo endpoint de pagamento seguindo o mesmo padrão."*
> **A Mágica:** A IA roda o analista de arquitetura, descobre seu padrão MVC, cria o arquivo correto e injeta a importação no arquivo principal sem você precisar copiar e colar nada.

### 🎨 Cenário 2: Clonagem de Design
**Você digita:** *"Acesse `https://ui.shadcn.com/docs/components/button` e crie um componente React igual a esse na minha pasta de componentes."*
> **A Mágica:** A IA usa o motor visual para extrair o CSS/HTML puro da URL e gera o componente estilizado.

### 🐛 Cenário 3: Resolução de Conflitos
**Você digita:** *"Tentei rodar o projeto mas deu erro. Descubra o que travou e conserte."*
> **A Mágica:** A IA lê seu terminal, percebe que o banco de dados Docker não subiu, e executa `docker-compose up -d` sozinha.

---

## 📁 Ecossistema do Projeto
- [🛣️ Roadmap](ROADMAP.md) | [⚖️ Decisions](DECISIONS.md) | [🧠 Memory](MEMORY.md)

<div align="center">
  Mantido pela comunidade <b>SkinSkill</b>.
</div>
