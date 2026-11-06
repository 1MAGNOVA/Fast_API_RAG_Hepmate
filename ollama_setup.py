import platform
import shutil
import requests

EMBEDDING_MODEL = "nomic-embed-text"
GENERATION_MODEL = "qwen2.5:0.5b"

REQUIRED_MODELS = [
    EMBEDDING_MODEL,
    GENERATION_MODEL,
]

OLLAMA_BASE_URL = "http://localhost:11434"

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
            "running": False,
            "system": system,
            "architecture": architecture,
            "download_url": OLLAMA_DOWNLOAD_URLS.get(system),
            "models": {},
            "message": "Ollama is not installed or not available in PATH.",
        }

    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=5,
        )
        response.raise_for_status()

        installed_models = {
            model.get("name", "").split(":")[0]
            for model in response.json().get("models", [])
        }

        model_status = {
            model: model.split(":")[0] in installed_models
            for model in REQUIRED_MODELS
        }

        all_models_available = all(model_status.values())

        return {
            "installed": True,
            "running": True,
            "system": system,
            "architecture": architecture,
            "models": model_status,
            "all_models_available": all_models_available,
            "message": (
                "Ollama and all required models are ready."
                if all_models_available
                else "Ollama is running, but one or more required models are missing."
            ),
        }

    except requests.RequestException:
        return {
            "installed": True,
            "running": False,
            "system": system,
            "architecture": architecture,
            "models": {},
            "message": "Ollama is installed but its local service is unavailable.",
        }
