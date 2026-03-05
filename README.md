# Backend database connection example

This project now includes a lightweight backend server connected to a SQLite database.

## Run

```bash
python3 server.py
```

By default it starts on `http://0.0.0.0:8000` and uses `app.db`.

## Environment variables

- `DB_PATH`: path to SQLite database file (default: `app.db`)
- `HOST`: server bind host (default: `0.0.0.0`)
- `PORT`: server bind port (default: `8000`)

## Endpoints

- `GET /health` - health check including DB path
- `GET /users` - list users
- `POST /users` - create user with JSON body:

```json
{
  "name": "Ada Lovelace",
  "email": "ada@example.com"
}
```
