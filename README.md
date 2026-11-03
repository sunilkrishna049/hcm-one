# HCM One

HCM One is an agentic AI payroll assistant for Indian payroll, with an HR view and an Employee view. A deterministic payroll engine does every calculation, a FastAPI backend uses CrewAI and OpenAI only to understand the question, and a React (Vite + TypeScript + Tailwind) frontend shows approved replies and cards.

---

## Live demo

Live demo: https://hcm-one-nine.vercel.app
Switch between HR view and Employee view at the top. Use Reset Demo to start over.
The backend runs on a free server that sleeps when unused. The first request after a quiet period can take up to a minute; the app shows "Waking up the demo server" while it starts.

---

## Demo data

All employees, salaries, tax details and records in this project are fictional and created for the demo. No real person or company data is used. This is not a tool for real payroll.

---

## AI Architecture: DEC-044 (Option A)

HCM One operates under **Option A ("The AI understands; approved templates speak")**:
- **Intent Understanding & Entity Extraction**: The AI (CrewAI + OpenAI) classifies user questions and extracts entities (employee names, months, bonus types).
- **Sentence Drafting**: AI free-form sentence generation is disabled (`AI_DRAFTING_ENABLED = False`). All user-facing messages are rendered strictly using approved message templates (`ai_messages.py`).
- **Calculation & Data Integrity**: All numbers, deductions, arrears, and eligibility counts come deterministically from the payroll engine and pass mechanical runtime guards.

---

## Design documentation

- [output/](output/) (design deliverables: brief, research, personas, journey maps, screen specs, evaluation)
- [project-memory/design-decisions.md](project-memory/design-decisions.md) (decision log)

---

## Deploy

Step-by-step instructions for the project owner to deploy the application to production using a private GitHub repository, Render for the backend, and Vercel for the frontend.

### Step 1: Push Code to a Private GitHub Repository
1. Create a new **Private** repository on [GitHub](https://github.com/new) (e.g., `ai-payroll-assistant`).
2. Add the remote and push your `master` branch:
   ```bash
   git remote add origin https://github.com/<your-username>/ai-payroll-assistant.git
   git branch -M master
   git push -u origin master
   ```
   *(Note: `.env`, `data/runtime/`, and eval log `.jsonl` files are strictly excluded by `.gitignore` and will never be pushed).*

---

### Step 2: Deploy Backend on Render
1. Sign in to [Render](https://render.com) and click **New +** > **Web Service**.
2. Connect your private GitHub repository (`ai-payroll-assistant`).
3. Configure the service settings:
   - **Name**: `ai-payroll-backend` (or your preferred name)
   - **Region**: Choose the closest region (e.g., Singapore or Oregon)
   - **Branch**: `master`
   - **Root Directory**: Leave blank (root of repository)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r app/backend/requirements.txt`
   - **Start Command**: `uvicorn app.backend.main:app --host 0.0.0.0 --port $PORT`
     *(Render will also automatically detect `render.yaml` or `Procfile` if using Infrastructure as Code)*
4. Set Environment Variables in Render (**Environment** tab):
   - `PYTHON_VERSION`: `3.12.14`
   - `OPENAI_API_KEY`: `<your-openai-api-key>`
   - `AI_MODE`: `true`
   - `OPENAI_MODEL`: `gpt-4o-mini`
   - `FRONTEND_ORIGIN`: Temporarily set to `http://localhost:5173` (we will update this with the real Vercel URL in Step 4).
5. Click **Create Web Service**. Wait for the build to finish.
6. Copy your Render backend URL (e.g., `https://ai-payroll-backend.onrender.com`).

---

### Step 3: Deploy Frontend on Vercel
1. Sign in to [Vercel](https://vercel.com) and click **Add New...** > **Project**.
2. Import your private GitHub repository (`ai-payroll-assistant`).
3. Configure the project:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click "Edit" and select `app/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable (**Environment Variables** section):
   - Key: `VITE_API_BASE_URL`
   - Value: Your Render backend URL from Step 2 (e.g., `https://ai-payroll-backend.onrender.com` — without a trailing slash).
5. Click **Deploy**. Vercel will build and assign a production URL (e.g., `https://hcm-one-nine.vercel.app`).

---

### Step 4: Link Frontend and Backend (CORS Configuration)
1. Copy your Vercel deployment URL from Step 3 (e.g., `https://hcm-one-nine.vercel.app`).
2. Go back to your Render backend dashboard > **Environment**.
3. Update `FRONTEND_ORIGIN`:
   - Value: `https://hcm-one-nine.vercel.app` (your actual Vercel domain, without a trailing slash).
4. Save changes. Render will automatically redeploy the backend with the new allowed CORS origin.

---

### Step 5: Test the Live Link
1. **Health Check**:
   Open in your browser: `https://<your-render-backend-url>/api/health`
   - Expected response: `{"status": "ok"}`
2. **Web App Interface**:
   Open your Vercel production URL: `https://<your-vercel-frontend-url>`
3. **Smoke Test**:
   - In HR view, click "Select an employee", search for "Neha" and pick Neha Gupta. Her options appear as chips.
   - Ask: "What needs my approval?" and check that proposal cards load.
   - Switch to Employee view and ask: "Why is my September salary lower than August?" Check that the reply uses an approved template and the numbers come from the payroll engine.
4. **Protections Active**:
   - Public IP rate limiting protects the `/api/chat` endpoint at 20 requests/minute/IP.
   - Daily live AI call cap automatically protects the OpenAI budget at 300 calls/day, with graceful fallback to deterministic statutory message templates if reached.

---

## Local Development

### 1. Engine & Backend
```bash
# Backend virtual environment (from repository root)
python -m venv app/backend/.venv
source app/backend/.venv/bin/activate  # Or app\backend\.venv\Scripts\activate on Windows
pip install -r app/backend/requirements.txt

# Start backend server (run from repository root)
uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend
```bash
cd app/frontend
npm install
npm run dev
```

### 3. Test Suites
- Engine tests: `python -m pytest engine/tests`
- Backend tests: `python -m pytest app/backend/tests`
- Frontend tests: `cd app/frontend && npm test -- --run`
- Frontend production build: `cd app/frontend && npm run build`

---

## Credits

Designed and built by Sunil Krishna (UX designer) with AI coding agents, as a portfolio project for the UXMint AI for Designers course.
