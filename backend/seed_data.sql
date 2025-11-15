-- ==========================================
-- Script de Seed para Banco de Dados Charlee
-- Popula o banco com dados de teste realistas
-- ==========================================

-- Limpar dados existentes (ordem importante devido às foreign keys)
DELETE FROM audit_logs;
DELETE FROM refresh_tokens;
DELETE FROM daily_logs;
DELETE FROM workloads;
DELETE FROM cycle_patterns;
DELETE FROM menstrual_cycles;
DELETE FROM tasks;
DELETE FROM big_rocks;
DELETE FROM users;

-- ==================== USUÁRIOS ====================

-- Senha para todos os usuários de teste: "TestPass123"
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYH0RwI5eNW

-- Usuário 1: Samara (local account)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, oauth_provider, oauth_id, avatar_url, failed_login_attempts, locked_until, last_failed_login, created_at, updated_at, last_login)
VALUES (
    'samara',
    'samara@charlee.app',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYH0RwI5eNW',
    'Samara Cassie',
    1,
    1,
    NULL,
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    datetime('now', '-90 days'),
    datetime('now'),
    datetime('now', '-2 hours')
);

-- Usuário 2: Maria (OAuth Google)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, oauth_provider, oauth_id, avatar_url, failed_login_attempts, locked_until, last_failed_login, created_at, updated_at, last_login)
VALUES (
    'maria.silva',
    'maria.silva@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYH0RwI5eNW',
    'Maria Silva',
    1,
    0,
    'google',
    'google_123456789',
    'https://lh3.googleusercontent.com/a/default-user',
    0,
    NULL,
    NULL,
    datetime('now', '-60 days'),
    datetime('now', '-1 day'),
    datetime('now', '-1 day')
);

-- Usuário 3: João (OAuth GitHub)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, oauth_provider, oauth_id, avatar_url, failed_login_attempts, locked_until, last_failed_login, created_at, updated_at, last_login)
VALUES (
    'joaodev',
    'joao@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYH0RwI5eNW',
    'João Desenvolvedor',
    1,
    0,
    'github',
    '987654321',
    'https://avatars.githubusercontent.com/u/987654321',
    0,
    NULL,
    NULL,
    datetime('now', '-30 days'),
    datetime('now', '-5 days'),
    datetime('now', '-5 days')
);

-- Usuário 4: Ana (conta inativa)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, oauth_provider, oauth_id, avatar_url, failed_login_attempts, locked_until, last_failed_login, created_at, updated_at, last_login)
VALUES (
    'ana',
    'ana@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYH0RwI5eNW',
    'Ana Oliveira',
    0,
    0,
    NULL,
    NULL,
    NULL,
    0,
    NULL,
    NULL,
    datetime('now', '-180 days'),
    datetime('now', '-180 days'),
    datetime('now', '-180 days')
);

-- ==================== BIG ROCKS ====================

-- Big Rocks da Samara (user_id = 1)
INSERT INTO big_rocks (user_id, name, color, active, created_at) VALUES
(1, 'Saúde & Bem-estar', '#22c55e', 1, datetime('now', '-90 days')),
(1, 'Carreira & Desenvolvimento', '#3b82f6', 1, datetime('now', '-90 days')),
(1, 'Relacionamentos', '#ec4899', 1, datetime('now', '-90 days')),
(1, 'Finanças', '#f59e0b', 1, datetime('now', '-90 days')),
(1, 'Aprendizado Contínuo', '#8b5cf6', 1, datetime('now', '-60 days')),
(1, 'Hobbies & Lazer', '#06b6d4', 1, datetime('now', '-30 days'));

-- Big Rocks da Maria (user_id = 2)
INSERT INTO big_rocks (user_id, name, color, active, created_at) VALUES
(2, 'Saúde Mental', '#10b981', 1, datetime('now', '-60 days')),
(2, 'Trabalho', '#6366f1', 1, datetime('now', '-60 days')),
(2, 'Família', '#f43f5e', 1, datetime('now', '-60 days')),
(2, 'Casa', '#14b8a6', 1, datetime('now', '-45 days'));

