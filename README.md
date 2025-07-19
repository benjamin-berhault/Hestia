# Family-Centered Relationship Platform - Complete Build Prompt for Cursor AI

## Project Overview
Build a complete, production-ready family-centered relationship platform for adults seeking committed relationships to start families. This is NOT for casual dating - it's for intentional people who want to build a life together without state-sanctioned marriage.

## Core Mission Statement
Create a private platform where emotionally mature adults can find committed partners to build families through mutual agreements, shared values, and parental responsibility - bypassing the legal/judicial risks of traditional marriage. The platform guides users toward understanding complementary masculine and feminine qualities that create strong, lasting partnerships and healthy family foundations. As the community grows, facilitate real-world connections through organized local events that recreate the natural courtship and community-building traditions of healthy societies.

## Technical Architecture Requirements

### Frontend Stack
- **Framework**: Vanilla JavaScript (ES6+) with modern DOM manipulation
- **Styling**: CSS3 with CSS Grid/Flexbox + CSS Custom Properties
- **Module System**: ES6 modules with dynamic imports
- **Build Tool**: Vite for development and bundling
- **Forms**: Native HTML5 validation + custom JavaScript validation
- **Authentication**: JWT tokens stored in httpOnly cookies
- **Image Handling**: Native File API + Canvas for client-side optimization

### Backend Stack
- **Framework**: FastAPI with Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens + FastAPI security utilities
- **File Storage**: MinIO for profile photos and documents
- **Email Service**: FastAPI-Mail or SMTP integration
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Deployment**: Docker containers (FastAPI + PostgreSQL + MinIO)

### Security & Privacy
- **Data Protection**: GDPR-compliant data handling
- **Content Moderation**: Automated + manual review system
- **Profile Verification**: Email + optional ID verification
- **Secure Messaging**: End-to-end encrypted conversations

## Feature Specifications

### 1. User Registration & Onboarding
**Registration Flow:**
- Email verification required
- Gender selection (Man/Woman) with role-specific guidance
- Multi-step onboarding questionnaire:
  - Demographics (age, location, education)
  - Family intentions (timeline for children, number desired)
  - Values assessment (religious/spiritual views, parenting philosophy)
  - Lifestyle preferences (living arrangements, career priorities)
  - Relationship goals (commitment level, timeline expectations)
  - Personal development goals and self-improvement journey

**Profile Creation with Gender-Specific Guidance:**

**For Men - Building Attractive Masculine Qualities:**
- Leadership assessment: Decision-making ability, vision for family future
- Provider mindset: Career stability, financial planning, ambition
- Physical fitness and health commitment
- Emotional stability and conflict resolution skills
- Protective instincts and family security priorities
- Personal mission and purpose beyond relationship
- Communication style and emotional intelligence

**For Women - Building Attractive Feminine Qualities:**
- Nurturing abilities: Emotional intelligence, care-giving nature
- Supportive partnership style: Encouraging growth, creating harmony
- Family-oriented priorities: Home-building, child-rearing values
- Grace and femininity: Social skills, relationship building
- Receptivity and appreciation: Ability to receive and acknowledge efforts
- Intuition and wisdom in family matters
- Life balance and wellness focus

**Universal Profile Elements:**
- Photo upload (3-6 photos required)
- Detailed bio section focusing on personal growth journey
- Family vision statement
- Deal-breakers and non-negotiables
- "What I Offer" and "What I Seek" sections
- Personal development and self-improvement goals

### 2. Search & Matching System
**Advanced Filtering:**
- Age range and location radius
- Timeline for children (within 1 year, 1-3 years, 3+ years)
- Number of children desired
- Education level and career ambitions
- Religious/spiritual alignment
- Parenting philosophy compatibility
- Living arrangement preferences
- Commitment timeline preferences
- Masculine/feminine energy balance preferences
- Personal development commitment level
- Family role preferences and expectations

**Gender-Specific Attraction Factors:**

**What Women Typically Seek in Men:**
- Leadership and decision-making capability
- Financial stability and provider potential
- Physical fitness and health consciousness
- Emotional maturity and communication skills
- Protective instincts and security-mindedness
- Clear life direction and personal mission
- Ability to plan and execute long-term goals
- Respect for feminine nature and supportive attitude

