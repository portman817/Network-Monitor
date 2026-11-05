# Network Monitor

Учебный проект: Python + FastAPI и React + Vite.
На этапе 1 реализованы только каркас интерфейса и `GET /api/health`,
возвращающий `{"status":"ok"}`. SQLite, ping и мониторинг ещё не реализованы.

## Требования

- Существующее виртуальное окружение `.venv` с Python 3.14.5.
- Node.js 20.19+ или 22.12+ (в текущей среде обнаружен Node.js 24.11.1).
- Windows PowerShell, обычные права пользователя.

Проверено 5 ноября 2026 года: существующее окружение .venv использует Python 3.14.5.
Установлены FastAPI 0.162.0 и Uvicorn 0.54.0; pip check не обнаружил конфликтов.
Frontend: React и React DOM 19.3.1, Vite 8.3.6, @vitejs/plugin-react 6.2.1.
Node.js 24.11.1, npm 11.6.2. Проверены запуск обоих серверов, API напрямую
и через прокси Vite, сообщение об успешном соединении и ошибка при отключении
backend в браузере, а также npm run build. Тестовые серверы после проверки остановлены.

## Подготовка в PowerShell

Все команды ниже выполняются из корня проекта, если не указано иначе.
Не создавайте новое окружение. Если существующее `.venv` находится в другом
месте, сначала уточните его путь и допустимость установки туда зависимостей.

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor
Test-Path .\.venv\Scripts\python.exe
& .\.venv\Scripts\python.exe --version
node --version
npm --version
```

Ожидается `True` и `Python 3.14.5`. Если окружение не найдено, остановитесь.
Активация окружения и изменение ExecutionPolicy не требуются:
команды обращаются непосредственно к его интерпретатору.

**Зависимости уже установлены. Команды для повторной установки при необходимости:**

```powershell
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
& .\.venv\Scripts\python.exe -m pip check
Push-Location .\frontend
npm install
Pop-Location
```

`npm install` создал `frontend/package-lock.json`; его следует хранить в Git
для воспроизводимых последующих установок через `npm ci`.

## Запуск backend — первое окно PowerShell

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir .\backend --host 127.0.0.1 --port 8000 --reload
```

API: http://127.0.0.1:8000/api/health

Документация API: http://127.0.0.1:8000/docs

## Запуск frontend — второе окно PowerShell

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor\frontend
npm run dev
```

Откройте http://127.0.0.1:5173.
Vite передаёт запросы `/api` на `http://127.0.0.1:8000`, сохраняя путь.
Браузер работает с одним origin, поэтому настройка CORS не нужна.
Прокси действует при `npm run dev`; публикация сборки с API пока не настроена.

## Проверка работоспособности

При работающих обоих серверах в третьем окне PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

Оба запроса должны вернуть поле `status` со значением `ok`.
Первый проверяет FastAPI, второй — взаимодействие через прокси Vite.
На странице должны появиться заголовок **Network Monitor** и сообщение
**Backend доступен: ok**.

Остановите backend сочетанием Ctrl+C и обновите страницу:
должно появиться понятное сообщение об отсутствии соединения.
После повторного запуска backend обновите страницу — статус восстановится.

Проверка сборки frontend после установки зависимостей:

```powershell
Set-Location C:\Users\CC-Student\PycharmProjects\Network-Monitor\frontend
npm run build
```

Для остановки каждого сервера используйте Ctrl+C в его окне.

## Структура

```text
backend/
  app/__init__.py       # Пакет Python
  app/main.py           # FastAPI и health endpoint
  requirements.txt     # Зависимости backend
frontend/
  index.html           # HTML-точка входа
  package.json         # Зависимости и команды npm
  vite.config.js       # React, локальный сервер и API-прокси
  src/main.jsx         # Подключение React
  src/App.jsx          # Заголовок и проверка связи с backend
  src/styles.css       # Базовые стили
.gitignore             # Исключения для Git
README.md              # Инструкции
```
