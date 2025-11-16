#!/usr/bin/env python3
"""Test conversation history and context tracking."""

import requests

API_URL = "http://localhost:8000/api/v1/agent/chat"


def chat(message, session_id=None):
    """Send message to Charlee agent."""
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id

    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    data = response.json()

    print(f"\n{'>'*60}")
    print(f"📤 Samara: {message}")
    print(f"💬 Charlee: {data['response']}")

    return data["session_id"]


print("\n" + "=" * 60)
print("🧪 TESTE DE HISTÓRICO DE CONVERSAS")
print("=" * 60)

# Start a conversation session
print("\n📋 Iniciando uma nova conversa...")

session = chat("Oi! Vou te contar sobre meus Big Rocks principais.")
session = chat(
    "Meu primeiro Big Rock é 'Syssa - Estágio', onde trabalho com desenvolvimento.",
    session_id=session,
)
session = chat(
    "O segundo é 'Crise Lunelli', relacionado a um projeto pessoal importante.",
    session_id=session,
)
session = chat(
    "Agora me diga: quais são os meus dois Big Rocks que acabei de mencionar?",
    session_id=session,
)

print("\n" + "=" * 60)
print(f"✅ Session ID: {session}")
print("=" * 60)
