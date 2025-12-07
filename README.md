# AutoList AI

> Intelligent product data mapping for e-commerce marketplaces

AutoList AI automates the tedious process of mapping Shopify product data to marketplace templates (Amazon, Flipkart, etc.). It uses rule-based mapping combined with AI-assisted extraction to achieve high auto-fill rates.

## Features

- **Shopify Integration** - Connect your store and sync products
- **Smart Mapping** - Rule-based + AI-powered field mapping
- **Template Schemas** - Support for multiple marketplace templates
- **Confidence Scoring** - Visual indicators for mapping accuracy
- **Inline Editing** - Review and correct mappings before export
- **XLSX Export** - Generate marketplace-ready templates

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd AUTOLIST_AI_NEW_MVP

# Run setup script
chmod +x setup.sh
./setup.sh

# Start services (3 terminals)
# Terminal 1: MongoDB
mongod

# Terminal 2: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend && npm run dev
```

Open http://localhost:5173 and login with the demo account.

## Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation instructions
- [API Docs](http://localhost:8000/docs) - Swagger UI (when running)
- [Integration Tests](backend/tests/INTEGRATION_CHECKLIST.md) - Test checklist

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| Database | MongoDB |
| AI | Claude (Anthropic) |
| Auth | JWT (PyJWT) |

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── services/  # Business logic
│   │   ├── workers/   # Background jobs
│   │   └── models/    # Data models
│   └── tests/         # Unit tests
│
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/# Reusable components
│   │   └── services/  # API clients
│
└── docker-compose.yml # Docker setup
```

## Phase 1 Acceptance Criteria

- [x] Connect Shopify store and sync 10+ products
- [x] Two template schemas (shirt, kurta) ingested
- [x] 80% of products have 70% auto-fill rate
- [x] Mapping preview with confidence badges
- [x] XLSX export with proper column alignment

## License

MIT
