# AI Payroll Assistant

An intelligent, dual-role (Employee & HR) payroll assistant built with a deterministic statutory payroll calculation engine, FastAPI backend with CrewAI/OpenAI integration, and a modern React (Vite + TypeScript + Tailwind) frontend.

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
5. Click **Deploy**. Vercel will build and assign a production URL (e.g., `https://ai-payroll-frontend.vercel.app`).

---

### Step 4: Link Frontend and Backend (CORS Configuration)
1. Copy your Vercel deployment URL from Step 3 (e.g., `https://ai-payroll-frontend.vercel.app`).
2. Go back to your Render backend dashboard > **Environment**.
3. Update `FRONTEND_ORIGIN`:
   - Value: `https://ai-payroll-frontend.vercel.app` (your actual Vercel domain, without a trailing slash).
4. Save changes. Render will automatically redeploy the backend with the new allowed CORS origin.

---

### Step 5: Test the Live Link
1. **Health Check**:
   Open in your browser: `https://<your-render-backend-url>/api/health`
   - Expected response: `{"status": "ok"}`
2. **Web App Interface**:
   Open your Vercel production URL: `https://<your-vercel-frontend-url>`
3. **Smoke Test**:
   - Verify the top demo bar shows the active employee (e.g., Neha Sharma `E05`) and the month selector.
   - Ask a question in chat: *"Why is my September salary lower than August?"*
   - Verify the AI response generates correctly with verified payroll numbers and breakdown cards.
   - Switch role to HR (`Anita Desai HR01`), ask: *"What needs my approval?"* and verify proposal cards load.
4. **Protections Active**:
   - Public IP rate limiting protects the `/api/chat` endpoint at 20 requests/minute/IP.
   - Daily live AI call cap automatically protects the OpenAI budget at 300 calls/day, with graceful fallback to deterministic statutory message templates if reached.

---

## Local Development

### 1. Engine & Backend
```bash
# Backend virtual environment
cd app/backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Start backend server
uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend
```bash
cd app/frontend
npm install
npm run dev
```

### 3. Test Suites
- Engine tests: `pytest engine/tests`
- Backend tests: `pytest app/backend/tests`
- Frontend tests: `cd app/frontend && npm test -- --run`
- Frontend production build: `cd app/frontend && npm run build`

