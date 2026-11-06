import platform
import shutil
import requests

OLLAMA_MODEL = "nomic-embed-text"

OLLAMA_DOWNLOAD_URLS = {
    "Darwin": "https://ollama.com/download/mac",
    "Windows": "https://ollama.com/download/windows",
    "Linux": "https://ollama.com/download/linux",
}


def check_ollama():

    system = platform.system()
    architecture = platform.machine()

    ollama_path = shutil.which("ollama")

    if not ollama_path:
        return {
            "installed": False,
            "system": system,
            "architecture": architecture,
            "download_url": OLLAMA_DOWNLOAD_URLS.get(system),
            "message": "Ollama is not installed or not available in PATH."
        }

    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        response.raise_for_status()

        models = response.json().get("models", [])

        model_available = any(
            model.get("name", "").startswith(OLLAMA_MODEL + ":")
            or model.get("name") == OLLAMA_MODEL
            for model in models
        )

        return {
            "installed": True,
            "running": True,
            "model_available": model_available,
            "model": OLLAMA_MODEL,
            "message": (
                "Ollama is ready."
                if model_available
                else "Ollama is running, but the embedding model is missing."
            )
        }

    except requests.RequestException:
        return {
            "installed": True,
            "running": False,
            "message": "Ollama is installed but its local service is unavailable."
        }