**What Men Typically Seek in Women:**
- Nurturing and caring nature
- Supportive and encouraging personality
- Feminine grace and social intelligence
- Family-oriented priorities and values
- Ability to create warm, welcoming home environment
- Receptivity and appreciation for efforts
- Emotional intelligence and intuition
- Respect for masculine leadership and vision

**Matching Algorithm:**
- Compatibility scoring based on complementary qualities
- Gender-specific attraction factor weighting
- Values alignment (traditional family roles, modern partnerships, etc.)
- Mutual growth potential assessment
- Life vision compatibility
- Communication style matching
- Weighted preferences (deal-breakers vs nice-to-haves)
- Activity-based matching (recent logins, engagement)

### 3. Communication System
**Secure Messaging:**
- Private messaging between matched users
- Conversation starters based on shared interests
- Photo/document sharing capabilities
- Video call integration (future enhancement)
- Message encryption for privacy

**Conversation Prompts:**
- Values-based discussion topics
- Family planning conversations
- Relationship role and expectation alignment
- Personal growth and development goals
- Masculine/feminine dynamic exploration
- Future planning scenarios
- Complementary strengths assessment
- Traditional vs modern relationship values discussion

### 4. Commitment Charter System
**Digital Agreement Builder:**
- Template-based relationship agreements
- Customizable terms for:
  - Financial responsibilities
  - Parenting decisions
  - Living arrangements
  - Conflict resolution methods
  - Relationship boundaries
  - Future planning commitments

**Charter Features:**
- Version control for agreement updates
- Both parties must agree to changes
- Digital signatures
- PDF export functionality
- Privacy-protected (not stored on platform permanently)

### 5. Guidance & Educational Content System
**Personal Development Resources:**

**For Men - Masculine Development:**
- Leadership skills in relationships and family
- Financial planning and provider mindset
- Physical fitness and health optimization
- Emotional intelligence and communication
- Conflict resolution and problem-solving
- Vision setting and goal achievement
- Protecting and providing for family
- Balancing work and family priorities

**For Women - Feminine Development:**
- Nurturing skills and emotional intelligence
- Creating harmony and supportive environments
- Feminine grace and social intelligence
- Intuitive decision-making in family matters
- Encouraging and uplifting communication
- Home-making and family-building skills
- Balancing personal goals with family priorities
- Receptivity and appreciation practices

**Universal Relationship Skills:**
- Healthy communication patterns
- Conflict resolution strategies
- Building trust and intimacy
- Financial partnership and planning
- Parenting preparation and philosophy
- Creating shared vision and goals
- Maintaining individual growth within partnership
- Building extended family and community connections

**Content Delivery:**
- Weekly articles and tips based on user interests
- Video content library with relationship experts
- Interactive self-assessment tools
- Progress tracking for personal development goals
- Community discussion forums (moderated)
- Recommended reading lists and resources

### 6. Local Events & Community Building System
**Event Categories:**

**Traditional Courtship Events:**
- Chaperoned group activities (hiking, cultural events, community service)
- Skill-sharing workshops (cooking, crafts, practical skills)
- Seasonal celebrations and holiday gatherings
- Family-friendly picnics and outdoor activities
- Educational seminars on relationships and family building
- Faith-based or spiritual community gatherings
- Dance lessons and social dancing events
- Book clubs focused on family and relationship topics

**Structured Social Interactions:**
- Speed meeting events with meaningful conversation prompts
- Group discussions on family values and life goals
- Mentorship circles with successful couples
- Volunteer opportunities for community service
- Skill exchanges (men teaching practical skills, women sharing domestic arts)
- Storytelling evenings about family traditions
- Intergenerational gatherings with elder wisdom sharing

**Event Management Features:**
- Geographic event organization by city/region
- RSVP system with attendance tracking
- Event feedback and safety reporting
- Volunteer coordinator roles for trusted community members
- Event photo sharing (with privacy controls)
- Follow-up connection facilitation after events
- Seasonal event calendar with traditional celebrations

**Community Building Tools:**
- Local chapter organization (city-based groups)
- Community leader identification and support
- Event hosting guidelines and training
- Safety protocols and background check integration
- Mentorship matching for new members
- Success story sharing from local communities
- Resource sharing for event planning and execution

