import os
import sys
import json
import httpx
import re
import asyncio
from pathlib import Path
from skillcode.config import load_config
from skillcode.core.skills_forge import deep_sniff, surgical_injection, validate_skill
from skillcode.core.subagent import SubagentManager

# Importações dos motores de ferramentas do antigo MCP
from skillcode.core.mcp_server import (
    skinskill_context_save, skinskill_shadow_query, skinskill_generate_pdf,
    skinskill_generate_docx, skinskill_generate_pptx, skinskill_generate_xlsx,
    skinskill_screenshot, skinskill_sigmap_search, skinskill_security_audit,
    skinskill_static_ui_extract, skinskill_ghost_hand, skinskill_distill_project,
    skinskill_hud_notify, skinskill_watchdog, skinskill_vision_audit, skinskill_a2a_sync,
    skinskill_forge_validate_and_save
)

class SkillCodeAgent:
    """
    Agente de Raciocínio Principal do SkillCode.
    Roda loops ReAct para planejar, depurar e executar tarefas complexas de desenvolvimento.
    """
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path(os.getcwd())
        self.subagent_manager = SubagentManager(self.workspace)
        
        # Registro local de ferramentas executáveis por tag
        self.tools = {
            "skinskill_sniff": lambda: json.dumps(deep_sniff(), indent=2),
            "skinskill_context_save": skinskill_context_save,
            "skinskill_shadow_query": skinskill_shadow_query,
            "skinskill_inject": surgical_injection,
            "skinskill_generate_pdf": skinskill_generate_pdf,
            "skinskill_generate_docx": skinskill_generate_docx,
            "skinskill_generate_pptx": skinskill_generate_pptx,
            "skinskill_generate_xlsx": skinskill_generate_xlsx,
            "skinskill_forge_validate_and_save": skinskill_forge_validate_and_save,
            "skinskill_screenshot": skinskill_screenshot,
            "skinskill_sigmap_search": skinskill_sigmap_search,
            "skinskill_security_audit": skinskill_security_audit,
            "skinskill_static_ui_extract": skinskill_static_ui_extract,
            "skinskill_ghost_hand": skinskill_ghost_hand,
            "skinskill_distill_project": skinskill_distill_project,
            "skinskill_hud_notify": skinskill_hud_notify,
            "skinskill_watchdog": skinskill_watchdog,
            "skinskill_vision_audit": skinskill_vision_audit,
            "skinskill_a2a_sync": skinskill_a2a_sync
        }

    async def run_task(self, user_intent: str, console_logger=None) -> str:
        """Executa o loop ReAct principal para atingir a intenção do usuário."""
        config = load_config()
        skinskill_hud_notify(f"🟣 Iniciando tarefa: '{user_intent[:40]}...'", "info")
        if console_logger:
            console_logger.print(f"[bold purple]🟣 Iniciando tarefa:[/bold purple] {user_intent}\n")
            
        system_prompt = f"""# SkillCode Agent - Elite Mindset
Você é o SkillCode, um agente de programação autônomo espetacular.
Seu workspace atual é: {self.workspace.absolute()}

## Super Habilidades (Tools)
Você possui 23 ferramentas executáveis. Para chamá-las, retorne no final de sua resposta a tag exata:
[CALL_TOOL: nome_da_ferramenta, arg1="valor", arg2="valor"]

Lista de ferramentas:
1. `skinskill_sniff` (sem args) - DNA do projeto.
2. `skinskill_context_save` (goal, action_taken, rationale, consequences) - Salva decisões no Shadow-Graph.
3. `skinskill_shadow_query` (query) - Consulta decisões passadas.
4. `skinskill_inject` (code, target_file) - Injeta código via AST.
5. `skinskill_generate_pdf` (content, filename) - Relatórios PDF.
6. `skinskill_generate_docx` (content, filename) - Documentos Word.
7. `skinskill_generate_pptx` (content, filename) - Slides PowerPoint.
8. `skinskill_generate_xlsx` (content, filename) - Planilhas Excel.
9. `skinskill_screenshot` (url=None) - Captura de tela.
10. `skinskill_sigmap_search` (query) - Busca neural semântica.
11. `skinskill_security_audit` (target_dir=".") - Auditoria contra vazamentos de API keys.
12. `skinskill_static_ui_extract` (dir_path=".") - Mapeia design local.
13. `skinskill_ghost_hand` (action, x=0, y=0, text="", key="") - Teclado/Mouse do OS.
14. `skinskill_distill_project` (dir_path=".") - Comprime assinaturas de classes/funções.
15. `skinskill_hud_notify` (message, status="info") - Envia logs para o HUD.
16. `skinskill_watchdog` (log_path, tail_lines=50) - Monitora logs.
17. `skinskill_vision_audit` (target_url, reference_url) - Visual TDD.
18. `skinskill_a2a_sync` (agent_name, message) - Sincroniza instâncias.
19. `skinskill_forge_validate_and_save` (skill_name, code, test_code, impact_description) - Cria novas ferramentas dinamicamente.

Você também pode gerenciar arquivos locais usando as tags:
[FILE_READ: caminho]
[FILE_WRITE: caminho]
CONTEÚDO
[/FILE_WRITE]
[EXEC_CMD: comando] (para rodar comandos bash/cmd locais)

## 🔄 Auto-Forge & Loop de Auto-Evolução
Se a tarefa exigir uma inteligência/ferramenta que você ainda não tem, você deve primeiramente escrever uma skill em Python (ex: `skins/custom_tool.py`), bolar um teste unitário (`tests/test_custom_tool.py`), rodar usando `[EXEC_CMD: ...]` ou `skinskill_forge_validate_and_save` para validar de forma isolada, e só depois utilizá-la.

Sempre que concluir, responda iniciando com "CONCLUÍDO: " e o resumo dos resultados.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_intent}
        ]
        
        max_iterations = 15
        iteration = 0
        final_answer = "A tarefa não pôde ser completada no limite de iterações."
        
        while iteration < max_iterations:
            iteration += 1
            if console_logger:
                console_logger.print(f"[dim]➔ Iteração {iteration}/{max_iterations}...[/dim]")
                
            try:
                # 1. Envia requisição para a LLM
                response_text = await self._call_llm_async(messages, config)
                messages.append({"role": "assistant", "content": response_text})
                
                # Exibe o raciocínio na console
                if console_logger:
                    # Remove tags de ferramentas da exibição comum para manter limpo
                    clean_text = re.sub(r'\[CALL_TOOL:.*?\]', '', response_text)
                    clean_text = re.sub(r'\[FILE_READ:.*?\]', '', clean_text)
                    clean_text = re.sub(r'\[FILE_WRITE:.*?\n.*?\[/FILE_WRITE\]', '', clean_text, flags=re.DOTALL)
                    clean_text = re.sub(r'\[EXEC_CMD:.*?\]', '', clean_text)
                    
                    if clean_text.strip():
                        console_logger.print(f"[white]{clean_text.strip()}[/white]")
                
                # 2. Verifica conclusão
                if "CONCLUÍDO:" in response_text:
                    final_answer = response_text
                    break
                    
                # 3. Execução de Ferramentas / Ações
                tool_output = ""
                
                # A. Chamada de Ferramenta do MCP
                if "[CALL_TOOL:" in response_text:
                    tool_call_str = response_text.split("[CALL_TOOL:", 1)[1].split("]", 1)[0].strip()
                    tool_output = await self._execute_mcp_tool(tool_call_str, console_logger)
                    
                # B. Ler arquivo
                elif "[FILE_READ:" in response_text:
                    read_path = response_text.split("[FILE_READ:", 1)[1].split("]", 1)[0].strip()
                    tool_output = self._read_file(read_path, console_logger)
                    
                # C. Escrever arquivo
                elif "[FILE_WRITE:" in response_text and "[/FILE_WRITE]" in response_text:
                    tool_output = self._write_file(response_text, console_logger)
                    
                # D. Executar comando de terminal
                elif "[EXEC_CMD:" in response_text:
                    cmd_str = response_text.split("[EXEC_CMD:", 1)[1].split("]", 1)[0].strip()
                    tool_output = await self._execute_cmd(cmd_str, console_logger)
                    
                if tool_output:
                    messages.append({"role": "user", "content": tool_output})
                else:
                    messages.append({"role": "user", "content": "Entendido. Prossiga para o próximo passo."})
                    
            except Exception as e:
                final_answer = f"Erro no loop do agente principal: {str(e)}"
                if console_logger:
                    console_logger.print(f"[bold red]❌ Erro:[/bold red] {final_answer}")
                break
                
        skinskill_hud_notify(f"🟣 Loop do agente principal encerrado.", "info")
        return final_answer

    async def _execute_mcp_tool(self, tool_call_str: str, console_logger) -> str:
        """Executa a ferramenta cadastrada a partir da string de tag."""
        parts = tool_call_str.split(",", 1)
        tool_name = parts[0].strip()
        args = {}
        
        if len(parts) > 1:
            # Extrai argumentos no formato arg_name="valor"
            arg_matches = re.findall(r'(\w+)\s*=\s*"(.*?)"', parts[1])
            for k, v in arg_matches:
                args[k] = v
                
        if tool_name not in self.tools:
            return f"Erro: Ferramenta '{tool_name}' não registrada."
            
        if console_logger:
            console_logger.print(f"[bold purple]🛠️ Chamando ferramenta:[/bold purple] [cyan]{tool_name}[/cyan] com args {json.dumps(args)}")
            
        skinskill_hud_notify(f"🛠️ Rodando ferramenta: {tool_name}", "info")
        
        try:
            func = self.tools[tool_name]
            # Verifica quantidade de argumentos esperada
            import inspect
            sig = inspect.signature(func)
            
            # Se for corrotina async
            if asyncio.iscoroutinefunction(func):
                if len(sig.parameters) == 0:
                    res = await func()
                else:
                    # Filtra argumentos válidos
                    valid_args = {k: v for k, v in args.items() if k in sig.parameters}
                    res = await func(**valid_args)
            else:
                if len(sig.parameters) == 0:
                    res = func()
                else:
                    valid_args = {k: v for k, v in args.items() if k in sig.parameters}
                    res = func(**valid_args)
                    
            return f"Output da ferramenta {tool_name}:\n{res}"
        except Exception as e:
            return f"Erro ao executar ferramenta {tool_name}: {str(e)}"

    def _read_file(self, filepath_str: str, console_logger) -> str:
        filepath = self.workspace / filepath_str
        if console_logger:
            console_logger.print(f"[bold yellow]📖 Lendo arquivo:[/bold yellow] {filepath_str}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f"=== FILE CONTENT OF {filepath_str} ===\n{f.read()}"
        except Exception as e:
            return f"Erro ao ler arquivo {filepath_str}: {str(e)}"

    def _write_file(self, response_text: str, console_logger) -> str:
        try:
            header_part, content_part = response_text.split("[/FILE_WRITE]", 1)
            filepath_str = header_part.split("[FILE_WRITE:", 1)[1].split("]", 1)[0].strip()
            file_content = header_part.split("]", 1)[1]
            if file_content.startswith("\n"):
                file_content = file_content[1:]
            
            filepath = self.workspace / filepath_str
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            if console_logger:
                console_logger.print(f"[bold yellow]💾 Escrevendo arquivo:[/bold yellow] {filepath_str}")
                
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_content)
                
            return f"Arquivo {filepath_str} escrito com sucesso (tamanho: {len(file_content)} bytes)."
        except Exception as e:
            return f"Erro ao escrever arquivo: {str(e)}"

    async def _execute_cmd(self, cmd_str: str, console_logger) -> str:
        if console_logger:
            console_logger.print(f"[bold red]💻 Executando comando:[/bold red] {cmd_str}")
            
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )
            stdout, stderr = await proc.communicate()
            res_str = (
                f"Comando executado: {cmd_str}\n"
                f"Exit Code: {proc.returncode}\n"
                f"STDOUT:\n{stdout.decode('utf-8', errors='ignore')}\n"
                f"STDERR:\n{stderr.decode('utf-8', errors='ignore')}"
            )
            return res_str
        except Exception as e:
            return f"Erro ao executar comando: {str(e)}"

    async def _call_llm_async(self, messages: list, config: dict) -> str:
        """Helper assíncrono para enviar chamada para a LLM configurada."""
        model = config.get("DEFAULT_MODEL", "openrouter/google/gemini-2.0-flash:free")
        
        # 1. OpenRouter
        if "openrouter" in model.lower() or config.get("OPENROUTER_API_KEY"):
            api_key = config.get("OPENROUTER_API_KEY")
            model_name = model.replace("openrouter/", "")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": messages
            }
            async with httpx.AsyncClient() as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60.0)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
                
        # 2. Gemini Direto
        elif config.get("GEMINI_API_KEY"):
            api_key = config.get("GEMINI_API_KEY")
            headers = {"Content-Type": "application/json"}
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" or msg["role"] == "system" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            data = {"contents": contents}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data, timeout=60.0)
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
                
        # 3. Claude Direto
        elif config.get("CLAUDE_API_KEY"):
            api_key = config.get("CLAUDE_API_KEY")
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            system_prompt = ""
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    chat_messages.append({"role": msg["role"], "content": msg["content"]})
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "messages": chat_messages
            }
            if system_prompt:
                data["system"] = system_prompt
            async with httpx.AsyncClient() as client:
                response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=data, timeout=60.0)
                response.raise_for_status()
                return response.json()["content"][0]["text"]
        else:
            raise ValueError("Chave de API não configurada. Use 'skc config' para cadastrar.")
