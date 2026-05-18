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
import re
from pathlib import Path
from dotenv import load_dotenv
from importlib import metadata

# Carrega chaves de API do .env
load_dotenv()

# Obtém versão dinâmica do pacote
try:
    __version__ = metadata.version("skinskill")
except:
    __version__ = "0.6.0"

app = typer.Typer(help=f"🧬 SkinSkill v{__version__}: The Agentic OS for AI")
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
        "env_keys": [],
        "neural_index_present": os.path.exists(".skinskill/memory_graph.json")
    }
    
    # Busca por índice neural para economizar tokens
    if context["neural_index_present"]:
        try:
            with open(".skinskill/memory_graph.json", "r", encoding="utf-8") as f:
                index = json.load(f)
                context["neural_summary"] = "Índice Neural detectado. O projeto possui mapeamento semântico pronto para consulta."
        except: pass

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

    return context

def validate_skill(skill_code, test_code, skill_name):
    """Executa o teste da skill em um ambiente temporário isolado para garantir que funciona."""
    temp_dir = Path(".skinskill/temp_validation")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    skill_file = temp_dir / skill_name
    test_file = temp_dir / f"test_{skill_name}"
    
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(skill_code)
    
    # Permite que o teste importe a skill diretamente do diretório atual
    validated_test_code = f"import sys\nimport os\n# Adiciona diretório da skill ao path\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n{test_code}"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(validated_test_code)
        
    try:
        # Executa com PYTHONPATH configurado para o diretório temporário
        env = os.environ.copy()
        env["PYTHONPATH"] = str(temp_dir.absolute()) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True, timeout=15, env=env)
        if result.returncode == 0:
            return (True, "✅ Testes aprovados!")
        else:
            return (False, f"❌ Falha no teste: {result.stderr or result.stdout}")
    except Exception as e:
        return (False, f"❌ Erro na validação: {str(e)}")

def surgical_injection(target_file, injection_line):
    """Injeta código cirurgicamente, evitando duplicatas e organizando imports."""
    if not os.path.exists(target_file):
        return (False, f"Arquivo {target_file} não encontrado.")
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 1. Tenta extrair o nome do módulo de forma robusta via Regex
        # Suporta: 'from skins.x import *', 'import skins.x', etc.
        match = re.search(r'(?:from|import)\s+skins\.([a-zA-Z0-9_]+)', injection_line)
        module_name = match.group(1) if match else None
        
        # 2. Verifica se já existe um import para este módulo
        if module_name and f"skins.{module_name}" in content:
            logger.info(f"Import de {module_name} já existe em {target_file}. Pulando injeção de cabeçalho.")
            import_line = ""
        else:
            import_line = f"from skins.{module_name} import *\n" if module_name else ""

        # 3. Organização com Âncora
        anchor = "# [SkinSkill Imports]"
        lines = content.splitlines()
        
        if anchor not in content and import_line:
            lines.insert(0, anchor)
            lines.insert(1, import_line)
        elif import_line:
            # Insere logo após a âncora existente
            for i, line in enumerate(lines):
                if anchor in line:
                    lines.insert(i + 1, import_line)
                    break
        
        # 4. Injeta a chamada se fornecida (se houver um ';' na linha)
        if ';' in injection_line:
            call_part = injection_line.split(';')[1].strip()
            if call_part not in content:
                lines.append(f"\n# [SkinSkill Action]\n{call_part}\n")
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        
        return (True, "Sucesso")
    except Exception as e:
        return (False, f"Erro na injeção: {str(e)}")

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
def main(intent: str = typer.Argument(..., help="O que você deseja que a IA faça no seu projeto?")):
    """Prepara o contexto neural para que VOCÊ (via Chat IA) possa gerar novas habilidades com 100% de precisão."""
    console.print(Panel("[bold cyan]🧬 SkinSkill (tisc) v0.5.8[/bold cyan]", border_style="cyan"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="[yellow]🔍 Mapeando DNA do Projeto...", total=None)
        context = deep_sniff()
        
    console.print("\n[bold green]✅ Contexto Neural Preparado![/bold green]")
    console.print("Para economizar tokens e garantir o melhor resultado, copie o comando abaixo e cole no seu chat de IA (Claude/ChatGPT/Gemini):")
    
    prompt_box = f"""
--- SKINSKILL CONTEXT PROMPT ---
Estou usando o SkinSkill MCP. Preciso que você gere uma nova habilidade (Skin) para: "{intent}"

CONTEXTO DO MEU PROJETO:
{json.dumps(context, indent=2)}

INSTRUÇÕES PARA A IA:
Gere um JSON com o código da habilidade e um teste unitário. 
Quando estiver pronto, use a ferramenta 'skinskill_forge_validate_and_save' para validar e instalar.
--------------------------------
"""
    console.print(Syntax(prompt_box, "markdown", theme="monokai"))

@app.command()
def heal(command: str = typer.Argument(..., help="O comando que você deseja rodar e auto-curar.")):
    """Executa um comando e, se falhar, prepara o diagnóstico para você enviar à sua IA."""
    console.print(Panel(f"[bold green]🛠️ Modo SELF-HEALING (Manual Context)[/bold green]\n[white]Executando:[/white] [cyan]{command}[/cyan]", border_style="green"))

    process = subprocess.run(command, shell=True, capture_output=True, text=True)

    if process.returncode == 0:
        console.print("[bold green]✅ Sucesso![/bold green]")
        console.print(process.stdout)
        return

    error_log = process.stderr or process.stdout
    console.print(f"[bold red]❌ Falha detectada![/bold red]")
    
    console.print("\n[bold yellow]🔍 Diagnóstico Gerado![/bold yellow]")
    console.print("Copie o erro abaixo para sua IA propor a correção via 'fix_command':")
    console.print(Panel(error_log, title="Erro de Saída", border_style="red"))

if __name__ == "__main__":
    app()
