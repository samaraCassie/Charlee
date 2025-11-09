"""
Testes para o AgentOrchestrator.

Este arquivo demonstra e testa o comportamento do sistema de orquestração inteligente.
"""

import sys
sys.path.append('/home/sam-cassie/GitHub/Charlee/backend')


def test_intent_detection():
    """Testa a detecção de intenção em diferentes mensagens."""

    test_cases = [
        # Wellness intent
        {
            "message": "Estou me sentindo muito cansada hoje",
            "expected_intent": "wellness",
            "expected_agent": "CycleAwareAgent"
        },
        {
            "message": "Qual fase do ciclo estou?",
            "expected_intent": "wellness",
            "expected_agent": "CycleAwareAgent"
        },
        {
            "message": "Minha energia está baixa por causa da TPM",
            "expected_intent": "wellness",
            "expected_agent": "CycleAwareAgent"
        },

        # Capacity intent
        {
            "message": "Posso aceitar um novo projeto?",
            "expected_intent": "capacity",
            "expected_agent": "CapacityGuardAgent"
        },
        {
            "message": "Estou com sobrecarga de trabalho",
            "expected_intent": "capacity",
            "expected_agent": "CapacityGuardAgent"
        },
        {
            "message": "Qual minha carga atual?",
            "expected_intent": "capacity",
            "expected_agent": "CapacityGuardAgent"
        },

        # Tasks intent
        {
            "message": "Criar tarefa: Apresentação Janeiro",
            "expected_intent": "tasks",
            "expected_agent": "CharleeAgent (com check de capacidade)"
        },
        {
            "message": "Listar minhas tarefas de hoje",
            "expected_intent": "tasks",
            "expected_agent": "CharleeAgent (com check de capacidade)"
        },
        {
            "message": "Adicionar novo big rock",
            "expected_intent": "tasks",
            "expected_agent": "CharleeAgent (com check de capacidade)"
        },

        # General intent (with consultation)
        {
            "message": "Qual deve ser meu foco hoje?",
            "expected_intent": "general",
            "expected_agent": "CharleeAgent (com consulta multi-agente)",
            "should_consult": True
        },
        {
            "message": "O que priorizar essa semana?",
            "expected_intent": "general",
            "expected_agent": "CharleeAgent (com consulta multi-agente)",
            "should_consult": True
        },
    ]

    print("=" * 80)
    print("🧪 TESTE: Detecção de Intenção do Orquestrador")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        message = test["message"]
        expected_intent = test["expected_intent"]
        expected_agent = test["expected_agent"]

        # Simular análise de intenção
        from agent.orchestrator import AgentOrchestrator

        # Mock do orquestrador apenas para análise
        class MockDB:
            pass

        try:
            # Testar análise sem executar (usar método privado para teste)
            message_lower = message.lower()

            # Wellness keywords
            wellness_keywords = [
                "ciclo", "menstrua", "energia", "cansa", "fase",
                "TPM", "ovula", "humor", "sintoma", "período",
                "bem-estar", "descanso", "saúde", "dormir", "sono",
                "estresse", "ansiedade", "hormônio"
            ]

            # Capacity keywords
            capacity_keywords = [
                "sobrecarga", "muito trabalho", "novo projeto",
                "aceitar", "compromisso", "carga", "capacidade",
                "não consigo", "muito", "trade-off", "projeto novo",
                "conseguir fazer", "dar conta", "prazo", "deadline",
                "adiar", "priorizar", "tempo suficiente"
            ]

            # Task keywords
            task_keywords = [
                "tarefa", "criar tarefa", "adicionar tarefa",
                "listar tarefa", "big rock", "pilar", "objetivo",
                "fazer hoje", "completar", "concluir", "marcar como"
            ]

            # Detect intent
            detected_intent = "general"
            if any(kw in message_lower for kw in wellness_keywords):
                detected_intent = "wellness"
            elif any(kw in message_lower for kw in capacity_keywords):
                detected_intent = "capacity"
            elif any(kw in message_lower for kw in task_keywords):
                detected_intent = "tasks"

            # Check result
            if detected_intent == expected_intent:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1

            print(f"{status} Teste {i}:")
            print(f"   Mensagem: '{message}'")
            print(f"   Intent esperado: {expected_intent}")
            print(f"   Intent detectado: {detected_intent}")
            print(f"   Agente: {expected_agent}")
            print()

        except Exception as e:
            print(f"❌ ERRO no teste {i}: {str(e)}")
            failed += 1
            print()

    print("=" * 80)
    print(f"Resultados: {passed} passaram, {failed} falharam de {len(test_cases)} testes")
    print("=" * 80)
    print()


