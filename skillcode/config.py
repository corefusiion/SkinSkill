import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path(".skinskill")
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "GEMINI_API_KEY": "",
    "CLAUDE_API_KEY": "",
    "OPENROUTER_API_KEY": "",
    "DEFAULT_MODEL": "openrouter/google/gemini-2.0-flash:free",
    "TELEGRAM_BOT_TOKEN": "",
    "DISCORD_BOT_TOKEN": "",
    "SLACK_BOT_TOKEN": "",
    "SLACK_APP_TOKEN": "",
    "GATEWAY_AUTH_TOKEN": "skillcode-secure-default-token-xyz123"
}

def load_config() -> dict:
    """Carrega as configurações unificando o arquivo local e variáveis do .env/SO."""
    config = DEFAULT_CONFIG.copy()
    
    # 1. Carrega do config.json se existir
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception:
            pass
            
    # 2. Carrega das variáveis de ambiente (.env ou SO) como override
    for key in config.keys():
        env_val = os.getenv(key)
        if env_val:
            config[key] = env_val
            
    return config

def save_config(config_data: dict) -> None:
    """Salva as configurações no arquivo config.json local."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Filtra chaves válidas
    filtered = {k: v for k, v in config_data.items() if k in DEFAULT_CONFIG}
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)
        
    # Também sincroniza com o arquivo .env local para compatibilidade
    env_lines = []
    for k, v in filtered.items():
        if v:
            env_lines.append(f"{k}={v}")
            
    # Escreve ou atualiza o .env
    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines) + "\n")
