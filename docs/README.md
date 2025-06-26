# Catalyst System v1

A comprehensive relationship coaching platform that provides real-time AI-powered insights and analysis for improving communication and relationship dynamics.

## 🌟 Features

### Core Platform

- **Project Management**: Create and manage relationship improvement projects
- **Real-time Analysis**: AI-powered sentiment and communication pattern analysis
- **Timeline Tracking**: Visual timeline of relationship milestones and events
- **Analytics Dashboard**: Comprehensive insights and progress tracking
- **Goal Setting**: Set and track relationship goals with milestone tracking

### AI Whisper System

- **Real-time Coaching**: Live suggestions during conversations
- **Multi-platform Support**: Works across WhatsApp, Messenger, Discord, Slack, Teams, and Telegram
- **Smart Suggestions**: Context-aware communication improvements
- **Privacy-focused**: Local processing with secure data handling

### Chrome Extension

- **Seamless Integration**: Works directly in your messaging platforms
- **Non-intrusive**: Subtle suggestions that don't interrupt conversations
- **Cross-platform**: Supports major messaging platforms
- **Real-time Processing**: Instant analysis and feedback

## 🏗️ Architecture

```
catalyst_system/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Application entry point
│   ├── routers/            # API route handlers
│   │   ├── projects.py     # Project management endpoints
│   │   ├── analysis.py     # Analysis and whisper endpoints
│   │   └── advanced_analytics.py # Advanced analytics endpoints
│   ├── services/           # Business logic layer
│   │   ├── analysis_service.py     # NLP analysis logic
│   │   ├── whisper_service.py      # Real-time coaching logic
│   │   ├── advanced_analytics.py   # Analytics engine
│   │   ├── report_generator.py     # Report generation
│   │   ├── file_storage_service.py # File management
│   │   ├── vector_search.py        # [Phase 2.1] Vector search
│   │   └── knowledge_base.py       # [Phase 2.1] Knowledge management
│   ├── models/             # Data models
│   │   ├── project.py      # Project and analysis models
│   │   └── enhanced_models.py # Enhanced database models
│   ├── schemas/            # Request/response schemas
│   │   └── project_schema.py
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── components/    # Reusable UI components
│   │   │   └── charts/    # Professional chart components
│   │   └── pages/         # Application pages
│   │       ├── Analytics.jsx      # Analytics dashboard
│   │       └── KnowledgeBase.jsx  # [Phase 2.1] Knowledge management
│   └── package.json       # Node.js dependencies
├── chrome_extension/       # Browser extension
│   ├── manifest.json      # Extension configuration
│   ├── background.js      # Background service worker
│   └── content_script.js  # DOM interaction script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm/yarn
- **Chrome Browser** (for extension)
- **Git** for version control

### Backend Setup

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development server**:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**:

   ```bash
   npm start
   # or
   yarn start
   ```

   The application will be available at `http://localhost:3000`

### Chrome Extension Setup

1. **Open Chrome and navigate to**:

   ```
   chrome://extensions/
   ```

2. **Enable Developer mode** (toggle in top-right corner)

3. **Click "Load unpacked"** and select the `chrome_extension` directory

4. **Pin the extension** to your toolbar for easy access

5. **Configure the extension**:
   - Click the extension icon
   - Set your backend URL (default: `http://localhost:8000`)
   - Enable the extension for desired messaging platforms

## 📱 Usage

### Creating a New Project

1. **Open the Catalyst dashboard** at `http://localhost:3000`
2. **Click "New Project"** in the sidebar
3. **Fill in project details**:
   - Project name and description
   - Relationship type (romantic, family, friendship, professional)
   - Add participants
   - Set goals and preferences
4. **Review and create** the project

### Using the AI Whisper System

1. **Ensure the Chrome extension is installed and enabled**
2. **Open any supported messaging platform**:
   - WhatsApp Web
   - Facebook Messenger
   - Discord
   - Slack
   - Microsoft Teams
   - Telegram Web
