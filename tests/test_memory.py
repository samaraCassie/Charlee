#!/usr/bin/env python3
"""Test script to verify agent memory and context persistence."""

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

    print(f"\n{'='*60}")
    print(f"User: {message}")
    print(f"Session ID: {data['session_id']}")
    print(f"{'='*60}")
    print(f"Charlee: {data['response']}")

    return data["session_id"]


# Test 1: First conversation - introduce myself
print("\n🧪 TEST 1: First conversation")
session1 = chat(
    "Oi! Meu nome é Samara e estou desenvolvendo um sistema de produtividade."
)

# Test 2: Continue same session - agent should remember my name
print("\n🧪 TEST 2: Same session - should remember my name")
session2 = chat("Você lembra qual é o meu nome?", session_id=session1)

# Test 3: New session - check if user memories persist
print("\n🧪 TEST 3: New session - should remember from user memories")
session3 = chat("Olá! Você sabe quem eu sou?")

print("\n✅ Test complete!")
print(f"Session 1 ID: {session1}")
print(f"Session 2 ID: {session2}")
print(f"Session 3 ID: {session3}")
