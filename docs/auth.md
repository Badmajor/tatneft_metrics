
# JWT Authentication API (SimpleJWT)

## Описание

В проекте используется **JWT-аутентификация** на базе
`djangorestframework-simplejwt`.

JWT-токены используются для:

* аутентификации пользователей
* доступа к защищённым API-эндпоинтам

---

## Эндпоинты

### Получение токенов

**POST** `/api/token/`

Используется для получения пары токенов:

* `access`
* `refresh`

#### Тело запроса

```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

#### Успешный ответ (200)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### Обновление access-токена

**POST** `/api/token/refresh/`

Используется, когда `access` токен истёк.

#### Тело запроса

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Успешный ответ (200)

```json
{
  "access": "new_access_token"
}
```

---

## Использование access-токена

Для доступа к защищённым эндпоинтам необходимо передавать
`access` токен в HTTP-заголовке:

```
Authorization: Bearer <access_token>
```

### Пример

```http
GET /api/metrics/
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
```

---

## Время жизни токенов

ACCESS_TOKEN - 60 минут,
REFRESH_TOKEN_LIFETIME - 24 часа,

---

## Типичные ошибки

### 401 Unauthorized

* Неверный логин или пароль
* Истёк `access` токен
* Не передан заголовок `Authorization`

### 403 Forbidden

* Недостаточно прав для доступа к ресурсу
