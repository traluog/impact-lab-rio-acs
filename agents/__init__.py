"""
Cliente compartilhado da API Anthropic.
Todos os agentes importam daqui para manter consistência.
"""

import os
import anthropic

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "❌ ANTHROPIC_API_KEY não encontrada.\n"
            "   Execute: export ANTHROPIC_API_KEY='sk-ant-...'\n"
            "   Ou adicione ao .env e rode: export $(cat .env | grep -v '#' | xargs)"
        )
    return anthropic.Anthropic(api_key=api_key)


def chamar_claude(system_prompt: str, user_message: str, max_tokens: int = MAX_TOKENS) -> str:
    client = get_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
