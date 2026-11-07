"""Ollama provider: a local open-source model (default Qwen3 30B-A3B) through Ollama's HTTP API.

Setup (once):
    1. Install Ollama for Windows (https://ollama.com) - it runs a local server on http://localhost:11434
    2. ollama pull qwen3:30b-a3b
.env:
    LLM_PROVIDER=ollama
    LLM_MODEL=qwen3:30b-a3b
    # OLLAMA_URL=http://localhost:11434

The reply is forced into the agent's JSON schema with Ollama's structured outputs ("format"). Qwen3's thinking mode is
turned off ("think": false): the agents ask for short, checked wording, and code makes the decisions.
Everything runs on this computer; no patient data leaves it.
"""
import json
import os
import re
import urllib.error
import urllib.request

from ..llm import LLMError

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434').rstrip('/')
OPTIONS = {
    'temperature': 0.2,                                    # steady wording; the checks reject anything off-script
    'num_ctx': int(os.getenv('OLLAMA_NUM_CTX', '16384')),  # room for document text and retrieved passages
}


def generate(system_prompt, payload, schema, model, timeout):
    body = {
        'model': model,
        'messages': [{'role': 'system', 'content': system_prompt},
                     {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, default=str)}],
        'format': schema,
        'stream': False,
        'think': False,
        'options': OPTIONS,
    }
    req = urllib.request.Request(f'{OLLAMA_URL}/api/chat', data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:200]
        if exc.code == 404:   # model not downloaded yet
            raise LLMError(f'Ollama model {model!r} not found; run: ollama pull {model}') from exc
        raise LLMError(f'Ollama error {exc.code}: {detail}') from exc
    except TimeoutError as exc:
        raise LLMError('AI call timed out') from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise LLMError('AI call timed out') from exc
        raise LLMError(f'Ollama not reachable at {OLLAMA_URL} ({exc.reason})') from exc
    except json.JSONDecodeError as exc:
        raise LLMError('Unreadable Ollama output') from exc

    text = ((out.get('message') or {}).get('content') or '').strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', text, re.S)   # tolerate stray text around the JSON
        if not m:
            raise LLMError('No JSON in AI reply')
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError as exc:
            raise LLMError('No JSON in AI reply') from exc
