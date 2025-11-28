# Energy App - Railway Deployment Guide

This guide will help you deploy the Energy App to Railway, including the PostgreSQL database with 2024-2025 m_lecturas data.

## 🚀 Quick Start

### Prerequisites
- Railway account (https://railway.app)
- GitHub account with this repository
- Google Gemini API key (for AI analysis features)

### Deployment Steps

1. **Connect Repository to Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your EnergyApp repository

2. **Add PostgreSQL Database**
   - In your Railway project, click "New"
   - Select "PostgreSQL"
   - Railway will automatically create a PostgreSQL database
   - Note the connection details (will be available as environment variables)

3. **Configure Environment Variables**
   - In your Railway project, go to "Variables" tab
   - Add the following environment variables:

   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=your_gemini_api_key_here
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-frontend-domain.railway.app
   ```

   - The `DATABASE_URL` will be automatically provided by Railway when you add PostgreSQL
   - Replace `your_gemini_api_key_here` with your actual Google Gemini API key
   - For `CORS_ORIGINS`, use your frontend domain once deployed

4. **Deploy the Application**
   - Railway will automatically deploy when you push to your connected repository
   - Monitor the deployment in the Railway dashboard

## 📁 Project Structure

```
EnergyApp/
├── railway.toml              # Railway configuration
├── backend/
│   ├── start.py             # Backend startup script
│   ├── database_seeder.py   # Database seeding script
│   ├── requirements.txt     # Python dependencies
│   └── app/                 # FastAPI application
└── frontend/
    ├── package.json         # Frontend dependencies
    ├── vite.config.ts       # Vite configuration
    ├── .env.production      # Production environment variables
    └── src/                 # React application
```

## 🔧 Configuration Details

### Backend Service
- **Port**: 8000
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Health Check**: `/health` endpoint
- **Auto-start**: Database initialization and seeding on first run

### Frontend Service  
- **Port**: 5173
- **Framework**: React + TypeScript + Vite
- **Build**: Production-optimized build
- **API Base URL**: Configurable via `VITE_API_BASE_URL` environment variable

### Database Schema
The application uses the following main tables:
- `departamentos` - Department information
- `municipios` - Municipality information  
- `localidades` - Location information
- `medidor` - Meter devices
- `m_lecturas` - Energy readings (2024-2025 data)

## 📊 Database Seeding

The application automatically seeds the database with:

### Sample Data Included:
- **4 Departments**: Antioquia, Bogotá D.C., Valle del Cauca, Atlántico
- **7 Municipalities**: Medellín, Envigado, Itagüí, Bogotá, Cali, Palmira, Barranquilla
- **5 Localities**: El Poblado, Laureles, Centro, Chapinero, Usaquén, San Fernando
- **4 Smart Meters**: MED001, MED002, MED003, MED004

### m_lecturas Data (2024-2025):
- **Time Period**: January 1, 2024 to December 31, 2025
- **Frequency**: Readings every 15 minutes
- **Total Records**: ~280,000 sample readings
- **Realistic Patterns**: 
  - Time-of-day variations (peak/off-peak)
  - Weekday/weekend differences
  - Device-type specific consumption patterns

## 🛠️ Manual Deployment Commands

If you need to deploy manually or troubleshoot:

### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python database_seeder.py  # Seed initial data
python start.py           # Start server
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run build
npm run start
```

## 🔍 Health Checks

### Backend Health:
```bash
curl https://your-backend-domain.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Energy N-Tier System",
  "version": "1.0.0",
  "environment": "production"
}
```

### Database Connection:
The backend automatically checks database connectivity on startup and will retry if the database isn't immediately available.

## 🚨 Troubleshooting

### Common Issues:

1. **Database Connection Failures**
   - Check that PostgreSQL service is running in Railway
   - Verify `DATABASE_URL` environment variable is set correctly
   - Check Railway logs for connection errors

2. **CORS Errors**
   - Ensure `CORS_ORIGINS` includes your frontend domain
   - Check that frontend is using the correct API base URL

3. **Build Failures**
   - Check that all dependencies are in requirements.txt and package.json
   - Verify Node.js and Python versions are compatible

4. **Missing Data**
   - Check Railway logs for database seeding output
   - Verify the database_seeder.py ran successfully

### Checking Logs:
- In Railway dashboard, go to your service
- Click "Logs" tab to see real-time application logs
- Look for database connection messages and seeding progress

## 📈 Monitoring

### Railway Dashboard:
- **Deployments**: View deployment history and status
- **Metrics**: Monitor CPU, memory, and network usage
- **Logs**: Real-time application logs
- **Variables**: Manage environment variables

### Application Monitoring:
- Backend health endpoint: `/health`
- Database connection status in logs
- API request logs for troubleshooting

## 🔄 Updates and Maintenance

### Adding New Data:
1. Update the `database_seeder.py` script
2. Push changes to GitHub
3. Railway will automatically redeploy
4. The seeder will only run if no data exists

### Environment Variables:
- Update in Railway dashboard → Variables
- Changes take effect on next deployment

### Scaling:
- In Railway, adjust service resources as needed
- PostgreSQL can be scaled independently

## 📞 Support

For deployment issues:
1. Check Railway documentation: https://docs.railway.app
2. Review application logs in Railway dashboard
3. Verify environment variables are set correctly
4. Ensure all dependencies are properly specified

For application issues:
1. Check the backend health endpoint
2. Review database connectivity
3. Verify API endpoints are accessible