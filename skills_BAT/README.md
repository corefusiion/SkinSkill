# Caio Skills & Agents Platform

Este repositório é uma plataforma avançada de agentes e ferramentas (skills) que estendem as capacidades do assistente Caio. A estrutura foi reorganizada para separar logicamente as ferramentas executáveis da inteligência baseada em conhecimento e personas.

## 📂 Estrutura do Projeto

O repositório está dividido em duas categorias principais:

### 1. `_apps_py` (Motores e Executáveis)
Contém as ferramentas operacionais, scripts de automação e integrações de sistema escritas em Python. Estes são os "músculos" do sistema.
- **Destaques:** Automação de E-mail, Integração com Google Calendar, Geradores de Documentos (PDF/Office), Scrapers Web e Orquestradores de Sistema.

### 2. `_docs_md` (Agentes e Inteligência)
Contém as definições de personas, princípios de design, guias de arquitetura e instruções de agentes em Markdown. Estes são o "cérebro" do sistema.
- **Destaques:** Especialistas em Backend/Frontend, Arquitetura de Software, Auditoria de Segurança, Estratégias de SEO e Modos de Brainstorming.

---

## 🛠️ Ferramentas em Destaque (Executáveis - `_apps_py`)

| Categoria | Pasta/Ferramenta | Descrição Técnica |
|:---|:---|:---|
| **Comunicação** | `email_agent`, `email_read/send/delete` | Suite completa para monitoramento e manipulação de e-mails. |
| **Produtividade** | `google_calendar` | Sincronização e gestão de eventos no Google Calendar. |
| **Documentos** | `generators`, `doc_agent`, `pdf_reader` | Geração de arquivos .docx, .xlsx, .pptx e leitura/processamento de PDFs. |
| **IA & Mídia** | `generator` | Ferramenta de geração de imagens e mídia via IA. |
| **Infraestrutura** | `system_status`, `shell`, `filesystem` | Monitoramento de sistema e manipulação avançada de arquivos e terminal. |
| **Orquestração** | `loop`, `subagent`, `smart_router` | Motores de execução contínua e roteamento inteligente de tarefas. |

---

## 🧠 Especialistas e Agentes (`_docs_md`)

| Persona/Skill | Descrição e Especialidade |
|:---|:---|
| `app-builder` | Orquestrador principal para criação de aplicações full-stack do zero. |
| `architecture` | Framework para decisões arquiteturais e análise de trade-offs. |
| `security-auditor` | Auditoria de segurança baseada em OWASP e Red Team tactics. |
| `nextjs-react-expert` | Especialista em performance React e ecossistema Next.js. |
| `database-design` | Princípios de modelagem de dados, indexação e seleção de ORM. |
| `brainstorming` | Protocolo de questionamento socrático para refinamento de requisitos. |
| `vulnerability-scanner` | Mapeamento de superfície de ataque e análise de risco. |
| `game-development` | Suite completa para desenvolvimento de jogos (2D, 3D, VR, Multiplayer). |

---

## 🔍 Notas de Organização e Duplicidade

Durante a análise minuciosa, foram identificadas e mapeadas as seguintes relações:

- **E-mail:** Fragmentado propositalmente em `read`, `send` e `delete` para permitir que o agente use apenas a permissão necessária para cada sub-tarefa.
- **Geradores:** 
    - `generator` (singular): Focado em geração de mídia por IA.
    - `generators` (plural): Biblioteca interna para criação de documentos Office.
- **Documentação:**
    - `doc_agent`: Motor de conversão e formatação de arquivos.
    - `documentation-writer`: Persona focada na escrita de manuais e clareza técnica.
- **Consolidação:** Pastas como `frontend-design` e `web-design-guidelines` trabalham em conjunto, onde uma define a estética e a outra valida a acessibilidade e conformidade.

---

## 🚀 Como Usar

Cada pasta dentro de `_apps_py` ou `_docs_md` pode conter um arquivo `SKILL.md`. Este arquivo contém o **YAML frontmatter** necessário para que o Caio reconheça a ferramenta automaticamente ao ser carregada.

Para criar uma nova ferramenta, utilize o agente `skill-creator` presente na plataforma.

---
*Atualizado em: 26 de Abril de 2026*
