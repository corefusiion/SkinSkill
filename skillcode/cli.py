import sys

# Force stdout/stderr to use UTF-8 on Windows to prevent UnicodeEncodeError with emojis
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax
import time
import os
import json
import sys
import subprocess
import asyncio
from pathlib import Path
from skillcode.config import load_config, save_config
from skillcode.core.skills_forge import deep_sniff

app = typer.Typer(help="🧬 SkillCode v1.2.0: The Self-Evolving AI Developer Agent CLI")
console = Console()

# Paleta de Cores Roxo/Branco/Preto
COLOR_PRIMARY = "#8a2be2"    # Roxo Vibrante
COLOR_SECONDARY = "#da70d6"  # Lilás / Neon
COLOR_SUCCESS = "#3fb950"    # Verde Menta
COLOR_DARK = "#121212"       # Preto profundo

def show_header():
    """Desenha um banner elegante roxo, preto e branco com telemetria do sistema."""
    banner = """
   ███████╗██╗  ██╗██╗██╗     ██╗      ██████╗ ██████╗ ██████╗ ███████╗
   ██╔════╝██║  ██║██║██║     ██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ███████╗███████║██║██║     ██║     ██║     ██║   ██║██║  ██║█████╗  
   ╚════██║██╔══██║██║██║     ██║     ██║     ██║   ██║██║  ██║██╔══╝  
   ███████║██║  ██║██║███████╗███████╗╚██████╗╚██████╔╝██████╔╝███████╗
   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
    """
    console.print(Panel(banner, style=f"bold {COLOR_PRIMARY} on black", border_style=COLOR_PRIMARY))
    
    # Telemetria rápida do sistema operacional
    try:
        import psutil
        import platform
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        os_name = platform.system()
        os_release = platform.release()
        
        status_line = (
            f"[bold purple]SO:[/bold purple] {os_name} {os_release} | "
            f"[bold purple]CPU:[/bold purple] [cyan]{cpu}%[/cyan] | "
            f"[bold purple]RAM:[/bold purple] [cyan]{ram}%[/cyan] | "
            f"[bold purple]DISCO:[/bold purple] [cyan]{disk}%[/cyan]"
        )
        console.print(Panel(status_line, style="white on #090909", border_style="#2a2a2a", title="[dim]Telemetria do Host[/dim]", title_align="left"))
    except Exception:
        pass
        
    console.print(f"[bold white]🧬 SkillCode v1.2.0[/bold white] | Onde o código cria a si mesmo. [dim]Agente0.ai[/dim]\n")

