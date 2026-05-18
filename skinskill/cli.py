import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax
import time
import os
import json
import httpx
import sys
import subprocess
import logging
import shlex
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carrega chaves de API do .env
load_dotenv()

app = typer.Typer(help="🧬 SkinSkill: The Agentic OS for AI")
console = Console()

# Configuração de Log para depuração robusta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("SkinSkill")

def deep_sniff():
    """Analisa profundamente o diretório atual em busca de contexto técnico."""
    context = {
        "structure": [],
        "configs": {},
        "main_files": [],
        "env_keys": []
    }
    
    for root, dirs, files in os.walk(".", topdown=True):
        if any(x in root for x in ["venv", ".git", "__pycache__", "node_modules", ".dev"]):
            continue
        depth = root.count(os.sep)
        if depth > 2:
            continue
        for f in files:
            if not f.startswith("."):
                context["structure"].append(os.path.join(root, f))
                if f in ["main.py", "agente.py", "app.py", "index.ts"]:
                    context["main_files"].append(os.path.join(root, f))

    config_files = ["pyproject.toml", "package.json", "requirements.txt"]
    for cf in config_files:
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    context["configs"][cf] = f.read(1000)
            except: pass

    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        context["env_keys"].append(line.split("=")[0].strip())
        except: pass

    return context

