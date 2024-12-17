# **rating_platform_backend**

## Описание проекта
**rating_platform** — это система для оценки студентами преподавателей и учебных заведений.  
Проект построен на **Django** и **Django Rest Framework**, поддерживает использование **Docker** для простого запуска.

---

## Стек технологий
- **Python 3.10+**
- **Django 4.x**
- **Django Rest Framework**
- **PostgreSQL**
- **Docker / Docker Compose**

---

## Prerequisites (Предварительные требования)
Перед запуском убедитесь, что на вашей машине установлено:
1. **Git** (система контроля версий)  
   - [Скачать Git](https://git-scm.com/)

2. **Docker** (для контейнеризации)  
   - [Установка Docker](https://docs.docker.com/get-docker/)  

## Как запустить проект локально

### 1. Клонирование репозитория
Клонируйте бэкэнд в вашу локальную директорию:
```bash
git clone https://github.com/NikitaMelnikovq/rating_platform_backend.git
cd rating_platform_backend
```
### 2. Клонирование фронтенда
Клонируйте фронтенд
```bash
git clone https://github.com/acuraels/Student-voice-Front-end.git
```

### 3. Запустите сервисы
```bash
docker compose build --no-cache
docker compose --env-file ./study_platform/.env up
```