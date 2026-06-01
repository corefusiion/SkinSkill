import os
import sys
import json
import re
import ast
import subprocess
import datetime
from pathlib import Path

def deep_sniff() -> dict:
    """Analisa profundamente o diretório atual em busca de contexto técnico."""
    context = {
        "structure": [],
        "configs": {},
        "main_files": [],
        "env_keys": [],
        "neural_index_present": os.path.exists(".skinskill/memory_graph.json")
    }
    
    if context["neural_index_present"]:
        try:
            with open(".skinskill/memory_graph.json", "r", encoding="utf-8") as f:
                index = json.load(f)
                context["neural_summary"] = "Índice Neural detectado. O projeto possui mapeamento semântico pronto."
        except:
            pass

    for root, dirs, files in os.walk(".", topdown=True):
        if any(x in root for x in ["venv", ".git", "__pycache__", "node_modules", ".dev", ".venv"]):
            continue
        depth = root.count(os.sep)
        if depth > 2:
            continue
        for f in files:
            if not f.startswith("."):
                rel_path = os.path.join(root, f)
                context["structure"].append(rel_path)
                if f in ["main.py", "agente.py", "app.py", "index.ts"]:
                    context["main_files"].append(rel_path)

    config_files = ["pyproject.toml", "package.json", "requirements.txt"]
    for cf in config_files:
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    context["configs"][cf] = f.read(1000)
            except:
                pass

    return context

def validate_skill(skill_code: str, test_code: str, skill_name: str) -> tuple[bool, str]:
    """Executa o teste da skill em um ambiente temporário isolado para garantir que funciona."""
    temp_dir = Path(".skinskill/temp_validation")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Adiciona __init__.py ao temp_dir
    init_file = temp_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        
    skill_file = temp_dir / skill_name
    test_file = temp_dir / f"test_{skill_name}"
    
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(skill_code)
    
    # Permite que o teste importe a skill diretamente do diretório temporário
    validated_test_code = (
        f"import sys\n"
        f"import os\n"
        f"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        f"{test_code}"
    )
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(validated_test_code)
        
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(temp_dir.absolute()) + os.pathsep + env.get("PYTHONPATH", "")
        # Desabilita buffers de output
        env["PYTHONUNBUFFERED"] = "1"
        
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        if result.returncode == 0:
            return (True, "✅ Testes aprovados com sucesso!")
        else:
            return (False, f"❌ Falha no teste:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    except Exception as e:
        return (False, f"❌ Erro na validação: {str(e)}")

def surgical_injection(target_file: str, injection_line: str) -> tuple[bool, str]:
    """Injeta código usando AST para máxima precisão e segurança no arquivo principal."""
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
