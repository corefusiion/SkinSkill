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
import ast
from pathlib import Path
from dotenv import load_dotenv
from importlib import metadata

# Carrega chaves de API do .env
load_dotenv()

# Obtém versão dinâmica do pacote
try:
    __version__ = metadata.version("skinskill")
except:
    __version__ = "0.7.0"

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
        # Usa sys.executable para evitar dependência de PATH global
        result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True, timeout=15, env=env)
        if result.returncode == 0:
            return (True, "✅ Testes aprovados!")
        else:
            return (False, f"❌ Falha no teste: {result.stderr or result.stdout}")
    except Exception as e:
        return (False, f"❌ Erro na validação: {str(e)}")

def surgical_injection(target_file, injection_line):
    """Injeta código usando AST para máxima precisão e segurança."""
    if not os.path.exists(target_file):
        return (False, f"Arquivo {target_file} não encontrado.")
    
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            source = f.read()
            
        tree = ast.parse(source)
        
        # 1. Extrai o módulo alvo do injection_line (ex: from skins.x import *)
        match = re.search(r'(?:from|import)\s+skins\.([a-zA-Z0-9_]+)', injection_line)
        module_name = match.group(1) if match else None
        
        # 2. Verifica se o import já existe via AST
        already_imported = False
        if module_name:
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == f"skins.{module_name}":
                    already_imported = True
                    break
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name == f"skins.{module_name}":
                            already_imported = True
                            break
                            
        lines = source.splitlines()
        
        # 3. Injeção de Cabeçalho (Import)
        if module_name and not already_imported:
            import_line = f"from skins.{module_name} import *"
            anchor = "# [SkinSkill Imports]"
            
            if anchor not in source:
                lines.insert(0, anchor)
                lines.insert(1, import_line)
            else:
                for i, line in enumerate(lines):
                    if anchor in line:
                        lines.insert(i + 1, import_line)
                        break
        
        # 4. Injeção de Ação (Call)
        if ';' in injection_line:
            call_part = injection_line.split(';')[1].strip()
            action_anchor = "# [SkinSkill Actions]"
            if call_part not in source:
                if action_anchor not in source:
                    lines.append(f"\n{action_anchor}")
                lines.append(call_part)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
            
        return (True, "Sucesso")
    except Exception as e:
        return (False, f"Falha na análise AST: {str(e)}")

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
                    if size < 500000:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
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

