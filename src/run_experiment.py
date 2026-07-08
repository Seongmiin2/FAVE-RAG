"""Run real LLM calls for FAVE-RAG once API keys are configured."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from common.jsonl_utils import read_jsonl, write_jsonl


METHOD_TO_FILE = {
    "llm_only": "llm_only.jsonl",
    "vanilla_clean": "vanilla_clean.jsonl",
    "vanilla_mixed": "vanilla_mixed.jsonl",
    "demo_mixed": "demo_mixed.jsonl",
    "fave_mixed": "fave_mixed.jsonl",
}


def evidence_map(item: dict) -> dict[str, dict]:
    rows = []
    rows.extend(item.get("valid_evidence", []))
    rows.extend(item.get("invalid_evidence", []))
    rows.extend(item.get("contested_evidence", []))
    return {row["id"]: row for row in rows}


def render_context(item: dict, context_ids: list[str]) -> str:
    by_id = evidence_map(item)
    lines = []
    for eid in context_ids:
        row = by_id[eid]
        lines.append(f"- {eid}: {row['text']}")
    return "\n".join(lines)


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def fill_template(template: str, **values: str) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def call_model(client: OpenAI, model: str, prompt: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_output": text}


def run_simple_method(client: OpenAI, model: str, method: str, bench_rows: list[dict]) -> list[dict]:
    if method == "llm_only":
        template = load_prompt("prompts/llm_only.txt")
        return [
            {"id": item["id"], "method": method, **call_model(client, model, fill_template(template, question=item["question"]))}
            for item in bench_rows
        ]

    if method == "vanilla_clean":
        template = load_prompt("prompts/vanilla_rag.txt")
        return [
            {
                "id": item["id"],
                "method": method,
                **call_model(client, model, fill_template(template, question=item["question"], context=render_context(item, item["clean_context"]))),
            }
            for item in bench_rows
        ]

    if method == "vanilla_mixed":
        template = load_prompt("prompts/vanilla_rag.txt")
        return [
            {
                "id": item["id"],
                "method": method,
                **call_model(client, model, fill_template(template, question=item["question"], context=render_context(item, item["mixed_context"]))),
            }
            for item in bench_rows
        ]

    if method == "demo_mixed":
        template = load_prompt("prompts/demo_style.txt")
        return [
            {
                "id": item["id"],
                "method": method,
                **call_model(client, model, fill_template(template, question=item["question"], context=render_context(item, item["mixed_context"]))),
            }
            for item in bench_rows
        ]

    raise ValueError(f"Unknown simple method: {method}")


def run_fave_method(client: OpenAI, model: str, bench_rows: list[dict]) -> list[dict]:
    checker_template = load_prompt("prompts/validity_checker.txt")
    solver_template = load_prompt("prompts/fave_rag.txt")
    outputs = []
    for item in bench_rows:
        context = render_context(item, item["mixed_context"])
        checker = call_model(
            client,
            model,
            fill_template(checker_template, question=item["question"], evidence_list=context),
        )
        arbitration = checker.get("arbitration", {})
        by_id = evidence_map(item)
        arbitrated_context = "\n".join(
            f"- {eid} [{arbitration.get(eid, 'Contested')}]: {by_id[eid]['text']}"
            for eid in item["mixed_context"]
        )
        solver = call_model(
            client,
            model,
            fill_template(solver_template, question=item["question"], arbitrated_context=arbitrated_context),
        )
        outputs.append(
            {
                "id": item["id"],
                "method": "fave_mixed",
                "predicted_arbitration": arbitration,
                "arbitration_reasons": checker.get("reasons", {}),
                **solver,
            }
        )
    return outputs


def run_method(client: OpenAI, model: str, method: str, bench_rows: list[dict]) -> list[dict]:
    if method == "fave_mixed":
        return run_fave_method(client, model, bench_rows)
    return run_simple_method(client, model, method, bench_rows)


def make_client(provider: str) -> tuple[OpenAI, str]:
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY is missing. Add it to .env before running OpenAI experiments.")
        return OpenAI(api_key=api_key), model

    if provider == "together":
        api_key = os.getenv("TOGETHER_API_KEY") or os.getenv("together_ai_API_KEY")
        model = os.getenv("TOGETHER_MODEL") or os.getenv("QWEN_MODEL") or "Qwen/Qwen2.5-72B-Instruct-Turbo"
        if not api_key:
            raise SystemExit("TOGETHER_API_KEY or together_ai_API_KEY is missing. Add it to .env before running Together/Qwen experiments.")
        return OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1"), model

    if provider == "qwen":
        api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL")
        model = os.getenv("QWEN_MODEL", "qwen-plus")
        if not api_key:
            raise SystemExit("QWEN_API_KEY or DASHSCOPE_API_KEY is missing. Add it to .env before running Qwen experiments.")
        if not base_url:
            raise SystemExit("QWEN_BASE_URL is missing. Add the OpenAI-compatible Qwen endpoint to .env.")
        return OpenAI(api_key=api_key, base_url=base_url), model

    raise ValueError(f"Unknown provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", default="data/pilot/fave_bench_10.jsonl")
    parser.add_argument("--provider", choices=["openai", "together", "qwen"], default="openai")
    parser.add_argument("--model", default=None, help="Override provider model from .env.")
    parser.add_argument("--method", choices=list(METHOD_TO_FILE), required=True)
    parser.add_argument("--output_dir", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    load_dotenv()
    client, default_model = make_client(args.provider)
    model = args.model or default_model
    bench_rows = list(read_jsonl(args.bench))
    if args.limit is not None:
        bench_rows = bench_rows[: args.limit]
    rows = run_method(client, model, args.method, bench_rows)
    output_dir = Path(args.output_dir or f"outputs/real/{args.provider}")
    output_path = output_dir / METHOD_TO_FILE[args.method]
    write_jsonl(output_path, rows)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
