import os
from pathlib import Path
from typing import Any, List
from agno.tools import Toolkit

class FileSystemToolkit(Toolkit):
    """Toolkit para manipulação de arquivos e navegação em diretórios."""
    
    def __init__(self, workspace: Path | None = None):
        super().__init__(name="filesystem_toolkit")
        self._workspace = workspace or Path.cwd()
        self.register(self.read_file)
        self.register(self.list_dir)
        self.register(self.write_file)

    def read_file(self, path: str) -> str:
        """Lê o conteúdo de um arquivo. Útil para consultar skills (.md) ou códigos (.py).
        
        Args:
            path (str): Caminho do arquivo a ser lido.
        """
        try:
            p = Path(path)
            if not p.is_absolute():
                p = self._workspace / p
            
            if not p.exists():
                return f"Erro: Arquivo não encontrado em {p}"
            
            return p.read_text(encoding="utf-8")
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

    def list_dir(self, path: str = ".") -> str:
        """Lista os arquivos e pastas em um diretório para entender a estrutura de skills disponíveis.
        
        Args:
            path (str): Caminho do diretório (padrão: raiz do projeto).
        """
        try:
            p = Path(path)
            if not p.is_absolute():
                p = self._workspace / p
                
            if not p.exists():
                return f"Erro: Diretório não encontrado em {p}"
            
            items = os.listdir(p)
            result = [f"{'[DIR]' if (p/item).is_dir() else '[FILE]'} {item}" for item in items]
            return "\n".join(result)
        except Exception as e:
            return f"Erro ao listar diretório: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        """Escreve conteúdo em um arquivo. Útil para criar novas skills ou gerar entregáveis.
        
        Args:
            path (str): Caminho do arquivo.
            content (str): Conteúdo a ser gravado.
        """
        try:
            p = Path(path)
            if not p.is_absolute():
                p = self._workspace / p
            
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Sucesso: Arquivo gravado em {path}"
        except Exception as e:
            return f"Erro ao gravar arquivo: {str(e)}"
