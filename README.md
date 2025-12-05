# GeoMonitor - Geospatial Pipeline Monitoring System

A comprehensive full-stack geospatial application for pipeline monitoring with satellite imagery analysis.

## Features

- **User Authentication**: Email-based login with JWT tokens using Djoser
- **Organization Management**: One-to-one relationship with users for multi-tenant support
- **Pipeline Route Management**: Upload and visualize GeoJSON pipeline routes
- **Satellite Image Analysis**: 
  - NDVI-based leak detection
  - Change detection using image differencing
  - Encroachment detection using YOLO object detection
  - Emissions tracking using anomaly detection
  - Facility monitoring using U-Net segmentation
- **Real-time Updates**: WebSocket support for live notifications
- **Alert Management**: Critical alert sound notifications
- **Dark/Light Mode**: Full theme support
- **Responsive Design**: Works on desktop and mobile

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- Djoser for authentication
- PostgreSQL with PostGIS
- Redis for caching and Celery broker
- Channels for WebSocket support
- GDAL/Rasterio for geospatial processing
- Ultralytics YOLO for object detection
- Segmentation Models PyTorch for U-Net

### Frontend
- React 19 with TypeScript
- Vite 7
- Tailwind CSS 4 (latest without tailwind.config.js)
- ShadCN UI components
- Redux Toolkit with Redux Persist
- React Router 6
- React Hook Form with Zod validation
- Leaflet for map visualization
- Framer Motion for animations

## Project Structure

```
flsf/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   │   ├── ui/           # ShadCN UI components
│   │   │   ├── common/       # Shared components
│   │   │   ├── layouts/      # Layout components
│   │   │   ├── dashboard/    # Dashboard components
│   │   │   ├── map/          # Map components
│   │   │   ├── analysis/     # Analysis components
│   │   │   └── auth/         # Auth components
│   │   ├── pages/            # Page components
│   │   ├── store/            # Redux store and slices
│   │   ├── services/         # API services
│   │   ├── hooks/            # Custom hooks
│   │   ├── types/            # TypeScript types
│   │   └── lib/              # Utility functions
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── nginx.conf
│
├── server/                    # Django backend
│   ├── core/                  # Main project
│   │   ├── settings/         # Split settings
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── celery.py
│   ├── user/                  # User app
│   ├── pipeline/              # Pipeline app
│   ├── analysis/              # Analysis app
│   │   └── processors/       # Image processors
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL with PostGIS
- Redis
- GDAL (for geospatial processing)

### Development Setup

#### Backend

```bash
cd server

# Create virtual environment
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Frontend

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Development

```bash
cd server
docker-compose -f docker-compose.dev.yml up -d
```

### Production Deployment

```bash
cd server
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Backend

```env
DJANGO_SECRET_KEY=your-secret-key
DB_NAME=geospatial_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Frontend

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/users/` - Register
- `POST /api/v1/auth/jwt/create/` - Login
- `POST /api/v1/auth/jwt/refresh/` - Refresh token
- `GET /api/v1/auth/users/me/` - Get current user

### Pipeline
- `GET /api/v1/pipeline/routes/` - List pipeline routes
- `GET /api/v1/pipeline/routes/all-geojson/` - Get all routes as GeoJSON
- `GET /api/v1/pipeline/images/` - List satellite images
- `GET /api/v1/pipeline/alerts/` - List alerts

### Analysis
- `GET /api/v1/analysis/results/` - List analysis results
- `POST /api/v1/analysis/results/run/` - Run analysis on image
- `GET /api/v1/analysis/results/summary/` - Get analysis summary

## Admin Panel

Access the Django admin at `http://localhost:8000/admin/` to:
- Upload GeoJSON pipeline routes
- Upload TIFF satellite images
- Run image analysis
- View and manage alerts

## License

MIT

