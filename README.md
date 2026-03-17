# Employee Management REST API

A simple Flask REST backend using **SQLite in-memory database**.  
No config, no files, no setup — just run and use. Data resets on every restart.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Run Locally](#run-locally)
- [Run with Docker](#run-with-docker)
- [Build & Push Docker Image Manually](#build--push-docker-image-manually)
- [Run Tests](#run-tests)
- [Deploy to Render](#deploy-to-render)
- [API Endpoints](#api-endpoints)
- [API Usage Examples](#api-usage-examples)
- [GitHub Actions CI/CD](#github-actions-cicd)

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | https://python.org |
| pip | latest | bundled with Python |
| Docker | 24+ | https://docs.docker.com/get-docker |
| Docker Compose | v2+ | bundled with Docker Desktop |
| Git | any | https://git-scm.com |

---

## Project Structure

```
employeemgnt/
├── app.py                  # Flask app — all routes and model
├── requirements.txt        # Python dependencies
├── Procfile                # Render start command
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Local Docker orchestration
├── .gitignore
├── README.md
├── tests/
│   └── test_app.py         # Pytest test suite
└── .github/
    └── workflows/
        └── ci-cd.yml       # GitHub Actions pipeline
```

---

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/employeemgnt.git
cd employeemgnt
```

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

| URL | Description |
|-----|-------------|
| http://localhost:5000/all | List all employees |
| http://localhost:5000/apidocs | Swagger UI (interactive docs) |
| http://localhost:5000/health | Health check |

> ℹ️ Data lives in memory only. It is cleared every time the app restarts.

---

## Run with Docker

### Build and start

```bash
docker-compose up --build
```

App runs at **http://localhost:5000**

### Stop

```bash
docker-compose down
```

> ℹ️ No volumes are used. Data is lost when the container stops — same behaviour as running locally.

---

## Build & Push Docker Image Manually

### Build the image

```bash
docker build -t employeemgnt:latest .
```

### Run the container

```bash
docker run -d --name employeemgnt -p 5000:5000 employeemgnt:latest
```

### Useful commands

```bash
docker logs -f employeemgnt       # tail logs
docker stop employeemgnt          # stop container
docker rm employeemgnt            # remove container
docker ps                         # list running containers
```

### Tag and push to Docker Hub

```bash
docker login
docker tag employeemgnt:latest <your-dockerhub-username>/employeemgnt:latest
docker push <your-dockerhub-username>/employeemgnt:latest
```

### Pull and run from Docker Hub on any machine

```bash
docker run -d -p 5000:5000 <your-dockerhub-username>/employeemgnt:latest
```

---

## Run Tests

```bash
pytest tests/ -v
```

---

## Deploy to Render

> ℹ️ Since the app uses an in-memory database, data resets on every Render redeploy or restart.  
> This is expected and fine for a demo / dev service.

> ⚠️ Render free services spin down after 15 minutes of inactivity. The first request after  
> a sleep may take 30–60 seconds (cold start). Subsequent requests are fast.

### Option A — Deploy from GitHub (recommended)

#### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<your-username>/employeemgnt.git
git push -u origin main
```

#### Step 2 — Create a Web Service on Render

1. Go to https://dashboard.render.com
2. Click **New → Web Service**
3. Connect your GitHub account and select the `employeemgnt` repo
4. Fill in:

   | Field | Value |
   |-------|-------|
   | **Name** | `employeemgnt` |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn --bind 0.0.0.0:5000 --workers 1 app:app` |
   | **Plan** | Free |

5. Click **Create Web Service**

Your API will be live at:
```
https://employeemgnt.onrender.com
```

#### Step 3 — Test your live API

```bash
curl https://employeemgnt.onrender.com/health

curl -X POST https://employeemgnt.onrender.com/add \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "Subba Reddy", "salary": 75000}'

curl https://employeemgnt.onrender.com/all
```

---

### Option B — Deploy from Docker Hub

1. Push your image to Docker Hub (see section above)
2. Go to **Render → New → Web Service**
3. Choose **Deploy an existing image from a registry**
4. Enter: `docker.io/<your-dockerhub-username>/employeemgnt:latest`
5. Set **Port** to `5000`
6. Click **Create Web Service**

---

### Redeployment

Every push to `main` triggers an automatic redeploy on Render (when connected to GitHub).  
For a manual redeploy: Dashboard → your service → **Manual Deploy → Deploy latest commit**.

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/add` | Add a new employee |
| `GET` | `/byId/<emp_id>` | Get employee by ID |
| `GET` | `/byName/<name>` | Get employee by name |
| `GET` | `/all` | Get all employees |
| `PUT` | `/update` | Update employee details |
| `DELETE` | `/delete/<emp_id>` | Delete by ID |
| `POST` | `/delete` | Delete via form field `delete_id` |
| `GET` | `/health` | Health check |

Full interactive docs: **http://localhost:5000/apidocs**

---

## API Usage Examples

### Add employee (JSON)
```bash
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "name": "Subba Reddy", "salary": 75000}'
```

### Add employee (form data)
```bash
curl -X POST http://localhost:5000/add \
  -F "id=2" -F "name=Ravi Kumar" -F "salary=60000"
```

### Get all employees
```bash
curl http://localhost:5000/all
```

### Get by ID
```bash
curl http://localhost:5000/byId/1
```

### Get by name
```bash
curl http://localhost:5000/byName/Subba%20Reddy
```

### Update employee
```bash
curl -X PUT http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{"emp_id": 1, "name": "Subba Reddy", "salary": 90000}'
```

### Delete by ID (DELETE)
```bash
curl -X DELETE http://localhost:5000/delete/1
```

### Delete via form POST
```bash
curl -X POST http://localhost:5000/delete -F "delete_id=2"
```

### Health check
```bash
curl http://localhost:5000/health
```

---

## GitHub Actions CI/CD

Defined in `.github/workflows/ci-cd.yml`.

| Trigger | Action |
|---------|--------|
| Push or PR to `main` | Runs the full test suite |
| Push to `main` (tests pass) | Builds and pushes Docker image to Docker Hub |

### Setup

1. Push the repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add secrets:

   | Secret | Value |
   |--------|-------|
   | `DOCKERHUB_USERNAME` | Your Docker Hub username |
   | `DOCKERHUB_TOKEN` | Your Docker Hub access token — https://hub.docker.com/settings/security |

4. Rename `github_workflows/` → `.github/workflows/`:

   **Windows:**
   ```bash
   mkdir .github\workflows
   move github_workflows\ci-cd.yml .github\workflows\ci-cd.yml
   rmdir github_workflows
   ```

   **Linux / macOS:**
   ```bash
   mkdir -p .github/workflows
   mv github_workflows/ci-cd.yml .github/workflows/ci-cd.yml
   rmdir github_workflows
   ```

---

## License

MIT