**Event Safety & Guidelines:**
- Background checks for event organizers
- Clear behavioral expectations and dress codes
- Chaperone requirements for appropriate events
- Report system for inappropriate behavior
- Emergency contact protocols
- Insurance and liability considerations
- Age-appropriate event categorization

### 7. Admin Dashboard & Moderation
**Content Moderation:**
- Automated photo screening
- Message content filtering
- Reported user review system
- Manual profile approval process
- Event safety monitoring and incident reporting
- Community leader oversight and feedback

**Analytics Dashboard:**
- User engagement metrics
- Matching success rates
- Platform growth statistics
- Content moderation queue
- Event attendance and success tracking
- Community health metrics by region
- Local chapter growth and activity levels

**User Management:**
- Account verification status
- Suspension/ban capabilities
- Support ticket system
- Communication logs (for safety)
- Event organizer approval and training
- Community leader certification process

## Database Schema Requirements

### SQLAlchemy Models:
```python
# Core tables with SQLAlchemy models
# users - authentication and basic info
# user_profiles - detailed profile information  
# user_photos - MinIO file references with metadata
# user_preferences - search and matching criteria
# matches - compatibility scores and match status
# conversations - message threads between users
# messages - individual messages with encryption
# charter_templates - reusable agreement templates
# user_charters - custom relationship agreements
# events - local community events and gatherings
# event_attendees - RSVP tracking and attendance
# local_chapters - geographic community organization
# community_leaders - trusted organizers and mentors
# event_feedback - post-event reviews and safety reports
# reports - user reports for moderation
# admin_actions - audit trail for admin activities
```

### FastAPI Endpoints Structure:
```python
# Authentication routes (/auth)
# User management routes (/users)
# Profile routes (/profiles)
# Photo upload routes (/photos) - MinIO integration
# Matching routes (/matches)
# Messaging routes (/messages)
# Charter routes (/charters)
# Events routes (/events) - local event management
# Community routes (/community) - chapters and leaders
# Admin routes (/admin)
```

## UI/UX Design Guidelines

### Design Principles:
- **Trust & Safety**: Clean, professional aesthetic that conveys seriousness
- **Simplicity**: Intuitive navigation, minimal cognitive load
- **Warmth**: Inviting colors and imagery that feel family-oriented
- **Privacy**: Clear privacy controls and settings visibility
- **Community**: Design elements that encourage real-world connections

### Color Palette:
- Primary: Warm earth tones (sage green, warm beige)
- Secondary: Soft blues and warm grays
- Accent: Golden yellow for highlights
- Error states: Muted reds
- Success states: Natural greens

### Frontend Structure:
```
frontend/
├── index.html (landing page)
├── css/
│   ├── main.css (global styles)
│   ├── components.css (reusable components)
│   └── pages.css (page-specific styles)
├── js/
│   ├── main.js (app initialization)
│   ├── api.js (API communication layer)
│   ├── auth.js (authentication handling)
│   ├── guidance.js (educational content system)
│   ├── matching.js (attraction factors and compatibility)
│   ├── events.js (local event management and RSVP)
│   ├── community.js (chapter organization and networking)
│   ├── components/ (reusable UI components)
│   ├── pages/ (page-specific logic)
│   └── utils/ (helper functions)
├── assets/
│   ├── images/
│   └── icons/
└── pages/
    ├── register.html
    ├── profile.html
    ├── browse.html
    ├── messages.html
    ├── events.html
    ├── community.html
    └── admin.html
```

### Backend Structure:
```
backend/
├── main.py (FastAPI application)
├── models/ (SQLAlchemy models)
├── routes/ (API endpoint handlers)
├── services/ (business logic)
├── guidance/ (educational content management)
├── matching/ (attraction factors and compatibility algorithms)
├── events/ (local event management and community building)
├── utils/ (helper functions)
├── config.py (environment configuration)
├── database.py (PostgreSQL connection)
├── minio_client.py (MinIO integration)
└── requirements.txt
```

## Implementation Strategy

### Phase 1: Backend Foundation (Weeks 1-2)
- FastAPI application setup with SQLAlchemy
- PostgreSQL database with core models
- MinIO integration for file storage
- JWT authentication system
- Basic CRUD operations for users and profiles
- API documentation with Swagger

