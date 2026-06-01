import sys
import os
import json
import httpx
import asyncio
import subprocess
from pathlib import Path
from skillcode.config import load_config
from skillcode.core.mcp_server import skinskill_hud_notify

class SubagentManager:
    """
    Gerenciador independente de subagentes em background.
    Roda loops de raciocínio da IA em tarefas específicas e executa comandos do terminal/arquivos.
    """
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path(os.getcwd())
        self._running_tasks = {}

    def spawn(self, task_description: str, label: str = "Subagent") -> str:
        """Dispara um subagente assíncrono em background."""
        task_id = os.urandom(4).hex()
        bg_task = asyncio.create_task(self._run_subagent(task_id, task_description, label))
        self._running_tasks[task_id] = bg_task
        bg_task.add_done_callback(lambda _: self._running_tasks.pop(task_id, None))
        
        skinskill_hud_notify(f"🤖 Subagente [{label}] iniciado (id: {task_id}).", "info")
        return f"🤖 Subagente [{label}] iniciado (id: {task_id}). Ele executará em background."

    async def _run_subagent(self, task_id: str, task_description: str, label: str):
        config = load_config()
        skinskill_hud_notify(f"🤖 Subagente [{task_id}] começou a trabalhar no plano...", "info")
        
        system_prompt = f"""# Subagente
Você é um subagente focado em completar uma tarefa de programação.
Seu workspace atual é: {self.workspace.absolute()}

## Instruções
Você deve atingir o objetivo solicitado. Se precisar ler arquivos, criar arquivos ou rodar comandos, envie sua intenção usando as tags estruturadas abaixo no final da sua mensagem:

1. Para ler um arquivo:
[FILE_READ: caminho_do_arquivo]

2. Para criar/sobrescrever um arquivo:
[FILE_WRITE: caminho_do_arquivo]
CONTEÚDO_DO_ARQUIVO
[/FILE_WRITE]

3. Para rodar um comando de terminal:
[EXEC_CMD: comando]

A cada iteração, você pode chamar apenas UMA ferramenta. Aguarde o retorno do sistema com o output antes de continuar.
Quando concluir o objetivo, responda com uma mensagem curta iniciando com "CONCLUÍDO: " e o resumo dos seus resultados.
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_description}
        ]
        
        max_iterations = 10
        iteration = 0
        success = False
        result_text = ""
        
        while iteration < max_iterations:
            iteration += 1
            try:
                # Chama a LLM
                response_text = await self._call_llm_async(messages, config)
                messages.append({"role": "assistant", "content": response_text})
                
                # Verifica conclusão
                if "CONCLUÍDO:" in response_text:
                    success = True
                    result_text = response_text
                    break
                
                # Processamento de Ferramentas
                tool_output = ""
                
                # 1. FILE_READ
                read_match = re_search(r'\[FILE_READ:\s*(.*?)\]', response_text)
                if read_match:
                    filepath = self.workspace / read_match.group(1).strip()
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            tool_output = f"=== FILE CONTENT OF {read_match.group(1)} ===\n{f.read()}"
                    except Exception as e:
                        tool_output = f"Erro ao ler arquivo: {str(e)}"
                
                # 2. FILE_WRITE
                elif "[FILE_WRITE:" in response_text and "[/FILE_WRITE]" in response_text:
                    try:
                        header_part, content_part = response_text.split("[/FILE_WRITE]", 1)
                        filepath_str = header_part.split("[FILE_WRITE:", 1)[1].split("]", 1)[0].strip()
                        file_content = header_part.split("]", 1)[1]
                        filepath = self.workspace / filepath_str
                        filepath.parent.mkdir(parents=True, exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(file_content)
                        tool_output = f"Arquivo {filepath_str} criado com sucesso."
                    except Exception as e:
                        tool_output = f"Erro ao escrever arquivo: {str(e)}"
                
                # 3. EXEC_CMD
                elif "[EXEC_CMD:" in response_text:
                    cmd_str = response_text.split("[EXEC_CMD:", 1)[1].split("]", 1)[0].strip()
                    try:
                        # Executa comando de forma segura
                        proc = await asyncio.create_subprocess_shell(
                            cmd_str,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            cwd=str(self.workspace)
                        )
                        stdout, stderr = await proc.communicate()
                        tool_output = f"Comando rodado: {cmd_str}\nExit Code: {proc.returncode}\nSTDOUT:\n{stdout.decode('utf-8', errors='ignore')}\nSTDERR:\n{stderr.decode('utf-8', errors='ignore')}"
                    except Exception as e:
                        tool_output = f"Erro ao rodar comando: {str(e)}"
                
                if tool_output:
                    messages.append({"role": "user", "content": tool_output})
                else:
                    # Se o modelo respondeu sem ferramenta e sem CONCLUÍDO, pede para ele continuar
                    messages.append({"role": "user", "content": "Por favor, execute o próximo passo ou retorne a resposta final com 'CONCLUÍDO:'"})
                    
            except Exception as e:
                result_text = f"Falha na execução do subagente: {str(e)}"
                break
                
        if success:
            skinskill_hud_notify(f"✅ Subagente [{label}] concluiu a tarefa!", "success")
        else:
            skinskill_hud_notify(f"❌ Subagente [{label}] falhou ou atingiu limite de iterações.", "error")
            
        # Grava resultado em log de status local
        status_dir = Path(".skinskill/subagents")
        status_dir.mkdir(parents=True, exist_ok=True)
        with open(status_dir / f"{task_id}.json", "w", encoding="utf-8") as f:
            json.dump({
                "label": label,
                "task": task_description,
                "success": success,
                "result": result_text or "Limite de iterações atingido"
            }, f, indent=2)

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
            raise ValueError("Chave de API não configurada.")

def re_search(pattern, text):
    import re
    return re.search(pattern, text)
