# SafeSpace - Secure AI-Powered Mental Health Journaling Platform

A comprehensive MVP for a secure AI-powered mental health journaling platform designed for users in Pakistan. This monorepo contains both the Django backend and React frontend.

## 🎯 Features

- **Anonymous User Mode**: Users can register with a username/alias without requiring real identity
- **Daily Journaling**: Text and voice journal entries with encrypted storage
- **AI Analysis**: Automatic analysis of journal entries including:
  - 2-line summary
  - Sentiment score (-1 to +1)
  - Intensity score (0 to 1)
  - Key themes detection
  - Risk flag detection
  - Chat suggestion based on risk assessment
- **SOP-Driven Chatbot**: Empathetic chatbot that follows Standard Operating Procedures
  - Never provides medical advice, diagnosis, or therapy recommendations
  - Asks clarifying questions and gathers history
  - Automatic escalation for high-risk situations
- **Escalation Workflow**: Automatic escalation to verified professionals for review
- **Professional Dashboard**: Verified professionals can review escalation tickets and submit verdicts
- **7-Day Insights**: Trend analysis and insights from the last 7 days of journaling
- **Consent-Based History Sharing**: Users can grant consent to share history with professionals
- **Branded PDF Reports**: Generate and download branded PDF reports of patient history

## 🏗️ Architecture

### Monorepo Structure

```
safespace/
├── backend/              # Django + DRF backend
│   ├── apps/
│   │   ├── accounts/     # User authentication & profiles
│   │   ├── journal/      # Journal entries with encryption
│   │   ├── ai/           # AI analysis services
│   │   ├── chat/         # SOP-driven chatbot
│   │   ├── professionals/# Professional profiles & escalation
│   │   ├── consent/      # Consent management
│   │   └── history/      # History generation & PDF export
│   ├── config/           # Django settings
│   └── manage.py
├── frontend/             # React + Vite + Tailwind
│   └── src/
│       ├── api/          # API client functions
│       ├── components/   # Reusable components
│       ├── pages/        # Page components
│       └── contexts/     # React contexts
└── package.json          # Root scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd safespace
```

2. **Install dependencies**

```bash
# Install root dependencies (concurrently)
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

3. **Configure environment variables**

Create `backend/.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ENCRYPTION_KEY=your-32-byte-encryption-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

Create `frontend/.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

4. **Run database migrations**

```bash
cd backend
python manage.py migrate
```

5. **Create demo data**

```bash
python manage.py create_demo_data
```

This creates:
- 2 demo users (demo_user/demo123, test_user/test123)
- 8 verified professionals (all use password: professional123)
- 8 SOP documents for chatbot guidance

6. **Start the development servers**

From the root directory:

```bash
npm run dev
```

This will start:
- Django backend on `http://localhost:8000`
- React frontend on `http://localhost:5173`

## 📝 Demo Credentials

### Regular Users
- **Username**: `demo_user` | **Password**: `demo123`
- **Username**: `test_user` | **Password**: `test123`

### Professionals
- **Username**: `dr_ahmed` | **Password**: `professional123`
- **Username**: `dr_fatima` | **Password**: `professional123`
- (All professionals use the same password: `professional123`)

## 🔑 Key Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `GET /api/auth/me/` - Get current user

### Journal
- `POST /api/journal/` - Create journal entry
- `GET /api/journal/` - List user's journal entries
- `GET /api/journal/<id>/` - Get journal entry detail
- `DELETE /api/journal/<id>/` - Delete journal entry

### Chat
- `POST /api/chat/sessions/` - Create or get active session
- `POST /api/chat/sessions/<id>/message/` - Send message
- `GET /api/chat/sessions/<id>/messages/` - Get messages

### Professionals
- `GET /api/professionals/list/` - List verified professionals
- `POST /api/professionals/apply/` - Apply to become professional
- `GET /api/professionals/escalations/` - Get assigned escalations (professional only)
- `POST /api/professionals/escalations/<id>/verdict/` - Submit verdict (professional only)

