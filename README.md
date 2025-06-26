# 📸 Website Screenshot API

A simple, containerized API service that captures website screenshots using **FastAPI + Playwright**, with Redis-based **compressed caching**.

---

## 🚀 Features

- 🔗 Accepts any `http(s)` URL
- 📐 Customizable screen size (`width` x `height`)
- ⏱️ Configurable delay before capture
- 🧠 Redis cache with 1-hour expiry (compressed with zlib)
- 🐳 Docker + Docker Compose for easy deployment

---

## ⚙️ Technologies

- Python
- FastAPI
- Playwright
- Redis
- Docker Compose

---

## 🧪 API Usage

```
GET /screenshot
```

### Query Parameters

| Param    | Type | Default | Description                              |
|----------|------|---------|------------------------------------------|
| `url`    | str  | —       | Website URL (must start with http/https) |
| `width`  | int  | 1280    | Screenshot viewport width in pixels      |
| `height` | int  | 720     | Screenshot viewport height in pixels     |
| `delay`  | int  | 1       | Delay in seconds before screenshot       |

### Example

```bash
curl "http://localhost:8000/screenshot?url=https://example.com&width=1280&height=720&delay=2" --output screenshot.png
```