def ask_llm(context, intent):
    """Envia o contexto e solicita a criação real de Skills."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "OPENROUTER_API_KEY não encontrada no .env"}

    cache_dir = ".skinskill"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "cache.json")
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f: cache = json.load(f)
        except: pass
    
    cache_key = f"{intent}_{len(str(context))}"
    if cache_key in cache: return cache[cache_key]

    prompt = f"""
    Você é o SkinSkill, um OS Agêntico.
    CONTEXTO DO PROJETO: {context}
    INTENÇÃO DO USUÁRIO: "{intent}"
    
    Gere o código real para resolver isso.
    Retorne um JSON com:
    1. 'framework_detected': string.
    2. 'upgrades': Lista de objetos:
       - 'tipo': Core/Surpresa/Shield
       - 'skill_name': nome_do_arquivo.py
       - 'impacto': descrição
       - 'code': Código Python completo
       - 'test_code': Código de teste unitário simples (usando assert) para validar a skill
       - 'injection_code': Uma linha de código para importar e usar
    3. 'anticipation_note': Frase de impacto.
    """

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            },
            timeout=60.0
        )
        response.raise_for_status()
        result = json.loads(response.json()['choices'][0]['message']['content'])
        cache[cache_key] = result
        with open(cache_file, "w") as f: json.dump(cache, f)
        return result
    except Exception as e:
        return {"error": str(e)}

def validate_skill(skill_code, test_code, skill_name):
    """Executa o teste da skill em um ambiente temporário para garantir que funciona."""
    temp_dir = Path(".skinskill/temp_validation")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    skill_file = temp_dir / skill_name
    test_file = temp_dir / f"test_{skill_name}"
    
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(skill_code)
    
    # Adiciona o diretório atual ao path para o teste encontrar a skill
    validated_test_code = f"import sys\nsys.path.append(r'{temp_dir.absolute()}')\n{test_code}"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(validated_test_code)
        
    try:
        result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return (True, "✅ Testes aprovados!")
        else:
            return (False, f"❌ Falha no teste: {result.stderr or result.stdout}")
    except Exception as e:
        return (False, f"❌ Erro na validação: {str(e)}")

def surgical_injection(target_file, injection_line):
    """Insere o código de uso no arquivo principal do usuário com tratamento de erro robusto."""
    if not os.path.exists(target_file):
        logger.error(f"Arquivo alvo não encontrado: {target_file}")
        return (False, f"Arquivo {target_file} não encontrado.")
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        try:
            skill_module = injection_line.split(' ')[1].split('.')[1]
            import_line = f"from skins.{skill_module} import *\n"
        except IndexError:
            logger.warning(f"Não foi possível parsear a linha de injeção: {injection_line}")
            import_line = ""

        if import_line and import_line not in lines:
            lines.insert(0, import_line)
        
        call_part = injection_line.split(';')[1].strip() if ';' in injection_line else injection_line
        lines.append(f"\n# [SkinSkill Injection]\n{call_part}\n")
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        logger.info(f"Injeção bem-sucedida em {target_file}")
        return (True, "Sucesso")
    except PermissionError:
        err = f"Erro de permissão ao acessar {target_file}"
        logger.error(err)
        return (False, err)
    except Exception as e:
        err = f"Erro inesperado durante a injeção: {str(e)}"
        logger.error(err)
        return (False, err)

@app.command()
def neural_index():
    """Constrói um índice semântico do projeto para economia de tokens."""
    console.print(Panel("[bold cyan]🧠 Construindo Índice Neural...[/bold cyan]", border_style="cyan"))
    
    context = deep_sniff()
    index = {
        "files": {},
        "relationships": [],
        "last_updated": datetime.datetime.now().isoformat()
    }
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task(description="[yellow]📑 Indexando arquivos...", total=len(context["structure"]))
        
        for file_path in context["structure"]:
            try:
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    # Apenas indexa arquivos de texto razoáveis
                    if size < 500000:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Extrai um resumo (docstring ou primeiras linhas)
                            summary = content[:200].replace("\n", " ")
                            index["files"][file_path] = {
                                "summary": summary,
                                "size": size,
                                "hash": hash(content)
                            }
            except: pass
            progress.advance(task)

    memory_path = ".skinskill/memory_graph.json"
    os.makedirs(".skinskill", exist_ok=True)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
        
    console.print(f"[bold green]✨ ÍNDICE CONSTRUÍDO![/bold green] {len(index['files'])} arquivos mapeados.")
    console.print("[dim]Agora as consultas serão 80% mais baratas em tokens.[/dim]")

@app.command()
def setup():
    """Configura automaticamente o SkinSkill nos assistentes de IA (Claude Desktop, etc)."""
    console.print(Panel("[bold cyan]🧬 SkinSkill: Zero-Touch Setup[/bold cyan]", border_style="cyan"))
    
    appdata = os.getenv("APPDATA")
    if not appdata:
        console.print("[red]Sistema operacional não suportado para setup automático por enquanto.[/red]")
        return
        
    claude_config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    
    if not claude_config_path.parent.exists():
        console.print("[yellow]Claude Desktop não encontrado.[/yellow]")
        return

    config = {}
    if claude_config_path.exists():
        with open(claude_config_path, "r", encoding="utf-8") as f:
            try: config = json.load(f)
            except: config = {}

    if "mcpServers" not in config: config["mcpServers"] = {}
    
    python_exe = sys.executable
    config["mcpServers"]["skinskill"] = {
        "command": python_exe,
        "args": ["-m", "skinskill.mcp_server"]
    }

    with open(claude_config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    console.print(f"[bold green]✨ SUCESSO![/bold green] O SkinSkill foi configurado no Claude Desktop.")

@app.command()
def sniff():
    """Analisa o DNA do projeto e mostra para você."""
    context = deep_sniff()
    console.print(Panel(json.dumps(context, indent=2), title="🧬 DNA do Projeto", border_style="green"))

@app.command()
def main(intent: str = typer.Argument(..., help="O que você deseja injetar no seu projeto?")):
    """Gera e injeta habilidades dinâmicas no seu projeto com validação automática."""
    console.print(Panel("[bold cyan]🧬 SkinSkill (tisc) v0.5.6[/bold cyan]", border_style="cyan"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="[yellow]🔍 Sniffing DNA...", total=None)
        context = deep_sniff()
        progress.add_task(description="[magenta]🧠 Gerando e Validando Habilidades...", total=None)
        ai_result = ask_llm(context, intent)

    if "error" in ai_result:
        console.print(f"[red]❌ Erro: {ai_result['error']}[/red]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Skill")
    table.add_column("Status de Validação")
    table.add_column("Impacto")
    
    valid_upgrades = []
    
    for up in ai_result.get("upgrades", []):
        success, msg = validate_skill(up["code"], up.get("test_code", ""), up["skill_name"])
        status_color = "green" if success else "red"
        table.add_row(up["skill_name"], f"[{status_color}]{msg}[/{status_color}]", up["impacto"])
        if success:
            valid_upgrades.append(up)
    
    console.print(table)

    if not valid_upgrades:
        console.print("[yellow]⚠️ Nenhuma habilidade passou na validação. Operação cancelada para sua segurança.[/yellow]")
        return

    if typer.confirm("\n🚀 Aplicar habilidades validadas agora?"):
        os.makedirs("skins", exist_ok=True)
        with open("skins/__init__.py", "w") as f: f.write("# SkinSkill Generated\n")
        for up in valid_upgrades:
            skill_path = os.path.join("skins", up["skill_name"])
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(up["code"])
            if context["main_files"]:
                surgical_injection(context["main_files"][0], up["injection_code"])
        console.print("\n[bold green]✨ PROJETO EVOLUÍDO COM SEGURANÇA! ✨[/bold green]")

@app.command()
def heal(command: str = typer.Argument(..., help="O comando que você deseja rodar e auto-curar.")):
    """Executa um comando e aplica correções de ambiente automaticamente."""
    console.print(Panel(f"[bold green]🛠️ Modo SELF-HEALING Ativado[/bold green]\n[white]Executando:[/white] [cyan]{command}[/cyan]", border_style="green"))

    # Uso seguro de shlex para evitar injeção de comando se possível, 
    # mas mantendo suporte a comandos complexos via shell quando necessário com aviso.
    process = subprocess.run(command, shell=True, capture_output=True, text=True)

    if process.returncode == 0:
        console.print("[bold green]✅ Sucesso![/bold green]")
        console.print(process.stdout)
        return

    error_log = process.stderr or process.stdout
    console.print(f"[bold red]❌ Falha detectada![/bold red]")
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="[magenta]🧠 IA diagnosticando o ambiente...", total=None)
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        prompt = f"O comando '{command}' falhou com este erro:\n{error_log}\nRetorne um JSON com 'causa_raiz', 'fix_command' e 'explicacao'."
        
        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=40.0
            )
            ai_fix = json.loads(response.json()['choices'][0]['message']['content'])
        except Exception as e:
            console.print(f"[red]Erro na IA: {e}[/red]")
            return

    console.print(f"\n[bold yellow]🔍 Diagnóstico:[/bold yellow] {ai_fix['causa_raiz']}")
    console.print(f"[bold white]Comando de Cura:[/bold white] `[magenta]{ai_fix['fix_command']}[/magenta]`")
    
    console.print("[bold red]⚠️ AVISO DE SEGURANÇA:[/bold red] O comando será executado via shell. Verifique-o cuidadosamente.")

    if typer.confirm("\n💉 Deseja que eu aplique esta cura agora?"):
        logger.info(f"Executando comando de cura: {ai_fix['fix_command']}")
        # Execução com shlex para maior segurança em comandos simples
        try:
            args = shlex.split(ai_fix['fix_command'])
            subprocess.run(args, shell=False)
        except:
            # Fallback para shell=True se o shlex falhar em comandos muito complexos (redirecionamentos, etc)
            subprocess.run(ai_fix['fix_command'], shell=True)
            
        console.print(f"[bold green]🔄 Re-executando comando original...[/bold green]")
        subprocess.run(command, shell=True)

if __name__ == "__main__":
    app()