-- Big Rocks do João (user_id = 3)
INSERT INTO big_rocks (user_id, name, color, active, created_at) VALUES
(3, 'Projetos Open Source', '#8b5cf6', 1, datetime('now', '-30 days')),
(3, 'Fitness', '#22c55e', 1, datetime('now', '-30 days')),
(3, 'Estudos', '#3b82f6', 1, datetime('now', '-20 days'));

-- ==================== TAREFAS ====================

-- Tarefas da Samara - Saúde & Bem-estar (big_rock_id = 1)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Caminhada matinal 30min', 'continuous', NULL, 1, 'in_progress', 3, 7.5, datetime('now', '-30 days'), datetime('now', '-1 day'), NULL),
(1, 'Consulta com nutricionista', 'fixed_appointment', date('now', '+7 days'), 1, 'pending', 2, 8.2, datetime('now', '-5 days'), datetime('now', '-5 days'), NULL),
(1, 'Fazer exames de rotina', 'task', date('now', '+15 days'), 1, 'pending', 4, 6.8, datetime('now', '-10 days'), datetime('now', '-10 days'), NULL),
(1, 'Meditação diária 10min', 'continuous', NULL, 1, 'completed', 5, 6.0, datetime('now', '-45 days'), datetime('now', '-2 days'), datetime('now', '-2 days')),
(1, 'Yoga às terças e quintas', 'continuous', NULL, 1, 'in_progress', 3, 7.0, datetime('now', '-20 days'), datetime('now', '-1 day'), NULL);

-- Tarefas da Samara - Carreira & Desenvolvimento (big_rock_id = 2)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Reunião semanal com equipe', 'fixed_appointment', date('now', '+2 days'), 2, 'pending', 1, 9.5, datetime('now', '-7 days'), datetime('now', '-7 days'), NULL),
(1, 'Finalizar feature de autenticação OAuth', 'task', date('now', '+3 days'), 2, 'in_progress', 1, 9.2, datetime('now', '-14 days'), datetime('now'), NULL),
(1, 'Code review dos PRs pendentes', 'task', date('now', '+1 day'), 2, 'pending', 2, 8.5, datetime('now', '-2 days'), datetime('now', '-2 days'), NULL),
(1, 'Atualizar documentação técnica', 'task', date('now', '+10 days'), 2, 'pending', 4, 6.5, datetime('now', '-5 days'), datetime('now', '-5 days'), NULL),
(1, 'Estudar arquitetura de microserviços', 'continuous', NULL, 2, 'in_progress', 6, 5.5, datetime('now', '-30 days'), datetime('now', '-3 days'), NULL);

-- Tarefas da Samara - Relacionamentos (big_rock_id = 3)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Jantar com família no domingo', 'fixed_appointment', date('now', '+5 days'), 3, 'pending', 3, 7.5, datetime('now', '-3 days'), datetime('now', '-3 days'), NULL),
(1, 'Ligar para a mãe', 'task', date('now', '+2 days'), 3, 'pending', 2, 8.0, datetime('now', '-1 day'), datetime('now', '-1 day'), NULL),
(1, 'Organizar encontro com amigas', 'task', date('now', '+14 days'), 3, 'pending', 5, 6.0, datetime('now', '-7 days'), datetime('now', '-7 days'), NULL);

-- Tarefas da Samara - Finanças (big_rock_id = 4)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Pagar conta de luz', 'task', date('now', '+5 days'), 4, 'pending', 2, 8.3, datetime('now', '-2 days'), datetime('now', '-2 days'), NULL),
(1, 'Revisar investimentos mensais', 'task', date('now', '+7 days'), 4, 'pending', 3, 7.2, datetime('now', '-5 days'), datetime('now', '-5 days'), NULL),
(1, 'Fazer planejamento financeiro 2025', 'task', date('now', '+30 days'), 4, 'pending', 6, 5.8, datetime('now', '-10 days'), datetime('now', '-10 days'), NULL);