### Phase 2: Frontend Core (Weeks 3-4)
- Vanilla JS application structure with Vite
- Authentication flow (login/register)
- Profile creation and photo upload to MinIO
- Basic search and filtering interface
- Responsive CSS design system

### Phase 3: Community & Events (Weeks 5-8)
- Local events system with RSVP management
- Community chapter organization by geography
- Event safety protocols and reporting
- Matching algorithm implementation
- Real-time messaging system
- Commitment charter builder
- Admin dashboard for moderation
- Email notifications

### Phase 4: Advanced Features & Polish (Weeks 9-12)
- Event feedback and success tracking
- Community leader identification system
- Mentorship and elder wisdom integration
- Docker containerization
- Security auditing and testing
- Performance optimization
- Production deployment with Docker Compose
- Beta user testing with local pilot events

## Content & Community Guidelines

### Platform Rules:
- Serious intentions only - no casual dating
- Commitment to personal growth and development
- Respectful communication honoring masculine/feminine differences
- Accurate profile information mandatory
- Openness to traditional relationship dynamics and family roles
- No solicitation or commercial activity
- Report suspicious or inappropriate behavior
- Participate constructively in educational content and discussions

### Success Metrics:
- User engagement (daily/weekly active users)
- Match quality (conversations started, depth of connections)
- Relationship formation (users leaving platform together)
- Safety metrics (reports resolved, user satisfaction)
- Charter creation rates and relationship commitments
- Personal development content engagement
- Educational resource completion rates
- Event attendance rates and regional growth
- Community health metrics (local chapter activity)
- Real-world relationship success tracking
- Intergenerational wisdom sharing engagement
- Traditional courtship event success rates

## Technical Implementation Notes

### Performance Requirements:
- Page load times under 2 seconds
- Mobile-first responsive design
- Accessible design (WCAG 2.1 AA)
- SEO optimized for organic discovery

### Scalability Considerations:
- Database indexing for search performance
- Image optimization and CDN usage
- Caching strategy for frequent queries
- Rate limiting for API endpoints

### Deployment & DevOps

### Docker Configuration:
- **FastAPI Container**: Python 3.9 + FastAPI + SQLAlchemy
- **PostgreSQL Container**: Official PostgreSQL 14+ image
- **MinIO Container**: Official MinIO server image
- **Nginx Container**: Reverse proxy for frontend and API
- **Docker Compose**: Orchestration for all services

### Environment Setup:
```yaml
# docker-compose.yml structure
version: '3.8'
services:
  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - MINIO_ENDPOINT=minio:9000
  db:
    image: postgres:14
  minio:
    image: minio/minio
  frontend:
    build: ./frontend
    depends_on: [api]
```

### Development Environment:
- Local development with Docker Compose
- Hot reloading for both frontend (Vite) and backend (FastAPI)
- PostgreSQL with sample data seeding
- MinIO with development buckets
- Environment variable management

### Monitoring & Analytics:
- Error tracking (Sentry)
- Performance monitoring
- User analytics (privacy-compliant)
- Uptime monitoring
- Database performance tracking

---

## CURSOR INSTRUCTIONS:

1. **Start with project setup**: Initialize FastAPI backend with PostgreSQL and MinIO, then create Vite frontend
2. **Build incrementally**: Complete each feature fully before moving to the next
3. **Focus on security**: Implement authentication and data protection from the start
4. **Test everything**: Write unit tests for critical functionality
5. **Document as you go**: Include README with setup instructions and API documentation
6. **Make it production-ready**: Include error handling, validation, and user feedback

**Begin with**: "Set up the FastAPI backend with PostgreSQL and MinIO integration, including user authentication and basic CRUD operations. Then create the Vanilla JavaScript frontend with Vite build system and implement the authentication flow. Finally, set up Docker containers for all services."

**Context**: This is a serious platform for adults seeking life partners, not a casual dating app. Every design decision should reflect maturity, intentionality, and trustworthiness. Use modern vanilla JavaScript patterns and FastAPI best practices for a clean, maintainable codebase. The platform should recreate the natural courtship and community-building traditions that historically created strong families and stable societies.