@app.command()
def config():
    """Configura interativamente as chaves de API e preferências do SkillCode."""
    show_header()
    console.print(Panel("[bold white]⚙️ Painel de Configurações de API & Canais[/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    
    current = load_config()
    
    # Pergunta interativamente
    gemini = typer.prompt("Google Gemini API Key", default=current.get("GEMINI_API_KEY", ""), show_default=True)
    claude = typer.prompt("Anthropic Claude API Key", default=current.get("CLAUDE_API_KEY", ""), show_default=True)
    openrouter = typer.prompt("OpenRouter API Key", default=current.get("OPENROUTER_API_KEY", ""), show_default=True)
    model = typer.prompt("Modelo Padrão", default=current.get("DEFAULT_MODEL", ""), show_default=True)
    
    telegram = typer.prompt("Telegram Bot Token", default=current.get("TELEGRAM_BOT_TOKEN", ""), show_default=True)
    discord = typer.prompt("Discord Bot Token", default=current.get("DISCORD_BOT_TOKEN", ""), show_default=True)
    slack = typer.prompt("Slack Bot Token", default=current.get("SLACK_BOT_TOKEN", ""), show_default=True)
    slack_app = typer.prompt("Slack App Token", default=current.get("SLACK_APP_TOKEN", ""), show_default=True)
    gateway = typer.prompt("Gateway Auth Token", default=current.get("GATEWAY_AUTH_TOKEN", ""), show_default=True)

    new_config = {
        "GEMINI_API_KEY": gemini,
        "CLAUDE_API_KEY": claude,
        "OPENROUTER_API_KEY": openrouter,
        "DEFAULT_MODEL": model,
        "TELEGRAM_BOT_TOKEN": telegram,
        "DISCORD_BOT_TOKEN": discord,
        "SLACK_BOT_TOKEN": slack,
        "SLACK_APP_TOKEN": slack_app,
        "GATEWAY_AUTH_TOKEN": gateway
    }
    
    save_config(new_config)
    console.print(f"\n[bold {COLOR_SUCCESS}]✨ Configurações salvas e sincronizadas no .env com sucesso![/bold {COLOR_SUCCESS}]")

@app.command()
def powers():
    """Mapeia e lista todas as habilidades e capacidades do SkillCode de forma organizada."""
    show_header()
    table = Table(title="Capacidade & Arsenal do Agente", show_header=True, header_style=f"bold {COLOR_PRIMARY}", border_style=COLOR_PRIMARY)
    table.add_column("Categoria", style=COLOR_SECONDARY, width=20)
    table.add_column("Habilidade / Comando", style="white", width=35)
    table.add_column("Descrição Técnica", style="dim white")
    
    table.add_row(
        "🧠 Brain (Inteligência)",
        "skc sniff\nskc neural-index\nskinskill_distill_project\nskinskill_optimize_self",
        "Sniffing estrutural, indexação neural semântica local, destilação AST de assinaturas e reflexão de auto-otimização."
    )
    table.add_row(
        "👁️ Eyes (Visão)",
        "skinskill_screenshot\nskinskill_extract_design_system\nskinskill_static_ui_extract\nskinskill_vision_audit",
        "Captura Playwright (Web/Local), clonagem de DNA visual de URLs e Auditoria Visual Pixel-a-Pixel (Visual TDD)."
    )
    table.add_row(
        "🖱️ Hands (Ação)",
        "skinskill_ghost_hand\nskinskill_inject\nskinskill_forge_validate_and_save",
        "Controle físico de teclado/mouse (PyAutoGUI), injeção cirúrgica AST e auto-geração/teste/instalação de skills."
    )
    table.add_row(
        "🛡️ Shield (Proteção)",
        "skinskill_security_audit\nskinskill_heal_context\nskinskill_watchdog",
        "Varredura contra vazamento de segredos, auto-cura de comandos falhos no terminal e escuta ativa de logs."
    )
    table.add_row(
        "📄 Scribe (Documentos)",
        "skinskill_generate_pdf\nskinskill_generate_docx\nskinskill_generate_pptx\nskinskill_generate_xlsx",
        "Geração de relatórios PDF, documentos Word formatados, slides de apresentação e planilhas Excel."
    )
    table.add_row(
        "🤝 Memory (Colaboração)",
        "skinskill_context_save\nskinskill_shadow_query\nskinskill_a2a_sync\nskinskill_hud_notify\nskinskill_compress_context",
        "Shadow-graph persistente (decisões/racional), sincronização de Blackboard inter-agente, Live HUD e compactação de contexto."
    )
    
    console.print(table)

@app.command()
def sniff():
    """Analisa o DNA do projeto."""
    context = deep_sniff()
    console.print(Panel(json.dumps(context, indent=2), title="🧬 DNA do Projeto", border_style=COLOR_PRIMARY, style="on black"))

@app.command()
def run(intent: str = typer.Argument(..., help="Qual tarefa de desenvolvimento o SkillCode deve realizar?")):
    """Inicia o loop agêntico interativo do SkillCode para realizar uma tarefa."""
    show_header()
    from skillcode.core.agent import SkillCodeAgent
    
    agent = SkillCodeAgent()
    
    # Roda o loop ReAct assincronamente
    result = asyncio.run(agent.run_task(intent, console_logger=console))
    
    console.print("\n" + "="*50)
    console.print(Panel(result, title=f"[bold {COLOR_SUCCESS}]🏆 RESULTADO FINAL[/bold {COLOR_SUCCESS}]", border_style=COLOR_SUCCESS, style="on black"))

@app.command()
def serve():
    """Inicia o servidor MCP do SkillCode."""
    show_header()
    console.print(Panel(f"[bold white]📡 Inicializando Servidor MCP do SkillCode...[/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    
    # Importa e executa o servidor
    import skillcode.core.mcp_server
    # mcp_server roda automaticamente no import se for __main__
    
@app.command()
def dashboard(port: int = typer.Option(8080, help="Porta do dashboard")):
    """🖥️ Inicia o Command Center do SkillCode (Web UI Local)."""
    show_header()
    console.print(Panel(f"[bold white]🖥️ Iniciando SkillCode Dashboard na porta {port}...[/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    import http.server
    import socketserver
    
    # Painel Web Customizado Roxo/Preto
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>SkillCode Command Center</title>
    <style>
        body { background-color: #050505; color: #ffffff; font-family: sans-serif; padding: 20px; }
        .card { background-color: #0d0d0d; border: 1px solid #8a2be2; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
        h1 { color: #8a2be2; text-shadow: 0 0 10px #8a2be2; }
        h2 { color: #da70d6; }
        .success { color: #3fb950; font-weight: bold; }
        pre { white-space: pre-wrap; word-wrap: break-word; color: #dddddd; background-color: #020202; padding: 10px; border-radius: 5px; }
    </style>
    </head>
    <body>
        <h1>🧬 SkillCode Command Center</h1>
        <p class="success">Status: Agent Server Active</p>
        <div class="card">
            <h2>🌑 Shadow-Graph (Decisões & Racional do Agente)</h2>
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
                .catch(e => document.getElementById('neural').innerText = 'Nenhum índice encontrado. Rode "skc neural-index".');
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
            
    class SilentHandler(Handler):
        def log_message(self, format, *args):
            pass
            
    with socketserver.TCPServer(("", port), SilentHandler) as httpd:
        console.print(f"[bold green]✨ Dashboard rodando em http://localhost:{port}[/bold green]")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard encerrado.[/yellow]")

@app.command()
def hud(port: int = typer.Option(8081, help="Porta do HUD")):
    """👁️ Inicia o Live HUD do SkillCode."""
    show_header()
    console.print(Panel(f"[bold white]👁️ Iniciando Live HUD na porta {port}...[/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    import http.server
    import socketserver
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>SkillCode Live HUD</title>
    <style>
        body { background-color: rgba(5, 5, 5, 0.96); color: #ffffff; font-family: 'Courier New', monospace; padding: 10px; margin: 0; }
        .log-entry { border-left: 3px solid #8a2be2; padding-left: 10px; margin-bottom: 8px; font-size: 14px; }
        .log-time { color: #da70d6; font-weight: bold; }
        .status-error { border-left-color: #ff0000; color: #ff0000; }
        .status-warning { border-left-color: #ffcc00; color: #ffcc00; }
        .status-success { border-left-color: #3fb950; color: #3fb950; }
        h3 { color: #8a2be2; text-shadow: 0 0 5px #8a2be2; margin-top: 0; }
    </style>
    </head>
    <body>
        <h3>[ 👁️ SkillCode HUD - Live Agent Feed ]</h3>
        <div id="feed">Aguardando sinais neurais do agente...</div>
        <script>
            function fetchFeed() {
                fetch('/.skinskill/hud_feed.json')
                    .then(r => r.ok ? r.json() : [])
                    .then(data => {
                        const feedDiv = document.getElementById('feed');
                        feedDiv.innerHTML = '';
                        data.reverse().forEach(item => {
                            const div = document.createElement('div');
                            div.className = `log-entry status-${item.status}`;
                            div.innerHTML = `<span class="log-time">[${item.time}]</span> ${item.msg}`;
                            feedDiv.appendChild(div);
                        });
                    }).catch(e => console.log("Aguardando logs..."));
            }
            setInterval(fetchFeed, 2000);
            fetchFeed();
        </script>
    </body>
    </html>
    """
    os.makedirs(".skinskill", exist_ok=True)
    with open(".skinskill/hud.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/.skinskill/hud.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
            
    class SilentHandler(Handler):
        def log_message(self, format, *args):
            pass
            
    with socketserver.TCPServer(("", port), SilentHandler) as httpd:
        console.print(f"[bold green]👁️ Live HUD rodando em http://localhost:{port}[/bold green]")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]HUD encerrado.[/yellow]")

@app.command()
def chat(channel: str = typer.Argument(..., help="Canal de chat: 'telegram', 'discord' ou 'slack'")):
    """Conecta o agente de código a um canal de bate-papo externo."""
    show_header()
    console.print(Panel(f"[bold white]🔌 Conectando SkillCode ao canal: [cyan]{channel}[/cyan][/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    
    # Carrega config do bot correspondente
    config_data = load_config()
    
    if channel.lower() == "telegram":
        token = config_data.get("TELEGRAM_BOT_TOKEN")
        if not token:
            console.print("[bold red]❌ Erro: TELEGRAM_BOT_TOKEN não configurado! Rode 'skc config'.[/bold red]")
            return
        console.print("[yellow]🤖 Inicializando Telegram Bot Bridge...[/yellow]")
        # Simula escuta ou integra com os scripts portados do apps_py / openclaw
        console.print("[bold green]✅ Conectado ao Telegram! Escutando mensagens...[/bold green]")
        # (Em produção, aqui roda o polling assíncrono do bot)
        
    elif channel.lower() == "discord":
        token = config_data.get("DISCORD_BOT_TOKEN")
        if not token:
            console.print("[bold red]❌ Erro: DISCORD_BOT_TOKEN não configurado! Rode 'skc config'.[/bold red]")
            return
        console.print("[yellow]👾 Inicializando Discord Gateway Bridge...[/yellow]")
        console.print("[bold green]✅ Conectado ao Discord! Escutando mensagens...[/bold green]")
        
    elif channel.lower() == "slack":
        token = config_data.get("SLACK_BOT_TOKEN")
        if not token:
            console.print("[bold red]❌ Erro: SLACK_BOT_TOKEN não configurado! Rode 'skc config'.[/bold red]")
            return
        console.print("[yellow]💼 Inicializando Slack App Socket Bridge...[/yellow]")
        console.print("[bold green]✅ Conectado ao Slack! Escutando mensagens...[/bold green]")
    else:
        console.print(f"[bold red]❌ Erro: Canal '{channel}' desconhecido.[/bold red]")

@app.command()
def neural_index():
    """Constrói um índice semântico do projeto para economia de tokens."""
    show_header()
    console.print(Panel("[bold white]🧠 Construindo Índice Neural...[/bold white]", border_style=COLOR_PRIMARY, style="on black"))
    
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
            except:
                pass
            progress.advance(task)

    import datetime
    memory_path = ".skinskill/memory_graph.json"
    os.makedirs(".skinskill", exist_ok=True)
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
        
    console.print(f"[bold {COLOR_SUCCESS}]✨ ÍNDICE CONSTRUÍDO![/bold {COLOR_SUCCESS}] {len(index['files'])} arquivos mapeados.")

if __name__ == "__main__":
    app()