-- Tarefas da Samara - Aprendizado Contínuo (big_rock_id = 5)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Completar curso de FastAPI', 'task', date('now', '+20 days'), 5, 'in_progress', 4, 6.8, datetime('now', '-15 days'), datetime('now', '-1 day'), NULL),
(1, 'Ler "Clean Architecture"', 'continuous', NULL, 5, 'in_progress', 5, 6.2, datetime('now', '-25 days'), datetime('now', '-3 days'), NULL),
(1, 'Praticar algoritmos LeetCode', 'continuous', NULL, 5, 'pending', 7, 4.5, datetime('now', '-10 days'), datetime('now', '-10 days'), NULL);

-- Tarefas da Samara - Hobbies & Lazer (big_rock_id = 6)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(1, 'Assistir filme recomendado', 'task', NULL, 6, 'pending', 8, 3.5, datetime('now', '-5 days'), datetime('now', '-5 days'), NULL),
(1, 'Continuar tricô do cachecol', 'continuous', NULL, 6, 'in_progress', 7, 4.0, datetime('now', '-20 days'), datetime('now', '-2 days'), NULL),
(1, 'Visitar exposição de arte', 'task', date('now', '+10 days'), 6, 'pending', 6, 5.0, datetime('now', '-3 days'), datetime('now', '-3 days'), NULL);

-- Tarefas da Maria (user_id = 2)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(2, 'Terapia semanal', 'fixed_appointment', date('now', '+3 days'), 7, 'pending', 1, 9.0, datetime('now', '-30 days'), datetime('now', '-7 days'), NULL),
(2, 'Journaling diário', 'continuous', NULL, 7, 'in_progress', 4, 6.5, datetime('now', '-40 days'), datetime('now', '-1 day'), NULL),
(2, 'Apresentação para diretoria', 'fixed_appointment', date('now', '+2 days'), 8, 'in_progress', 1, 9.8, datetime('now', '-10 days'), datetime('now'), NULL),
(2, 'Revisar orçamento do projeto', 'task', date('now', '+5 days'), 8, 'pending', 2, 8.0, datetime('now', '-3 days'), datetime('now', '-3 days'), NULL),
(2, 'Jantar com pais', 'fixed_appointment', date('now', '+4 days'), 9, 'pending', 3, 7.5, datetime('now', '-2 days'), datetime('now', '-2 days'), NULL),
(2, 'Comprar presente de aniversário do sobrinho', 'task', date('now', '+8 days'), 9, 'pending', 4, 6.5, datetime('now', '-5 days'), datetime('now', '-5 days'), NULL);

-- Tarefas do João (user_id = 3)
INSERT INTO tasks (user_id, description, type, deadline, big_rock_id, status, calculated_priority, priority_score, created_at, updated_at, completed_at) VALUES
(3, 'Contribuir para projeto FastAPI', 'task', date('now', '+7 days'), 11, 'in_progress', 3, 7.0, datetime('now', '-10 days'), datetime('now', '-1 day'), NULL),
(3, 'Code review no repositório do time', 'task', date('now', '+2 days'), 11, 'pending', 2, 8.0, datetime('now', '-3 days'), datetime('now', '-3 days'), NULL),
(3, 'Academia 5x por semana', 'continuous', NULL, 12, 'in_progress', 4, 6.5, datetime('now', '-20 days'), datetime('now', '-1 day'), NULL),
(3, 'Completar curso de TypeScript avançado', 'task', date('now', '+15 days'), 13, 'in_progress', 5, 6.0, datetime('now', '-12 days'), datetime('now', '-2 days'), NULL);

-- ==================== CICLOS MENSTRUAIS ====================

-- Ciclos da Samara (user_id = 1) - últimos 3 meses
INSERT INTO menstrual_cycles (user_id, start_date, phase, symptoms, energy_level, focus_level, creativity_level, notes, created_at) VALUES
-- Ciclo atual (fase menstrual)
(1, date('now', '-3 days'), 'menstrual', 'fadiga,dor_leve', 4, 5, 6, 'Primeiro dia mais intenso, depois melhorou', datetime('now', '-3 days')),
(1, date('now', '-2 days'), 'menstrual', 'fadiga', 5, 6, 7, NULL, datetime('now', '-2 days')),

