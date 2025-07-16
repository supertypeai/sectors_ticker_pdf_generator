# Sectors Ticker PDF Generator

A Django REST API application for generating PDF reports focused on sector analysis and ticker-specific information.

## Features

- **Sector Analysis**: Generate comprehensive sector analysis reports
- **Ticker Analysis**: Create detailed ticker-specific reports 
- **PDF Generation**: Professional PDF reports with custom styling
- **REST API**: Easy-to-use REST endpoints for PDF generation
- **Authentication**: Secure token-based authentication
- **Template-based**: Modular design for easy customization

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Get authentication token

### PDF Generation
- `GET /api/generate-sector-pdf/` - Generate sector/ticker PDF report

#### Parameters:
- `title` (optional): Report title
- `email` (optional): Email for report customization
- `sector` (optional): Sector name for analysis
- `ticker` (optional): Ticker symbol for analysis

#### Example:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/generate-sector-pdf/?sector=Technology&ticker=AAPL&title=Tech%20Sector%20Analysis"
```

## Environment Variables

Create a `.env` file with:
```
JWT_SECRET=your_jwt_secret_key
PASSWORD=your_api_password
SUPABASE_URL=your_supabase_url (optional)
SUPABASE_KEY=your_supabase_key (optional)
```

## Project Structure

```
sectors_ticker_pdf_generator/
├── api/
│   ├── asset/
│   │   ├── font/          # Font files
│   │   └── cover.png      # Cover image template
│   ├── pdf_generator.py   # PDF generation logic
│   ├── views.py          # API views
│   ├── urls.py           # URL routing
│   └── models.py         # Data models
├── sectors_api/
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Customization

### PDF Templates
The PDF generation can be customized by modifying:
- `api/pdf_generator.py` - Main PDF generation logic
- `api/asset/` - Images, fonts, and other assets
- Color schemes and styling in the generator functions

### Adding New Sectors
To add new sector-specific analysis:
1. Modify `generate_sector_page()` in `pdf_generator.py`
2. Add sector-specific data sources
3. Customize analysis templates

### Adding New Data Sources
To integrate with external data APIs:
1. Add API configuration to `settings.py`
2. Implement data fetching in `pdf_generator.py`
3. Update the report generation logic

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request