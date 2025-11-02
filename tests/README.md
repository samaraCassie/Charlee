# Charlee Tests

Testes automatizados para o sistema Charlee.

## Estrutura

- `test_memory.py`: Testes de memória e user memories
- `test_conversation_history.py`: Testes de histórico de conversação

## Executando os Testes

### Teste de Memória
```bash
python3 tests/test_memory.py
```

### Teste de Histórico
```bash
python3 tests/test_conversation_history.py
```

## Requisitos

- Backend deve estar rodando em `http://localhost:8000`
- Redis deve estar ativo
- OpenAI API key configurada

## Próximos Testes

- [ ] Testes unitários com pytest
- [ ] Testes de integração da API
- [ ] Testes dos agentes especializados
- [ ] Testes de performance
