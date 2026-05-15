"""Context builder for assembling agent prompts."""

import base64
import mimetypes
import platform
from pathlib import Path
from typing import Any

from loguru import logger

from caiocore.agent.memory import MemoryStore
from caiocore.agent.skills import SkillsLoader


class ContextBuilder:
    """
    Builds the context (system prompt + messages) for the agent.
    
    Assembles bootstrap files, memory, skills, and conversation history
    into a coherent prompt for the LLM.
    """
    
    BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md"]
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory = MemoryStore(workspace)
        self.skills = SkillsLoader(workspace)
    
    def build_system_prompt(self, skill_names: list[str] | None = None, is_specialist: bool = False) -> str:
        """
        Build the system prompt from bootstrap files, memory, and skills.
        
        Args:
            skill_names: Optional list of skills to include.
            is_specialist: Whether this prompt is for a specialized agent.
        
        Returns:
            Complete system prompt.
        """
        parts = []
        
        # Core identity
        parts.append(self._get_identity(is_specialist=is_specialist))
        
        # Bootstrap files
        bootstrap = self._load_bootstrap_files(is_specialist=is_specialist)
        if bootstrap:
            parts.append(bootstrap)
        
        # Memory context
        memory = self.memory.get_memory_context()
        if memory:
            parts.append(f"# Memory\n\n{memory}")
        
        # Skills - only load for the main orchestrator (Caio)
        if not is_specialist:
            # 1. Always-loaded skills: include full content
            always_skills = self.skills.get_always_skills()
            if always_skills:
                always_content = self.skills.load_skills_for_context(always_skills)
                if always_content:
                    parts.append(f"# Active Skills\n\n{always_content}")
            
            # 2. Available skills: only show summary
            skills_summary = self.skills.build_skills_summary()
            if skills_summary:
                parts.append(f"""# Habilidades Técnicas Auxiliares (Skills)

IMPORTANTE: As 'Skills' abaixo são apenas capacidades técnicas que estendem seus comandos. Elas NÃO são agentes/especialistas. 
Para usar uma skill, leia seu arquivo SKILL.md usando a tool read_file.

{skills_summary}""")
        
        return "\n\n---\n\n".join(parts)
    
    def _get_identity(self, is_specialist: bool = False) -> str:
        """Get the core identity section."""
        from datetime import datetime
        import time as _time
        now = datetime.now().strftime("%Y-%m-%d %H:%M (%A)")
        tz = _time.strftime("%Z") or "UTC"
        workspace_path = str(self.workspace.expanduser().resolve())
        system = platform.system()
        runtime = f"{'macOS' if system == 'Darwin' else system} {platform.machine()}, Python {platform.python_version()}"
        
        if is_specialist:
            identity_header = "# Nucleo Especialista"
            identity_desc = "Você é um agente de inteligência especializado operando dentro do ecossistema Caio Core."
        else:
            identity_header = "# CAIO — Assistente Executivo Inteligente"
            identity_desc = "Você é o CAIO, um assistente de IA altamente capaz criado pela Caio Corp. Você é profissional, direto e eficiente."

        return f"""{identity_header}

{identity_desc}

## Como Responder
- Seja DIRETO e NATURAL. Responda como um profissional competente, nunca como um robô.
- Para cumprimentos simples ("oi", "olá"), responda de forma breve e amigável. Exemplo: "Olá! Como posso ajudar?" — NUNCA despeje relatórios técnicos ou status do sistema.
- Use formatação markdown normalmente (negrito, itálico, listas, títulos) quando fizer sentido para clareza.
- Foque no que o usuário PEDIU. Não adicione informações técnicas desnecessárias (workspace, hora UTC, tier de agentes).
- IDIOMA: Português Brasileiro.

## Quando Usar Estrutura
- SOMENTE quando a resposta for complexa (relatórios, diagnósticos, análises) use títulos e listas.
- Para conversas curtas, responda em texto simples.

## Capacidades
- Você coordena agentes especializados (Email, Schedule, Documentos, Pesquisa, etc.)
- Você tem acesso à ferramenta `get_system_status` para monitorar em tempo real a saúde de toda a stack CaioCore (Agente BD, Token, SSO, Life). SEMPRE use esta ferramenta antes de responder sobre a saúde do sistema.
- Você pode executar ferramentas: buscar na web, ler/escrever arquivos, executar comandos, gerar documentos.
- Quando o usuário pedir uma tarefa que exija ferramentas, EXECUTE IMEDIATAMENTE e reporte o resultado.

## Ambiente de Execução
{runtime}
Hora Atual: {now} ({tz})
Workspace: {workspace_path}

## Workspace
Seu workspace esta em: {workspace_path}
- Memoria: {workspace_path}/memory/MEMORY.md
- Saida de Arquivos (Download): {workspace_path}/out/

CRITICO: Salve QUALQUER arquivo gerado (PDF, XLSX, HTML, etc.) obrigatoriamente em {workspace_path}/out/.
Para recordar eventos passados, use grep em {workspace_path}/memory/HISTORY.md"""
    
    def _load_bootstrap_files(self, is_specialist: bool = False) -> str:
        """Load all bootstrap files from workspace."""
        parts = []
        
        # Prevent personality leakage: Specialists should not receive Caio's SOUL.md, AGENTS.md, or TOOLS.md
        files_to_load = [f for f in self.BOOTSTRAP_FILES if not (is_specialist and f in ["SOUL.md", "AGENTS.md", "USER.md", "TOOLS.md"])]
        
        for filename in files_to_load:
            file_path = self.workspace / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8", errors="replace")
                parts.append(f"## {filename}\n\n{content}")
        
        return "\n\n".join(parts) if parts else ""
    
    def build_messages(
        self,
        history: list[dict[str, Any]],
        current_message: str,
        skill_names: list[str] | None = None,
        media: list[str] | None = None,
        channel: str | None = None,
        chat_id: str | None = None,
        specialist_instruction: str = ""
    ) -> list[dict[str, Any]]:
        """
        Build the complete message list for an LLM call.

        Args:
            history: Previous conversation messages.
            current_message: The new user message.
            skill_names: Optional skills to include.
            media: Optional list of local file paths for images/media.
            channel: Current channel (telegram, feishu, etc.).
            chat_id: Current chat/user ID.
            specialist_instruction: Optional specialized instructions for this turn.

        Returns:
            List of messages including system prompt.
        """
        messages = []

        # System prompt
        base_system_prompt = self.build_system_prompt(skill_names, is_specialist=bool(specialist_instruction))
        
        if specialist_instruction:
            logger.info("Building system prompt with SPECIALIST identity (specialist_instruction present)")
            # Persona Dominante: As instruções do especialista vêm PRIMEIRO e com aviso de autoridade
            system_prompt = (
                f"## IDENTIDADE E MISSÃO DO ESPECIALISTA\n"
                f"VOCÊ É O SEGUINTE ESPECIALISTA E DEVE AGIR ESTRITAMENTE DE ACORDO COM ESTAS INSTRUÇÕES:\n"
                f"{specialist_instruction}\n\n"
                f"--- SISTEMA CAIO CORE (CAPACIDADES BASE) ---\n"
                f"{base_system_prompt}"
            )
        else:
            system_prompt = base_system_prompt
            
        if channel and chat_id:
            system_prompt += f"\n\n## Sessão Atual\nCanal: {channel}\nID do Chat: {chat_id}"

        messages.append({"role": "system", "content": system_prompt})

        # History
        messages.extend(history)

        # Current message (with optional image attachments)
        user_content = self._build_user_content(current_message, media)
        messages.append({"role": "user", "content": user_content})

        return messages

    def _build_user_content(self, text: str, media: list[str] | None) -> str | list[dict[str, Any]]:
        """Build user message content with optional base64-encoded images."""
        if not media:
            return text
        
        images = []
        for path in media:
            p = Path(path)
            mime, _ = mimetypes.guess_type(path)
            if not p.is_file() or not mime or not mime.startswith("image/"):
                continue
            b64 = base64.b64encode(p.read_bytes()).decode()
            images.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
        
        if not images:
            return text
        return images + [{"type": "text", "text": text}]
    
    def add_tool_result(
        self,
        messages: list[dict[str, Any]],
        tool_call_id: str,
        tool_name: str,
        result: str
    ) -> list[dict[str, Any]]:
        """
        Add a tool result to the message list.
        
        Args:
            messages: Current message list.
            tool_call_id: ID of the tool call.
            tool_name: Name of the tool.
            result: Tool execution result.
        
        Returns:
            Updated message list.
        """
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": result
        })
        return messages
    
    def add_assistant_message(
        self,
        messages: list[dict[str, Any]],
        content: str | None,
        tool_calls: list[dict[str, Any]] | None = None,
        reasoning_content: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Add an assistant message to the message list.
        
        Args:
            messages: Current message list.
            content: Message content.
            tool_calls: Optional tool calls.
            reasoning_content: Thinking output (Kimi, DeepSeek-R1, etc.).
        
        Returns:
            Updated message list.
        """
        msg: dict[str, Any] = {"role": "assistant"}

        # Always include content — some providers (e.g. StepFun) reject
        # assistant messages that omit the key entirely.
        msg["content"] = content

        if tool_calls:
            msg["tool_calls"] = tool_calls

        # Include reasoning content when provided (required by some thinking models)
        if reasoning_content is not None:
            msg["reasoning_content"] = reasoning_content

        messages.append(msg)
        return messages
