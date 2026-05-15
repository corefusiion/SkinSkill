import yt_dlp
import os
import re
from pathlib import Path
from agno.tools import Toolkit
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

class YouTubeMediaToolkit(Toolkit):
    """Toolkit para extrair informações e mídias do YouTube."""
    
    def __init__(self, workspace: Path | None = None):
        super().__init__(name="youtube_media_toolkit")
        self._workspace = (workspace or Path.cwd()) / "tmp" / "media"
        self._workspace.mkdir(parents=True, exist_ok=True)
        self.register(self.get_transcription)

    def _extract_video_id(self, url: str) -> str | None:
        """Extrai o ID do vídeo de uma URL do YouTube."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:be\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11}).*',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcription(self, url: str) -> str:
        """Obtém a transcrição de um vídeo do YouTube. 
        Tenta primeiro via legendas oficiais/automáticas (grátis) e usa Whisper como fallback.
        
        Args:
            url (str): A URL do vídeo do YouTube.
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            return "Erro: Não foi possível extrair o ID do vídeo da URL fornecida."

        # Tenta usar a API de transcrição gratuita primeiro
        try:
            print(f"🔍 Buscando legendas para o vídeo {video_id}...")
            # Na versão 1.2.4+, é necessário instanciar a API
            # Para pular erro de SSL, criamos uma sessão customizada
            import requests
            from urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            
            session = requests.Session()
            session.verify = False
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            
            api = YouTubeTranscriptApi(http_client=session)
            transcript_list = api.list(video_id)
            
            try:
                # Tenta PT primeiro, depois EN
                transcript = transcript_list.find_transcript(['pt', 'en'])
            except:
                # Se não achar nenhuma das duas, tenta as geradas
                try:
                    transcript = transcript_list.find_generated_transcript(['pt', 'en'])
                except:
                    # Se ainda não achar, tenta qualquer uma
                    transcript = next(iter(transcript_list))
            
            data = transcript.fetch()
            text = " ".join([t['text'] for t in data])
            return f"Transcrição (via YouTube API):\n\n{text}"
        except Exception as e:
            print(f"⚠️ Legendas grátis indisponíveis: {e}. Tentando via Download + Whisper...")

        # Fallback: Download de áudio + Whisper via OpenRouter
        try:
            output_template = str(self._workspace / "%(id)s.%(ext)s")
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'nocheckcertificate': True, 
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'outtmpl': output_template,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'], # Android costuma ser mais resiliente
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'prefer_free_formats': True,
                'youtube_include_dash_manifest': False,
                'youtube_include_hls_manifest': False,
            }

            print(f"📥 Baixando áudio para transcrição via IA...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id_real = info['id']
                audio_path = self._workspace / f"{video_id_real}.mp3"

            if not audio_path.exists():
                return f"Erro: O download do áudio falhou (arquivo não encontrado em {audio_path})."

            print(f"🎙️ Transcrevendo áudio '{info['title']}' com Whisper...")
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
            
            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="openai/whisper-1",
                    file=audio_file
                )
            
            # Limpeza opcional: os.remove(audio_path)
            return f"Transcrição de '{info['title']}' (via Whisper AI):\n\n{transcript.text}"

        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                return (
                    "O YouTube bloqueou o acesso (Erro 403). Isso geralmente acontece porque:\n"
                    "1. O vídeo foi deletado ou é privado.\n"
                    "2. O YouTube detectou o acesso como bot.\n"
                    f"Detalhes técnicos: {error_msg}"
                )
            if "Video unavailable" in error_msg:
                return f"O vídeo não está disponível: {error_msg}"
                
            return f"Erro ao processar vídeo: {error_msg}"