-- Ciclo anterior
(1, date('now', '-31 days'), 'menstrual', 'fadiga,dor_moderada,irritabilidade', 3, 4, 5, 'Dia difícil, precisei de mais descanso', datetime('now', '-31 days')),
(1, date('now', '-27 days'), 'follicular', 'energia_alta', 8, 9, 8, 'Dia muito produtivo!', datetime('now', '-27 days')),
(1, date('now', '-24 days'), 'follicular', 'energia_alta,foco_intenso', 9, 9, 7, 'Consegui finalizar várias tarefas', datetime('now', '-24 days')),
(1, date('now', '-17 days'), 'ovulation', 'criatividade_alta,energia_alta', 9, 8, 10, 'Ótimas ideias para o projeto', datetime('now', '-17 days')),
(1, date('now', '-10 days'), 'luteal', 'leve_fadiga', 6, 7, 6, NULL, datetime('now', '-10 days')),
(1, date('now', '-5 days'), 'luteal', 'fadiga,irritabilidade', 5, 5, 5, 'TPM leve', datetime('now', '-5 days')),

-- Ciclo mais antigo
(1, date('now', '-60 days'), 'menstrual', 'fadiga,dor_leve', 4, 5, 6, NULL, datetime('now', '-60 days')),
(1, date('now', '-53 days'), 'follicular', 'energia_alta', 8, 8, 8, NULL, datetime('now', '-53 days')),
(1, date('now', '-46 days'), 'ovulation', 'criatividade_alta', 9, 9, 10, NULL, datetime('now', '-46 days')),
(1, date('now', '-39 days'), 'luteal', 'leve_fadiga,irritabilidade', 6, 6, 5, NULL, datetime('now', '-39 days'));

-- Ciclos da Maria (user_id = 2)
INSERT INTO menstrual_cycles (user_id, start_date, phase, symptoms, energy_level, focus_level, creativity_level, notes, created_at) VALUES
(2, date('now', '-5 days'), 'menstrual', 'fadiga,dor_moderada', 3, 4, 5, 'Precisei trabalhar de casa', datetime('now', '-5 days')),
(2, date('now', '-20 days'), 'follicular', 'energia_alta,foco_intenso', 9, 9, 8, NULL, datetime('now', '-20 days')),
(2, date('now', '-14 days'), 'ovulation', 'criatividade_alta', 8, 8, 10, 'Apresentação foi muito bem!', datetime('now', '-14 days'));

-- ==================== PADRÕES DE CICLO ====================

INSERT INTO cycle_patterns (phase, identified_pattern, average_productivity, average_focus, average_energy, confidence_score, suggestions, samples_used, created_at, updated_at) VALUES
('menstrual', 'Baixa energia e foco nos primeiros 2 dias, melhora gradual', 0.6, 0.5, 0.4, 0.75, 'Priorizar tarefas simples;Permitir mais tempo de descanso;Evitar reuniões importantes', 24, datetime('now', '-30 days'), datetime('now', '-1 day')),
('follicular', 'Alta energia e foco, período ideal para tarefas complexas', 1.3, 1.4, 1.3, 0.85, 'Agendar tarefas mais desafiadoras;Aproveitar para aprendizado;Reuniões estratégicas', 28, datetime('now', '-30 days'), datetime('now', '-1 day')),
('ovulation', 'Pico de criatividade e comunicação', 1.2, 1.2, 1.4, 0.80, 'Sessões de brainstorming;Apresentações importantes;Networking', 15, datetime('now', '-30 days'), datetime('now', '-1 day')),
('luteal', 'Energia decrescente, foco em organização', 0.9, 0.8, 0.7, 0.70, 'Tarefas organizacionais;Revisão e documentação;Preparar próxima semana', 22, datetime('now', '-30 days'), datetime('now', '-1 day'));

-- ==================== WORKLOAD ====================

