from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


HCMUS_ROOT = Path(__file__).resolve().parent


def build_default_output_path(model_name: str) -> Path:
    ts = datetime.now().strftime("%y%m%d_%H%M")
    safe_model = model_name.strip().replace(" ", "-").replace("/", "-")
    return HCMUS_ROOT / "output" / f"{ts}_{safe_model}.jsonl"


def add_llm_args(
    parser: ArgumentParser,
    *,
    default_provider: str,
    default_model: str,
    include_output: bool = False,
    include_run_name: bool = False,
    include_base_url: bool = False,
) -> ArgumentParser:
    parser.add_argument(
        "--provider",
        type=str,
        default=default_provider,
        choices=["openai", "anthropic", "local", "gemini", "huggingface"],
        help="LLM provider",
    )
    parser.add_argument("--model", type=str, default=default_model, help="Model name")

    if include_run_name:
        parser.add_argument(
            "--run-name",
            type=str,
            default=None,
            help="Base output filename without extension",
        )

    if include_output:
        parser.add_argument(
            "--output",
            type=Path,
            default=None,
            help="Output JSONL file. If omitted, auto-generate under evaluation/hcmus/output",
        )

    if include_base_url:
        parser.add_argument("--base-url", type=str, default=None, help="Base URL for local provider")

    return parser