3. **Start a conversation** - the extension will automatically:
   - Analyze message sentiment and tone
   - Provide real-time suggestions
   - Track communication patterns
   - Offer coaching tips

### Viewing Analytics

1. **Navigate to the Analytics page** in the dashboard
2. **View comprehensive insights**:
   - Communication quality trends
   - Sentiment analysis over time
   - Goal progress tracking
   - Relationship health metrics
   - Personalized recommendations

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database (if using external DB)
DATABASE_URL=sqlite:///./catalyst.db

# AI/NLP Services (optional)
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,chrome-extension://*

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration

Create a `.env` file in the frontend directory:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_WHISPER=true

# Development
REACT_APP_DEBUG=true
```

## 🧪 Development

### Running Tests

**Backend tests**:

```bash
cd backend
pytest tests/ -v
```

**Frontend tests**:

```bash
cd frontend
npm test
# or
yarn test
```

### Code Quality

**Backend linting**:

```bash
cd backend
flake8 .
black .
```

**Frontend linting**:

```bash
cd frontend
npm run lint
npm run format
```

### Building for Production

**Backend**:

```bash
cd backend
pip install -r requirements.txt
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Frontend**:

```bash
cd frontend
npm run build
# or
yarn build
```

**Chrome Extension**:

1. Zip the `chrome_extension` directory
2. Upload to Chrome Web Store Developer Dashboard

## 🔒 Privacy & Security

### Data Handling

- **Local Processing**: Most analysis happens locally in the browser
- **Minimal Data Transfer**: Only essential data is sent to the backend
- **No Message Storage**: Conversations are not permanently stored
- **Encrypted Communication**: All API calls use HTTPS
- **User Consent**: Clear opt-in for all features

### Security Features

- **CORS Protection**: Configured for specific origins
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: API endpoints are rate-limited
- **Secure Headers**: Security headers are implemented
- **Extension Permissions**: Minimal required permissions

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow existing code style and conventions
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Use meaningful commit messages

## 📋 API Documentation

### Core Endpoints

**Projects**:

- `GET /projects` - List all projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Analysis**:

- `POST /analysis/upload` - Upload conversation data
- `POST /analysis/analyze` - Analyze text content
- `WS /analysis/whisper` - Real-time whisper stream

**Health**:

- `GET /health` - Service health check

For detailed API documentation, visit `http://localhost:8000/docs` when the backend is running.

## 🐛 Troubleshooting

### Common Issues

**Backend won't start**:

- Check Python version (3.8+ required)
- Ensure virtual environment is activated
- Verify all dependencies are installed
- Check port 8000 is not in use

**Frontend won't start**:

- Check Node.js version (16+ required)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall
- Check port 3000 is not in use

**Extension not working**:

- Ensure extension is enabled in Chrome
- Check if you're on a supported platform
- Verify backend is running and accessible
- Check browser console for errors

**CORS errors**:

- Verify `ALLOWED_ORIGINS` in backend configuration
- Ensure frontend URL is included in CORS settings
- Check that both frontend and backend are running

### Getting Help

- Check the [Issues](https://github.com/your-repo/catalyst/issues) page
- Review the API documentation at `/docs`
- Check browser console for error messages
- Verify all services are running correctly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **React** for the powerful frontend library
- **Material-UI** for beautiful UI components
- **Chrome Extensions API** for browser integration
- **OpenAI** for AI/NLP capabilities
- **Recharts** for data visualization

## 🗺️ Roadmap

### Version 1.1

- [ ] Mobile app (React Native)
- [ ] Advanced NLP models
- [ ] Multi-language support
- [ ] Voice message analysis

### Version 1.2

- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] Integration with calendar apps
- [ ] Relationship coaching courses

### Version 2.0

- [ ] AI-powered relationship matching
- [ ] Video call analysis
- [ ] Predictive relationship insights
- [ ] Professional therapist integration

---

**Built with ❤️ for better relationships**
