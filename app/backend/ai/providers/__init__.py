"""LLM providers behind backend/ai/llm.py. LLM_PROVIDER in .env names the module to use.

Each module exposes `generate(system_prompt, payload, schema, model, timeout)` returning a dict, or raising
llm.LLMError. To add a provider, drop a new module here and set LLM_PROVIDER to its name.

    ollama       local open-source model through Ollama (default: Qwen3 30B-A3B)
"""
