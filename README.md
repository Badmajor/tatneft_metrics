# Tatneft Metrics

Простой REST API для управления метриками с JWT авторизацией, кэшированием и Celery.

Линтер: [Black](https://pypi.org/project/black/)

## 🔹 Быстрый старт (Docker)

1. Клонируем репозиторий:

```bash
git clone https://github.com/badmajor/tatneft_metrics.git
cd tatneft_metrics
```

2. Создаём .env файл:
```bash
cp infra/.env.example infra/.env
```

При необходимости меняем переменные окружения.

3. Запуск Docker:

```bash
docker compose -f infra/docker-compose.yml up --build
```

4. Создать суперпользователя:

```bash
docker compose -f infra/docker-compose.yml exec backend python manage.py createsuperuser
```

5. Админ панель:

```
http://127.0.0.1:8081/admin/
```

6. Просмотр отчета:
```bash
docker compose -f infra/docker-compose.yml exec backend cat reports/metrics_report.txt
```

- [JWT авторизация](docs/auth.md)
- [API для работы с метриками](docs/metrics.md)

- Создание пользователей реализовано через админ панель, стандартными инструментами django
- Создане Тэгов реализовано через админ панель