@app.command()
def setup(scope: str = typer.Option("global", "--scope", "-s", help="Escopo do setup: 'global' (usuário) ou 'local' (projeto).")):
    """Configura o SkinSkill nos assistentes de IA (Claude, Gemini CLI, etc)."""
    console.print(Panel(f"[bold cyan]🧬 SkinSkill Universal Setup (Scope: {scope})[/bold cyan]", border_style="cyan"))
    
    python_exe = sys.executable
    mcp_config = {
        "command": python_exe,
        "args": ["-m", "skinskill.mcp_server"]
    }

    # 1. Claude Desktop Setup
    appdata = os.getenv("APPDATA")
    if appdata:
        claude_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
        if claude_path.parent.exists():
            try:
                config = {}
                if claude_path.exists():
                    with open(claude_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                
                if "mcpServers" not in config: config["mcpServers"] = {}
                config["mcpServers"]["skinskill"] = mcp_config
                
                with open(claude_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                console.print("[green]✅ Configurado no Claude Desktop.[/green]")
            except Exception as e:
                console.print(f"[red]❌ Erro ao configurar Claude: {e}[/red]")

    # 2. Gemini CLI Setup
    home = Path.home()
    gemini_path = home / ".gemini" / "settings.json"
    if gemini_path.parent.exists() or scope == "global":
        try:
            gemini_path.parent.mkdir(parents=True, exist_ok=True)
            config = {}
            if gemini_path.exists():
                with open(gemini_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            if "mcpServers" not in config: config["mcpServers"] = {}
            config["mcpServers"]["skinskill"] = mcp_config
            
            with open(gemini_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            console.print("[green]✅ Configurado no Gemini CLI.[/green]")
        except Exception as e:
            console.print(f"[red]❌ Erro ao configurar Gemini CLI: {e}[/red]")

    # 3. Local Project Config (Cursor/Windsurf)
    if scope == "local":
        try:
            vscode_path = Path(".vscode")
            vscode_path.mkdir(exist_ok=True)
            # Apenas gera um snippet para o usuário copiar
            console.print("\n[yellow]💡 Para Cursor/Windsurf, adicione este MCP manualmente:[/yellow]")
            console.print(Syntax(json.dumps({"skinskill": mcp_config}, indent=2), "json"))
        except: pass

    console.print(f"\n[bold green]✨ PRONTO![/bold green] SkinSkill agora usa: [dim]{python_exe}[/dim]")

@app.command()
def sniff():
    """Analisa o DNA do projeto."""
    context = deep_sniff()
    console.print(Panel(json.dumps(context, indent=2), title="🧬 DNA do Projeto", border_style="green"))

@app.command()
def main(intent: str = typer.Argument(..., help="O que você deseja que a IA faça?")):
    """Orquestrador de Contexto Neural."""
    console.print(Panel(f"[bold cyan]🧬 SkinSkill v{__version__}[/bold cyan]", border_style="cyan"))
    context = deep_sniff()
    
    prompt_box = f"""
--- SKINSKILL CONTEXT ---
Intenção: "{intent}"
Contexto: {json.dumps(context, indent=2)}
Instrução: Gere a skill + teste e use 'skinskill_forge_validate_and_save'.
-------------------------
"""
    console.print(Syntax(prompt_box, "markdown", theme="monokai"))

@app.command()
def heal(command: str = typer.Argument(..., help="Comando a ser curado.")):
    """Diagnóstico de falhas de terminal."""
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode == 0:
        console.print("[bold green]✅ Sucesso![/bold green]")
        return
    console.print(Panel(process.stderr or process.stdout, title="Erro detectado", border_style="red"))

@app.command()
def dashboard(port: int = typer.Option(8080, help="Porta do dashboard")):
    """🖥️ Inicia o SkinSkill Command Center (Web UI Local)."""
    console.print(Panel(f"[bold cyan]🖥️ Iniciando SkinSkill Dashboard na porta {port}...[/bold cyan]", border_style="cyan"))
    import http.server
    import socketserver
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>SkinSkill Command Center</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; padding: 20px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        h1, h2 { color: #58a6ff; }
        .success { color: #3fb950; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
    </head>
    <body>
        <h1>🧬 SkinSkill Command Center</h1>
        <p class="success">Status: MCP Online & Monitorando</p>
        <div class="card">
            <h2>🌑 Shadow-Graph (Decisões & Racional)</h2>
            <pre id="shadow">Carregando...</pre>
        </div>
        <div class="card">
            <h2>🧠 Memória Neural (Index Semântico)</h2>
            <pre id="neural">Carregando...</pre>
        </div>
        <script>
            fetch('/.skinskill/shadow_graph.json')
                .then(r => r.ok ? r.json() : [])
                .then(d => document.getElementById('shadow').innerText = JSON.stringify(d, null, 2))
                .catch(e => document.getElementById('shadow').innerText = 'Nenhuma decisão registrada ainda.');
            fetch('/.skinskill/memory_graph.json')
                .then(r => r.ok ? r.json() : {})
                .then(d => document.getElementById('neural').innerText = JSON.stringify(d, null, 2))
                .catch(e => document.getElementById('neural').innerText = 'Nenhum índice encontrado. Rode "tisc neural-index".');
            
            // Auto-refresh a cada 5 segundos
            setInterval(() => { location.reload(); }, 5000);
        </script>
    </body>
    </html>
    """
    
    os.makedirs(".skinskill", exist_ok=True)
    with open(".skinskill/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/.skinskill/dashboard.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    # Supress logs no stdout para manter o terminal limpo
    class SilentHandler(Handler):
        def log_message(self, format, *args):
            pass

    with socketserver.TCPServer(("", port), SilentHandler) as httpd:
        console.print(f"[bold green]✨ Dashboard rodando em http://localhost:{port}[/bold green]")
        console.print("[dim]Pressione Ctrl+C para encerrar.[/dim]")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard encerrado.[/yellow]")

if __name__ == "__main__":
    app()
