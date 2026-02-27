# BrainBattle PRD

## Оригинальная задача
QuizBattle от Сбера — командный квиз в реальном времени. Два участника отвечают на вопросы по очереди, AI генерирует вопросы, WebSocket синхронизация, рейтинг, регистрация, статистика.

## Архитектура
- **Backend**: FastAPI + Motor (async MongoDB) + WebSocket + JWT + bcrypt
- **Frontend**: React 19 + React Router + Framer Motion + Tailwind
- **AI**: emergentintegrations (OpenAI GPT-4o)
- **DB**: MongoDB (коллекции: users, games, game_history)
- **GitHub**: https://github.com/SeventhSkySoul/brainbattle1

## Реализовано (2025-02-27)
- AI генерация вопросов (GPT-4o) + резервные вопросы по темам
- Командный режим (А vs Б) + FFA (каждый за себя)
- WebSocket + polling fallback для реального времени
- Лобби с выбором команды, список игроков
- Игровой процесс: таймер, 4 варианта ответа, блокировка кнопок
- Очерёдность внутри команды (turn-based)
- Хост: пауза/возобновление, пропуск, дисквалификация
- Бонус за скорость, выбор сложности (easy/medium/hard)
- JWT авторизация, регистрация, профили
- Рейтинг (таблица лидеров)
- Статистика после игры + экспорт JSON
- Возврат в игру при перезагрузке страницы
- Защита комнаты паролем
- Дизайн: "The Void Terminal" — Syne + Space Mono, #050505 + #CCFF00
- Звуковые эффекты (Web Audio API)
- Мобильная адаптация
- GitHub репо: brainbattle1

## Тестирование
- Backend: 93.3% (все критические тесты прошли)
- Frontend: 100%
- Overall: 96.5%

## Backlog
- P1: Уведомления (sonner toast) при правильном/неправильном ответе
- P1: Улучшить UX перехода между вопросами
- P2: Admin panel для управления вопросами
- P2: Публичное API для интеграции
- P3: React Three Fiber 3D logo (пока CSS 3D)
