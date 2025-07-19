# Family-Centered Relationship Platform

A comprehensive platform for adults seeking committed relationships to start families, built with FastAPI and vanilla JavaScript.

## 🎯 Mission

Create a private platform where emotionally mature adults can find committed partners to build families through mutual agreements, shared values, and parental responsibility - bypassing the legal/judicial risks of traditional marriage.

## ✨ Features

### Core Functionality
- **User Authentication** - Secure JWT-based auth with email verification
- **Profile Management** - Comprehensive profiles with family goals and values
- **Smart Matching** - Compatibility algorithm based on family timelines and values
- **Secure Messaging** - End-to-end encrypted conversations
- **Photo Management** - Secure photo upload with MinIO object storage
- **Charter System** - Digital relationship agreement builder
- **Admin Dashboard** - Content moderation and user management

### Safety & Security
- Email verification required
- Profile photo moderation
- Secure messaging with encryption
- Report system for inappropriate behavior
- Privacy-first design with GDPR compliance

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh capability
- **File Storage**: MinIO for profile photos and documents
- **Email**: FastAPI-Mail with SMTP integration
- **Caching**: Redis for sessions and performance

### Frontend (Vanilla JavaScript)
- **Build Tool**: Vite for development and bundling
- **Styling**: CSS3 with CSS Grid/Flexbox + Custom Properties
- **Module System**: ES6 modules with dynamic imports
- **Forms**: Native HTML5 validation + custom JavaScript validation
- **API Client**: Axios for HTTP requests

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 14+
- **Object Storage**: MinIO server
- **Caching**: Redis 7
- **Reverse Proxy**: Nginx (production)

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd family-platform
```

### 2. Environment Setup
```bash
# Copy environment variables
cp backend/.env.example backend/.env

# Edit the environment variables
# Update SECRET_KEY, EMAIL credentials, etc.
nano backend/.env
```

### 3. Start with Docker Compose
```bash
# Start all services (database, API, frontend, MinIO, Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 4. Access the Application
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/api/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Database**: localhost:5432 (family_user/family_pass/family_db)

## 🛠️ Development Setup

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Database Management
```bash
# Access PostgreSQL
docker exec -it family_platform_db psql -U family_user -d family_db

# View database logs
docker logs family_platform_db
```

## 📁 Project Structure

```
family-platform/
├── backend/                 # FastAPI backend
│   ├── models/             # SQLAlchemy database models
│   ├── routes/             # API endpoint handlers
│   ├── services/           # Business logic
│   ├── utils/              # Helper functions
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # Vanilla JS frontend
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript modules
│   ├── pages/              # HTML pages
│   ├── assets/             # Static assets
│   ├── index.html          # Landing page
│   ├── package.json        # Node.js dependencies
│   └── vite.config.js      # Vite configuration
├── docker-compose.yml      # Multi-service orchestration
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://family_user:family_pass@db:5432/family_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Email (Gmail example)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@familyplatform.com

# MinIO Object Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Application
DEBUG=true
APP_NAME=Family-Centered Relationship Platform
```

### Database Schema

The platform uses the following core models:
- **Users** - Authentication and basic info
- **UserProfiles** - Detailed profile information
- **UserPhotos** - MinIO file references with metadata
- **UserPreferences** - Search and matching criteria
- **Matches** - Compatibility scores and match status
- **Conversations** - Message threads between users
- **Messages** - Individual messages with encryption
- **CharterTemplates** - Reusable agreement templates
- **UserCharters** - Custom relationship agreements
- **Reports** - User reports for moderation
- **AdminActions** - Audit trail for admin activities

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v

# Run with coverage
pytest --cov=. tests/
```

### Frontend Tests
```bash
cd frontend
npm test

# Run linting
npm run lint
```

## 🚢 Deployment

### Production Environment
```bash
# Build and deploy with production profile
docker-compose --profile production up -d

# SSL certificates should be placed in nginx/ssl/
# Update nginx/nginx.conf for your domain
```

### Environment Checklist
- [ ] Change default passwords and secret keys
- [ ] Configure SSL certificates
- [ ] Set up email SMTP credentials
- [ ] Configure backup strategy for PostgreSQL
- [ ] Set up monitoring and logging
- [ ] Configure domain and DNS
- [ ] Review CORS and security settings

## 🔒 Security Features

### Authentication & Authorization
- JWT tokens with automatic refresh
- Secure password hashing with bcrypt
- Email verification required for activation
- Role-based access control (User/Moderator/Admin)

### Data Protection
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with content security policies
- Rate limiting on sensitive endpoints
- Secure file upload with type validation

### Privacy
- End-to-end encrypted messaging
- GDPR-compliant data handling
- User data export and deletion
- Private relationship agreements
- Secure MinIO object storage

## 📊 Monitoring & Analytics

### Health Checks
- Application health endpoint: `/health`
- Database connectivity monitoring
- MinIO storage availability
- Redis cache status

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- User action audit trails
- Performance metrics

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Code Standards
- Python: Follow PEP 8, use type hints
- JavaScript: ESLint configuration included
- CSS: Use CSS custom properties, follow BEM methodology
- Git: Conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Email: support@familyplatform.com
- Documentation: See `/api/docs` when running

## 🗺️ Roadmap

### Phase 1 (Current)
- [x] Core authentication system
- [x] Basic profile management
- [x] Photo upload functionality
- [x] Database schema and models
- [x] Docker containerization

### Phase 2 (Next)
- [ ] Matching algorithm implementation
- [ ] Real-time messaging system
- [ ] Charter builder interface
- [ ] Admin moderation tools
- [ ] Email notification system

### Phase 3 (Future)
- [ ] Mobile app development
- [ ] Video calling integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] API rate limiting and caching

---

**Building meaningful relationships for family-focused adults.** 💕👨‍👩‍👧‍👦