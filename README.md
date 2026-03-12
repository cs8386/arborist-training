# Arborist Training Tracker

Track arboriculture trainings and generate Google Slides presentations using **Claude** with content based on:

- **ISA** – International Society of Arboriculture best practices  
- **ANSI Z133** – Arboriculture safety requirements  
- **OSHA Crane** – Crane and derrick best practices  

## Features

- Create and manage training records
- Use Claude to generate slide content aligned with industry standards
- Save presentations directly to your Google Drive
- Track training status and slide links

## Setup

### 1. Install dependencies

```bash
cd arborist-training-app
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get API keys

**Anthropic (Claude)**  
- Go to [console.anthropic.com](https://console.anthropic.com)
- Create an API key and copy it

**Unsplash (optional – for images in slides)**  
- Go to [unsplash.com/developers](https://unsplash.com/developers)
- Create an app and copy the Access Key
- Add `UNSPLASH_ACCESS_KEY=...` to your `.env`
- If not set, slides are generated without images

**Google (Slides & Drive)**  
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create a project or use an existing one
- Enable **Google Slides API** and **Google Drive API**
- Configure OAuth consent screen (external user type if needed)
- Create OAuth 2.0 credentials (Web application)
- Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
- Copy the Client ID and Client Secret

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLIENT_ID=...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=...
SECRET_KEY=your-random-secret-key
BASE_URL=http://localhost:8000
ACCESS_PASSWORD=your_shared_password   # Required - share with allowed users
```

**Security**: Keep `.env` out of git (it's in `.gitignore`). API keys and the password stay server-side only. On GitHub, only your code is visible—never your secrets.

### 4. Run the app

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Usage

1. **Log in** – Enter the access password (shared with allowed users).
2. **Link Google** (owner only, once) – Click “Link Google Account” to connect your Drive. Slides from all users go to your Drive.
3. **Create a training** – Click “+ New Training”, fill in title, description, standard (ISA, ANSI Z133, or OSHA Crane), and topics.
4. **Generate slides** – Click “Generate Slides” on a training. Claude will create content, and the app will create a new presentation in your Google Drive.

## Project structure

```
arborist-training-app/
├── app/
│   ├── api/           # API routes (trainings, auth)
│   ├── models/        # SQLite models
│   ├── services/      # Claude & Google Slides
│   └── utils/         # Google OAuth
├── static/            # Frontend (HTML, CSS, JS)
├── .env.example
├── requirements.txt
└── README.md
```

## Tech stack

- **Backend**: FastAPI, SQLAlchemy, SQLite  
- **AI**: Anthropic Claude (Sonnet)  
- **Slides**: Google Slides API, Google Drive API  
- **Frontend**: Vanilla JS, no build step  
