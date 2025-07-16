# Deployment Guide

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Quick Start

1. **Clone or setup the project:**
   ```bash
   cd sectors_ticker_pdf_generator
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database:**
   ```bash
   python manage.py migrate
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Test the setup:**
   ```bash
   python test_generator.py
   ```

## Environment Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

# JWT Authentication
JWT_SECRET=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXP_DELTA_SECONDS=3600

# API Authentication
PASSWORD=your-secure-api-password

# Optional: External APIs
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Security Notes

- Use strong, unique passwords for `SECRET_KEY` and `PASSWORD`
- Keep `JWT_SECRET` secure and unique
- In production, set `DEBUG=False`
- Configure `ALLOWED_HOSTS` appropriately for your domain

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Create a Gunicorn configuration file:**
   ```python
   # gunicorn_config.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "sync"
   timeout = 120
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn sectors_api.wsgi:application -c gunicorn_config.py
   ```

### Using Docker

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   RUN python manage.py collectstatic --noinput

   EXPOSE 8000

   CMD ["gunicorn", "sectors_api.wsgi:application", "--bind", "0.0.0.0:8000"]
   ```

2. **Build and run:**
   ```bash
   docker build -t sectors-ticker-pdf .
   docker run -p 8000:8000 --env-file .env sectors-ticker-pdf
   ```

### Nginx Configuration

For production, use Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/static/files/;
    }
}
```

## Cloud Deployment Options

### Railway

1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

### Heroku

1. **Create requirements.txt with gunicorn:**
   ```
   # Add to your requirements.txt
   gunicorn==20.1.0
   ```

2. **Create Procfile:**
   ```
   web: gunicorn sectors_api.wsgi --log-file -
   ```

3. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key
   # Set other environment variables
   git push heroku main
   ```

### DigitalOcean App Platform

1. Connect repository
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn sectors_api.wsgi:application`

## Database Options

### SQLite (Default)
- Good for development and small deployments
- No additional setup required

### PostgreSQL (Recommended for Production)

1. **Install psycopg2:**
   ```bash
   pip install psycopg2-binary
   ```

2. **Update settings.py:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('DB_NAME'),
           'USER': os.environ.get('DB_USER'),
           'PASSWORD': os.environ.get('DB_PASSWORD'),
           'HOST': os.environ.get('DB_HOST', 'localhost'),
           'PORT': os.environ.get('DB_PORT', '5432'),
       }
   }
   ```

## Monitoring and Logging

### Basic Logging Configuration

Add to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'sectors_api.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Check

The API includes a health check endpoint:
- `GET /api/health/` - Returns service status

## Performance Optimization

### PDF Generation Optimization

1. **Font Caching:** Fonts are registered once at startup
2. **Image Optimization:** Use optimized images in `api/asset/`
3. **Memory Management:** PDF buffers are properly cleaned up

### API Rate Limiting

Configured in `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'user': '50/minute',
        'anon': '50/minute',
    },
}
```

## Troubleshooting

### Common Issues

1. **Font not found errors:**
   - Ensure fonts are in `api/asset/font/`
   - Check file permissions

2. **PDF generation fails:**
   - Verify ReportLab installation
   - Check available memory

3. **Authentication errors:**
   - Verify JWT_SECRET is set
   - Check password configuration

### Debug Mode

Enable debug logging:
```python
# In settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## Backup and Maintenance

### Database Backup

For SQLite:
```bash
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

For PostgreSQL:
```bash
pg_dump your_database > backup_$(date +%Y%m%d).sql
```

### Log Rotation

Set up log rotation to prevent disk space issues:
```bash
# Add to crontab
0 0 * * * find /path/to/logs -name "*.log" -mtime +30 -delete
```

## Security Checklist

- [ ] Set strong SECRET_KEY
- [ ] Configure secure PASSWORD
- [ ] Set DEBUG=False in production
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Use HTTPS in production
- [ ] Keep dependencies updated
- [ ] Monitor for security vulnerabilities
- [ ] Set up proper firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable access logging