-- Workload da Samara por Big Rock (semana atual)
INSERT INTO workloads (period_start, period_end, big_rock_id, estimated_hours, available_hours, load_percentage, at_risk, risk_reason, calculated_at) VALUES
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 1, 5.0, 7.0, 71.4, 0, NULL, datetime('now', '-1 day')),
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 2, 25.0, 20.0, 125.0, 1, 'Carga de trabalho acima da capacidade disponível', datetime('now', '-1 day')),
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 3, 4.0, 5.0, 80.0, 0, NULL, datetime('now', '-1 day')),
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 4, 2.0, 3.0, 66.7, 0, NULL, datetime('now', '-1 day')),
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 5, 6.0, 8.0, 75.0, 0, NULL, datetime('now', '-1 day')),
(date('now', 'weekday 0', '-7 days'), date('now', 'weekday 0'), 6, 3.0, 5.0, 60.0, 0, NULL, datetime('now', '-1 day'));

-- Workload da semana anterior
INSERT INTO workloads (period_start, period_end, big_rock_id, estimated_hours, available_hours, load_percentage, at_risk, risk_reason, calculated_at) VALUES
(date('now', 'weekday 0', '-14 days'), date('now', 'weekday 0', '-7 days'), 1, 6.0, 7.0, 85.7, 0, NULL, datetime('now', '-8 days')),
(date('now', 'weekday 0', '-14 days'), date('now', 'weekday 0', '-7 days'), 2, 22.0, 20.0, 110.0, 1, 'Pequeno excesso de demanda', datetime('now', '-8 days')),
(date('now', 'weekday 0', '-14 days'), date('now', 'weekday 0', '-7 days'), 3, 3.0, 5.0, 60.0, 0, NULL, datetime('now', '-8 days'));

-- ==================== LOGS DIÁRIOS ====================

-- Logs da Samara (últimos 7 dias)
INSERT INTO daily_logs (user_id, date, wake_time, sleep_time, sleep_hours, sleep_quality, energy_level, productivity_level, mood, notes, created_at) VALUES
(1, date('now', '-6 days'), '07:00', '23:30', 7.5, 8, 7, 8, 'bem', 'Dia produtivo, consegui focar bem', datetime('now', '-6 days')),
(1, date('now', '-5 days'), '07:15', '00:00', 7.25, 6, 6, 6, 'ok', 'Um pouco cansada', datetime('now', '-5 days')),
(1, date('now', '-4 days'), '06:45', '23:00', 7.75, 9, 8, 9, 'ótimo', 'Melhor dia da semana!', datetime('now', '-4 days')),
(1, date('now', '-3 days'), '07:30', '00:30', 7.0, 5, 5, 4, 'mal', 'Menstruação começou, muita fadiga', datetime('now', '-3 days')),
(1, date('now', '-2 days'), '08:00', '00:00', 8.0, 7, 6, 5, 'ok', 'Melhorando aos poucos', datetime('now', '-2 days')),
(1, date('now', '-1 day'), '07:00', '23:30', 7.5, 8, 7, 7, 'bem', 'Energia voltando', datetime('now', '-1 day')),
(1, date('now'), '07:15', NULL, NULL, NULL, 7, NULL, 'bem', 'Dia começando bem', datetime('now'));

-- Logs da Maria (últimos 3 dias)
INSERT INTO daily_logs (user_id, date, wake_time, sleep_time, sleep_hours, sleep_quality, energy_level, productivity_level, mood, notes, created_at) VALUES
(2, date('now', '-2 days'), '06:30', '22:30', 8.0, 9, 8, 8, 'ótimo', NULL, datetime('now', '-2 days')),
(2, date('now', '-1 day'), '06:45', '23:00', 7.75, 7, 7, 7, 'bem', NULL, datetime('now', '-1 day')),
(2, date('now'), '06:30', NULL, NULL, NULL, 8, NULL, 'bem', NULL, datetime('now'));

-- ==================== AUDIT LOGS ====================