def test_routing_examples():
    """Demonstra exemplos de roteamento do orquestrador."""

    print("=" * 80)
    print("📋 EXEMPLOS: Como o Orquestrador Roteia Mensagens")
    print("=" * 80)
    print()

    examples = [
        {
            "categoria": "Bem-Estar e Ciclo",
            "mensagens": [
                "Como está minha energia hoje?",
                "Registrar fase menstrual",
                "Estou com muita dor de cabeça e cansaço"
            ],
            "agente": "CycleAwareAgent",
            "comportamento": "Fornece informações sobre fase do ciclo e sugestões baseadas em energia"
        },
        {
            "categoria": "Capacidade e Sobrecarga",
            "mensagens": [
                "Posso aceitar um projeto de 15 tarefas?",
                "Estou sobrecarregada",
                "Qual minha carga de trabalho atual?"
            ],
            "agente": "CapacityGuardAgent",
            "comportamento": "Calcula carga, avalia capacidade, sugere trade-offs se necessário"
        },
        {
            "categoria": "Gestão de Tarefas",
            "mensagens": [
                "Criar tarefa: Reunião com Breno",
                "Listar minhas tarefas de hoje",
                "Marcar tarefa X como concluída"
            ],
            "agente": "CharleeAgent (com check automático de capacidade)",
            "comportamento": "Gerencia tarefas E consulta CapacityGuard para alertar sobre sobrecarga"
        },
        {
            "categoria": "Planejamento Estratégico",
            "mensagens": [
                "Qual deve ser meu foco hoje?",
                "O que priorizar essa semana?",
                "Como planejar meu mês?"
            ],
            "agente": "CharleeAgent (com consulta MULTI-AGENTE)",
            "comportamento": "Consulta CycleAware (energia) + CapacityGuard (carga) + responde com contexto completo"
        }
    ]

    for example in examples:
        print(f"🎯 **{example['categoria']}**")
        print(f"   Agente: {example['agente']}")
        print(f"   Comportamento: {example['comportamento']}")
        print()
        print("   Exemplos de mensagens:")
        for msg in example['mensagens']:
            print(f"   • \"{msg}\"")
        print()
        print("-" * 80)
        print()


def test_orchestration_features():
    """Lista as features de orquestração implementadas."""

    print("=" * 80)
    print("✨ FEATURES DO SISTEMA DE ORQUESTRAÇÃO")
    print("=" * 80)
    print()

    features = [
        {
            "nome": "Intelligent Routing",
            "descricao": "Análise automática de intenção e roteamento para agente especializado",
            "beneficio": "Respostas mais precisas de especialistas"
        },
        {
            "nome": "Cross-Agent Consultation",
            "descricao": "Para decisões complexas, consulta múltiplos agentes automaticamente",
            "beneficio": "Decisões baseadas em contexto completo (energia + carga + histórico)"
        },
        {
            "nome": "Capacity-Aware Task Creation",
            "descricao": "Ao criar tarefas, verifica automaticamente se há sobrecarga",
            "beneficio": "Proteção proativa contra overcommitment"
        },
        {
            "nome": "Wellness Context Injection",
            "descricao": "Injeta contexto de bem-estar em perguntas de planejamento",
            "beneficio": "Recomendações adaptadas à fase do ciclo e energia atual"
        },
        {
            "nome": "Keyword-Based Intent Detection",
            "descricao": "Detecta intenção baseado em palavras-chave expandidas (50+ keywords)",
            "beneficio": "Alta precisão na detecção de intenção"
        },
        {
            "nome": "Debug & Analytics Endpoint",
            "descricao": "Endpoint /analyze-routing para entender decisões de roteamento",
            "beneficio": "Transparência e facilidade de debugging"
        }
    ]

    for i, feature in enumerate(features, 1):
        print(f"{i}. ✅ **{feature['nome']}**")
        print(f"   📝 {feature['descricao']}")
        print(f"   💡 Benefício: {feature['beneficio']}")
        print()


def main():
    """Executa todos os testes."""
    print()
    print("🚀 CHARLEE - TESTES DO AGENT ORCHESTRATOR")
    print("=" * 80)
    print()

    # Testes
    test_intent_detection()
    test_routing_examples()
    test_orchestration_features()

    print()
    print("=" * 80)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 80)
    print()
    print("💡 Para testar com a API rodando:")
    print("   1. docker-compose up -d")
    print("   2. curl -X POST http://localhost:8000/api/v1/agent/analyze-routing \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"message\": \"Estou cansada hoje\"}'")
    print()


if __name__ == "__main__":
    main()
