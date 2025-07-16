# API Documentation

## Overview

The Sectors Ticker PDF Generator API provides endpoints for generating comprehensive PDF reports focused on sector analysis and individual ticker analysis. The API is built using Django REST Framework and supports secure token-based authentication.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses token-based authentication. You need to obtain a token first and include it in subsequent requests.

### Get Authentication Token

**Endpoint:** `POST /api/token/`

**Request Body:**
```json
{
    "email": "user@supertype.ai",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Requirements:**
- Email must end with `@supertype.ai`
- Password must match the configured API password

## PDF Generation

### Generate Sector/Ticker PDF Report

**Endpoint:** `GET /api/generate-sector-pdf/`

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `title` | string | No | "Sector Ticker Analysis Report" | Custom title for the report |
| `email` | string | No | "human@supertype.ai" | Email to include in the report |
| `sector` | string | No | "" | Sector name for analysis (e.g., "Technology", "Healthcare") |
| `ticker` | string | No | "" | Ticker symbol for analysis (e.g., "AAPL", "MSFT") |

**Example Requests:**

1. **Sector Analysis Only:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/generate-sector-pdf/?sector=Technology&title=Tech%20Sector%20Analysis"
```

2. **Ticker Analysis Only:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/generate-sector-pdf/?ticker=AAPL&title=Apple%20Stock%20Analysis"
```

3. **Combined Sector and Ticker Analysis:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/generate-sector-pdf/?sector=Technology&ticker=AAPL&title=Apple%20in%20Tech%20Sector"
```

4. **Custom Email and Title:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/generate-sector-pdf/?sector=Healthcare&email=analyst@company.com&title=Healthcare%20Investment%20Analysis"
```

**Response:**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="[title].pdf"`
- **Body:** PDF file content

**Error Responses:**

```json
{
    "detail": "Invalid credentials"
}
```

## Supported Sectors

The API supports analysis for the following sectors:

- **Technology**: Software, Hardware, Semiconductors, IT Services, Cloud Computing
- **Healthcare**: Pharmaceuticals, Biotechnology, Medical Devices, Healthcare Services
- **Financial**: Banks, Insurance, Investment Services, Real Estate, Fintech
- **Energy**: Oil & Gas, Renewable Energy, Utilities, Pipeline Companies
- **Consumer Discretionary**: Retail, Automotive, Hotels & Restaurants, Media & Entertainment
- **Consumer Staples**: Food & Beverages, Personal Care, Household Products, Tobacco
- **Industrials**: Aerospace & Defense, Construction, Transportation, Industrial Machinery
- **Materials**: Chemicals, Metals & Mining, Paper & Packaging, Construction Materials
- **Utilities**: Electric Utilities, Gas Utilities, Water Utilities, Renewable Energy
- **Real Estate**: REITs, Real Estate Development, Real Estate Services
- **Communication Services**: Telecommunications, Media & Entertainment, Interactive Media

## PDF Report Structure

The generated PDF reports include:

1. **Cover Page**: Title, sector/ticker tags, email customization
2. **Sector Analysis Page** (if sector provided): 
   - Sector overview and description
   - Key performance metrics
   - Subcategories
   - Risk factors
   - Market position analysis
3. **Ticker Analysis Page** (if ticker provided):
   - Company overview
   - Financial metrics
   - Business highlights
   - Technical analysis
4. **Methodology Page**: Research methodology and disclaimers

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful PDF generation
- `400 Bad Request`: Missing required parameters
- `401 Unauthorized`: Invalid or missing authentication
- `500 Internal Server Error`: Server-side error during PDF generation

### Error Response Format

```json
{
    "detail": "Error description"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authenticated users**: 50 requests per minute
- **Anonymous users**: 50 requests per minute

## Environment Variables

Required environment variables:

```env
JWT_SECRET=your_jwt_secret_key
PASSWORD=your_api_password
SUPABASE_URL=your_supabase_url (optional)
SUPABASE_KEY=your_supabase_key (optional)
```

## Python SDK Example

```python
import requests

# Get authentication token
auth_response = requests.post('http://localhost:8000/api/token/', json={
    'email': 'user@supertype.ai',
    'password': 'your_password'
})
token = auth_response.json()['token']

# Generate PDF report
headers = {'Authorization': f'Bearer {token}'}
params = {
    'sector': 'Technology',
    'ticker': 'AAPL',
    'title': 'Apple Technology Analysis',
    'email': 'analyst@company.com'
}

response = requests.get(
    'http://localhost:8000/api/generate-sector-pdf/',
    headers=headers,
    params=params
)

# Save PDF to file
with open('report.pdf', 'wb') as f:
    f.write(response.content)
```

## JavaScript/Node.js Example

```javascript
const axios = require('axios');
const fs = require('fs');

async function generateReport() {
    // Get authentication token
    const authResponse = await axios.post('http://localhost:8000/api/token/', {
        email: 'user@supertype.ai',
        password: 'your_password'
    });
    
    const token = authResponse.data.token;
    
    // Generate PDF report
    const response = await axios.get('http://localhost:8000/api/generate-sector-pdf/', {
        headers: { 'Authorization': `Bearer ${token}` },
        params: {
            sector: 'Technology',
            ticker: 'AAPL',
            title: 'Apple Technology Analysis'
        },
        responseType: 'arraybuffer'
    });
    
    // Save PDF to file
    fs.writeFileSync('report.pdf', response.data);
}
```

## Customization

### Adding New Sectors

To add support for new sectors:

1. Update `api/asset/sectors_config.json` with new sector information
2. Restart the application

### Custom Styling

To customize PDF styling:

1. Modify color schemes in `sectors_config.json`
2. Update fonts in `api/asset/font/` directory
3. Replace cover image at `api/asset/cover.png`

### Data Integration

To integrate with external data sources:

1. Add API credentials to environment variables
2. Implement data fetching in `api/pdf_generator.py`
3. Update analysis functions with real-time data

## Support

For support and questions:
- Check the README.md file for setup instructions
- Run the test suite: `python test_generator.py`
- Review server logs for error details
