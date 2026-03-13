# GLM-OCR Web Application

Распознавание текста с изображений с помощью GLM-OCR и llama.cpp.

## Возможности

- 🖼️ Загрузка изображений (PNG, JPG, WebP, GIF)
- 🧠 OCR на базе GLM-OCR (0.9B параметров)
- 🌐 Современный веб-интерфейс
- 🐳 Docker-контейнер
- 📋 Копирование результата в буфер

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repo-url>
cd glm-ocr-webapp

# Запуск (модель скачается автоматически)
docker-compose up -d

# Открыть в браузере
open http://localhost:8080
```

Модель загрузится автоматически с HuggingFace при первом запуске (~1 GB).

### Альтернативная сборка

Если официальный образ `ghcr.io/ggml-org/llama.cpp:server` не работает:

```bash
# Использовать Dockerfile.build (сборка из исходников)
docker build -f Dockerfile.build -t glm-ocr-webapp .
docker run -p 8080:8080 glm-ocr-webapp
```

**Время сборки:**
- `Dockerfile` (официальный образ): ~1-2 минуты
- `Dockerfile.build` (из исходников): ~10-15 минут

## Требования

- 2-4 GB RAM (Q8_0) или 4-6 GB RAM (F16)
- CPU (GPU опционально)
- Современный браузер с поддержкой JavaScript

## Модель

GLM-OCR — мультимодальная модель для распознавания текста.
Автоматически скачивается с HuggingFace при первом запуске.

**Модель по умолчанию:** `ggml-org/GLM-OCR-GGUF:Q8_0`

**Переменные окружения:**
- `HF_REPO=ggml-org/GLM-OCR-GGUF:Q8_0` — модель с HuggingFace
- `HF_REPO=ggml-org/GLM-OCR-GGUF:F16` — альтернатива (лучшее качество, больше памяти)

**Требования:** 2-4 GB RAM для Q8_0

**Источник:** https://huggingface.co/ggml-org/GLM-OCR-GGUF

## API

### POST /api/ocr

Загрузка изображения для распознавания.

```bash
curl -X POST http://localhost:8080/api/ocr \
  -F "file=@image.png"
```

Ответ:
```json
{
  "success": true,
  "text": "Распознанный текст",
  "file_id": "uuid"
}
```

### GET /health

Проверка состояния сервера.

```json
{
  "status": "healthy",
  "server_ready": true,
  "model": "glm-ocr-q8_0.gguf"
}
```

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  FastAPI    │────▶│ llama.cpp   │
│  (index.html)│     │  (Python)   │     │  server     │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                          ┌─────▼─────┐
                                          │ GLM-OCR   │
                                          │ GGUF model│
                                          └───────────┘
```

## Лицензия

MIT