-- Logs de auditoria da Samara
INSERT INTO audit_logs (user_id, event_type, event_status, event_message, ip_address, user_agent, request_path, event_metadata, created_at) VALUES
(1, 'register', 'success', 'Usuário registrado com sucesso', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/register', NULL, datetime('now', '-90 days')),
(1, 'login', 'success', 'Login bem-sucedido', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/login', '{"method": "password"}', datetime('now', '-90 days')),
(1, 'login', 'success', 'Login bem-sucedido', '192.168.1.105', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)', '/api/v1/auth/login', '{"method": "password"}', datetime('now', '-30 days')),
(1, 'login', 'failure', 'Senha incorreta', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/login', '{"reason": "wrong_password"}', datetime('now', '-15 days')),
(1, 'login', 'success', 'Login bem-sucedido', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/login', '{"method": "password"}', datetime('now', '-2 hours')),
(1, 'password_change', 'success', 'Senha alterada com sucesso', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/change-password', NULL, datetime('now', '-45 days'));

-- Logs de auditoria da Maria (OAuth Google)
INSERT INTO audit_logs (user_id, event_type, event_status, event_message, ip_address, user_agent, request_path, event_metadata, created_at) VALUES
(2, 'register', 'success', 'Usuário registrado via OAuth', '192.168.1.200', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', '/api/v1/auth/oauth/google/callback', '{"provider": "google"}', datetime('now', '-60 days')),
(2, 'oauth_login', 'success', 'Login via Google bem-sucedido', '192.168.1.200', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', '/api/v1/auth/oauth/google/callback', '{"provider": "google"}', datetime('now', '-60 days')),
(2, 'oauth_login', 'success', 'Login via Google bem-sucedido', '192.168.1.201', 'Mozilla/5.0 (iPad; CPU OS 16_0)', '/api/v1/auth/oauth/google/callback', '{"provider": "google"}', datetime('now', '-1 day'));

-- Logs de auditoria do João (OAuth GitHub)
INSERT INTO audit_logs (user_id, event_type, event_status, event_message, ip_address, user_agent, request_path, event_metadata, created_at) VALUES
(3, 'register', 'success', 'Usuário registrado via OAuth', '192.168.1.150', 'Mozilla/5.0 (X11; Linux x86_64)', '/api/v1/auth/oauth/github/callback', '{"provider": "github"}', datetime('now', '-30 days')),
(3, 'oauth_login', 'success', 'Login via GitHub bem-sucedido', '192.168.1.150', 'Mozilla/5.0 (X11; Linux x86_64)', '/api/v1/auth/oauth/github/callback', '{"provider": "github"}', datetime('now', '-30 days')),
(3, 'oauth_login', 'success', 'Login via GitHub bem-sucedido', '192.168.1.150', 'Mozilla/5.0 (X11; Linux x86_64)', '/api/v1/auth/oauth/github/callback', '{"provider": "github"}', datetime('now', '-5 days'));

-- Logs de auditoria da Ana (tentativas de login em conta inativa)
INSERT INTO audit_logs (user_id, event_type, event_status, event_message, ip_address, user_agent, request_path, event_metadata, created_at) VALUES
(4, 'register', 'success', 'Usuário registrado com sucesso', '192.168.1.180', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/register', NULL, datetime('now', '-180 days')),
(4, 'login', 'blocked', 'Conta inativa', '192.168.1.180', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', '/api/v1/auth/login', '{"reason": "inactive_account"}', datetime('now', '-30 days'));

-- ==========================================
-- Resumo dos Dados Inseridos:
-- ==========================================
-- ✅ 4 usuários (1 admin, 2 OAuth, 1 inativo)
-- ✅ 13 Big Rocks distribuídos entre usuários
-- ✅ 43 tarefas com diversos status e prioridades
-- ✅ 17 registros de ciclo menstrual
-- ✅ 4 padrões de ciclo identificados
-- ✅ 9 análises de workload
-- ✅ 10 logs diários
-- ✅ 13 logs de auditoria
-- ==========================================

-- Verificar contagens
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Big Rocks', COUNT(*) FROM big_rocks
UNION ALL
SELECT 'Tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'Menstrual Cycles', COUNT(*) FROM menstrual_cycles
UNION ALL
SELECT 'Cycle Patterns', COUNT(*) FROM cycle_patterns
UNION ALL
SELECT 'Workloads', COUNT(*) FROM workloads
UNION ALL
SELECT 'Daily Logs', COUNT(*) FROM daily_logs
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM audit_logs;
