"""Provider-agnostic LLM access for the agents and the Arabic report translation.

Agents call `generate(system_prompt, payload, schema)` and always get a dict back or an LLMError.
Providers (env LLM_PROVIDER): any module in backend/ai/providers/ with the same name, for example
    ollama       local open-source model through Ollama - DEFAULT, model qwen3:30b-a3b
    mock         no model; agents fall back to their own template wording
Tools are disabled for every call; the model reads and writes text only.
"""
import importlib
import os
import re

DEFAULT_MODELS = {'ollama': 'qwen3:30b-a3b'}
DEFAULT_TIMEOUTS = {'ollama': 300}   # local models are slower, especially on CPU

PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')
MODEL = os.getenv('LLM_MODEL') or DEFAULT_MODELS.get(PROVIDER, '')
TIMEOUT = int(os.getenv('LLM_TIMEOUT_SECONDS') or DEFAULT_TIMEOUTS.get(PROVIDER, 120))

BANNED = re.compile(r'\b(safe to (substitute|use|take|carry)|approved|cleared|permitted to carry|you (can|may) carry|'
                    r'is allowed|guaranteed|diagnos(is|ed|e)|diabet(es|ic)|prediabet)', re.I)


class LLMError(Exception):
    pass


def provider_label():
    return f'{PROVIDER}:{MODEL}' if PROVIDER != 'mock' else 'mock'


def generate(system_prompt, payload, schema):
    """Structured generation. Raises LLMError when the provider is mock / unavailable / returns junk."""
    if PROVIDER == 'mock':
        raise LLMError('mock provider')
    if not re.fullmatch(r'[a-z0-9_]+', PROVIDER or ''):
        raise LLMError(f'Unknown LLM_PROVIDER {PROVIDER!r}')
    try:
        provider = importlib.import_module(f'backend.ai.providers.{PROVIDER}')
    except ModuleNotFoundError as exc:
        raise LLMError(f'Unknown LLM_PROVIDER {PROVIDER!r} (no backend/ai/providers/{PROVIDER}.py)') from exc
    data = provider.generate(system_prompt, payload, schema, MODEL, TIMEOUT)
    if not isinstance(data, dict):
        raise LLMError('AI reply is not an object')
    return data


# ------------------------------------------------------------------ validation helpers
_NUM = re.compile(r'\d+(?:[.,]\d+)?')


def numbers_in(text):
    return {n.replace(',', '.').rstrip('0').rstrip('.') if '.' in n.replace(',', '.') else n
            for n in _NUM.findall(text or '')}


def check_text(text, allowed_numbers, field):
    """Reject banned wording and numbers that are not in the facts given to the model."""
    if not text:
        return
    if BANNED.search(text):
        raise LLMError(f'{field}: wording not allowed ({BANNED.search(text).group(0)!r})')
    extra = numbers_in(text) - allowed_numbers
    if extra:
        raise LLMError(f'{field}: numbers not in the evidence {sorted(extra)}')


def check_length(text, max_words, field):
    """Keep AI wording short; longer replies fall back to the template wording."""
    n = len((text or '').split())
    if n > max_words:
        raise LLMError(f'{field}: {n} words (max {max_words})')