### Consent & History
- `POST /api/consent/grant/` - Grant consent to professional
- `GET /api/consent/status/` - Get consent status
- `POST /api/history/generate/` - Generate history snapshot
- `GET /api/history/pdf/<snapshot_id>/` - Download PDF

## 🔒 Security Features

- **Field-Level Encryption**: Journal text and chat messages are encrypted at rest using `django-cryptography`
- **JWT Authentication**: Secure token-based authentication
- **Anonymous Mode**: Users can use aliases without revealing real identity
- **Role-Based Access Control**: Separate permissions for users and professionals

## 🤖 AI Analysis

The AI analysis service uses rule-based keyword matching for the MVP:

- **Sentiment Analysis**: Analyzes positive/negative keywords
- **Intensity Detection**: Detects intensifiers, exclamation marks, and capitalization
- **Theme Detection**: Identifies themes like anxiety, depression, stress, relationships, etc.
- **Risk Flagging**: Detects self-harm risk, panic, severe depression, isolation
- **7-Day Trend**: Analyzes trends over the last 7 days to suggest chat sessions

## 💬 Chatbot Behavior

The chatbot follows SOP documents created by professionals:

- **Empathetic Responses**: Always responds with empathy and validation
- **Information Gathering**: Asks clarifying questions to understand the situation
- **No Medical Advice**: Explicitly states it does not provide medical advice, diagnosis, or therapy
- **Automatic Escalation**: Escalates to professionals when dangerous levels are detected
- **SOP-Driven**: Uses keyword matching to select relevant SOP documents

## 📊 Escalation Workflow

1. User creates journal entry or sends chat message
2. AI analysis detects risk flags or dangerous keywords
3. Chatbot escalates session to professional queue
4. Escalation ticket is created and assigned to a verified professional (round-robin)
5. Professional reviews ticket and submits verdict:
   - `consult_required`: Professional consultation needed
   - `monitor`: Continue monitoring
   - `no_action`: No action required

## 📄 History Sharing

1. User grants consent to a verified professional
2. User generates history snapshot (last 7 days)
3. History includes:
   - Journal summaries with sentiment/intensity scores
   - Key themes and risk flags
   - Chat session highlights
   - Escalation history
   - Trend analysis
4. User can download branded PDF report
5. Professional can access history if consent is granted

## 🛠️ Development

### Backend Management Commands

```bash
# Create demo data
python manage.py create_demo_data

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Frontend Development

```bash
cd frontend
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

## 📦 Technology Stack

### Backend
- Django 4.2.7
- Django REST Framework 3.14.0
- SimpleJWT for authentication
- django-cryptography for field-level encryption
- ReportLab for PDF generation
- SQLite (dev) / PostgreSQL (production-ready)

### Frontend
- React 18.2
- Vite 5.0
- Tailwind CSS 3.3
- Framer Motion for animations
- Axios for API calls
- React Router for routing

## 🎨 UI/UX

- **Modern & Minimal**: Clean, calming design
- **Tasteful Animations**: Subtle transitions using Framer Motion
- **Responsive**: Works on desktop and mobile
- **Accessible**: Proper contrast and keyboard navigation
- **Anonymous Mode Badge**: Clear indication when in anonymous mode

## 📋 MVP Limitations

- Voice transcription is a placeholder (not implemented in MVP)
- No revoke consent functionality (as per requirements)
- Rule-based AI analysis (not ML-based)
- Simple keyword matching for SOP selection
- Local file storage for voice files (dev only)

## 🚧 Production Considerations

Before deploying to production:

1. Set `DEBUG=False` in Django settings
2. Use PostgreSQL instead of SQLite
3. Configure proper CORS origins
4. Set up proper encryption key management
5. Implement voice transcription service
6. Add rate limiting
7. Set up proper logging and monitoring
8. Configure HTTPS
9. Set up backup strategy
10. Add comprehensive error handling

## 📄 License

This project is for demonstration purposes.


## ⚠️ Disclaimer

This platform is for demonstration purposes only. It does not replace professional medical advice, diagnosis, or treatment. If you're in crisis, please contact emergency services immediately.
