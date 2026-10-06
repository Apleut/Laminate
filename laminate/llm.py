from pathlib import Path
from llama_cpp import Llama
from platformdirs import user_data_dir

_CANDIDATE_DIRS = [
    Path.cwd() / "models",
    Path(user_data_dir("Laminate", "Apleut")) / "models",
]

DEFAULT_N_CTX = 4096
_llm: Llama | None = None


class LLMError(Exception):
    pass


def _find_model_file() -> Path:
    checked = []

    for candidate_dir in _CANDIDATE_DIRS:
        checked.append(str(candidate_dir))

        if not candidate_dir.exists():
            continue

        gguf_files = list(candidate_dir.glob("*.gguf"))

        if len(gguf_files) == 1:
            return gguf_files[0]

        if len(gguf_files) > 1:
            names = ", ".join(f.name for f in gguf_files)
            raise LLMError(
                f"Multiple .gguf files found in {candidate_dir} ({names}) - "
                "keep only one so Laminate knows which to load."
            )

    checked_str = "\n  - ".join(checked)
    raise LLMError(
        "No .gguf model file found. Laminate checked:\n  - "
        f"{checked_str}\n"
        "Download a compatible model (see README) and place it in one "
        "of those folders (create the folder if it doesn't exist)."
    )


def get_llm(n_ctx: int = DEFAULT_N_CTX) -> Llama:
    global _llm

    if _llm is None:
        model_path = _find_model_file()
        try:
            _llm = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                verbose=False,
            )
        except Exception as e:
            raise LLMError(f"Failed to load model at {model_path}: {e}")

    return _llm


def generate(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.3,
) -> str:
    """
    Sends a prompt to the local model and returns its text response.

    system_prompt: optional instruction framing the model's role/task
        (e.g. "You are a precise changelog generator...")
    temperature: kept low by default (0.3) to prevent rambling. Increase the temperature for more "creative" responses.
    """
    llm = get_llm()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response["choices"][0]["message"]["content"].strip()

# testing purposes only
if __name__ == "__main__":
    print("Loading model...")
    get_llm()
    print("Model loaded. Sending a test prompt...\n")

    reply = generate(
        "Reply with exactly one short sentence confirming you're working.",
        max_tokens=50,
    )
    print(f"Response: {reply}")