from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from io import BytesIO
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
from reportlab.lib.utils import ImageReader
import requests
import unicodedata

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_PATH = os.path.join(BASE_DIR, "asset")

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple for reportlab"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

def draw_name_tag(c, text, x, y, padding_x=10, padding_y=6, fill_color=colors.white, text_color=colors.HexColor("#F0748A"),
                  corner_radius=5, font_name="Inter-Bold", font_size=10):
    """
    Draws a name tag rectangle that automatically expands to fit the text.
    - x, y: bottom-left corner of the rectangle.
    """
    # Measure text width
    c.setFont(font_name, font_size)
    text_width = c.stringWidth(text, font_name, font_size)

    # Total width and height with padding
    rect_width = text_width + 2 * padding_x
    rect_height = font_size + 2 * padding_y

    # Draw rounded rectangle
    c.setLineWidth(2)
    c.setStrokeColor(fill_color)
    c.setFillColor(fill_color)
    c.roundRect(x, y, rect_width, rect_height, corner_radius, stroke=1, fill=1)

    # Draw text centered vertically and with horizontal padding
    c.setFillColor(text_color)
    text_x = x + padding_x
    text_y = y + padding_y + 1
    c.drawString(text_x, text_y, text)

def draw_shrinking_text(c, text, max_width, x, y, font_name='Inter-Bold', initial_font_size=20, min_font_size=5, color=colors.black):
    """Draw text that shrinks to fit within max_width"""
    font_size = initial_font_size
    c.setFillColor(color)
    
    while font_size >= min_font_size:
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(text, font_name, font_size)
        if text_width <= max_width:
            break
        font_size -= 1
    
    c.drawString(x, y, text)

def draw_justified_text(c, text, x, y, max_width, max_height, font_name="Inter", initial_font_size=14, min_font_size=8, line_spacing=2):
    """Draw justified text that fits within specified dimensions"""
    c.setFillColor(colors.black)
    font_size = initial_font_size
    
    while font_size >= min_font_size:
        c.setFont(font_name, font_size)
        
        words = text.split()
        line = ""
        lines = []

        # Split text into lines based on max_width
        for word in words:
            test_line = f"{line} {word}".strip()
            if c.stringWidth(test_line, font_name, font_size) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        line_height = font_size + line_spacing
        total_height = line_height * len(lines)

        # Check if total height fits within max_height
        if total_height <= max_height:
            break
        else:
            font_size -= 1  # Shrink font and try again

    # Draw lines with justification
    for i, line in enumerate(lines):
        line_words = line.split()

        if i == len(lines) - 1 or len(line_words) == 1:
            c.drawString(x, y, line)
        else:
            total_word_width = sum(c.stringWidth(word, font_name, font_size) for word in line_words)
            space_count = len(line_words) - 1
            if space_count > 0:
                extra_space = (max_width - total_word_width) / space_count
            else:
                extra_space = 0

            word_x = x
            for word in line_words:
                c.drawString(word_x, y, word)
                word_x += c.stringWidth(word, font_name, font_size) + extra_space

        y -= line_height

def cover_text_generator(pdf, height, sector, ticker, email_text, title_text):
    """Generate cover page text content"""
    pdf.setFont('Inter-Bold', 40)
    pdf.setFillColor(colors.white)
    pdf.drawString(64, height-582-33, "Sector")

    r, g, b = hex_to_rgb("#F0748A")
    pdf.setFillColorRGB(r, g, b)
    pdf.drawString(200, height-582-33, "Analysis")

    # Create name tags for sector and ticker
    x = 64
    y = height - 646 - 18
    
    tags = []
    if sector:
        tags.append(sector)
    if ticker:
        tags.append(ticker)
    
    # Add default analyst names
    tags.extend(['Market Analyst', 'Sector Specialist'])

    for tag in tags:
        draw_name_tag(
            pdf, tag, x, y,
            padding_x=10, padding_y=6,
            fill_color=colors.white,
            text_color=colors.HexColor("#91132A"),
            corner_radius=5,
            font_name="Inter", font_size=10
        )
        text_width = pdfmetrics.stringWidth(tag, "Inter", 10)
        x += text_width + 2 * 10 + 10  # tag width + spacing

    draw_shrinking_text(pdf, title_text, 400, 64, height-690-15, font_name='Inter-Bold', initial_font_size=20, min_font_size=5, color=colors.white)

    pdf.setFont('Inter', 20)
    pdf.setFillColor(colors.white)
    pdf.drawString(64, height-737-15, "For")

    # Email
    r, g, b = hex_to_rgb("#F0748A")
    pdf.setFillColorRGB(r, g, b)
    draw_shrinking_text(pdf, email_text, 400, 105, height-737-15, font_name='Inter-Bold', initial_font_size=18, min_font_size=10, color=colors.HexColor("#F0748A"))

def load_sectors_config():
    """Load sector configuration from JSON file"""
    try:
        config_path = os.path.join(ASSET_PATH, "sectors_config.json")
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def generate_sector_page(pdf, sector, height):
    """Generate sector analysis page with enhanced content"""
    config = load_sectors_config()
    sector_info = config.get("sectors", {}).get(sector, {})
    
    pdf.setFont('Inter-Bold', 24)
    pdf.setFillColor(colors.HexColor("#F0748A"))
    pdf.drawString(64, height-120, f"Sector Analysis: {sector}")
    
    # Get sector-specific information
    description = sector_info.get("description", f"Analysis of the {sector.lower()} sector")
    key_metrics = sector_info.get("key_metrics", ["Revenue Growth", "Market Share", "Profitability"])
    subcategories = sector_info.get("subcategories", [])
    risk_factors = sector_info.get("risk_factors", ["Market volatility", "Economic cycles"])
    
    # Build enhanced sector content
    sector_content = f"""
    {sector} Sector Overview
    
    {description}
    
    Key Performance Metrics:
    """
    
    for metric in key_metrics:
        sector_content += f"• {metric}\n    "
    
    if subcategories:
        sector_content += f"""
    
    Sector Subcategories:
    """
        for subcat in subcategories:
            sector_content += f"• {subcat}\n    "
    
    sector_content += f"""
    
    Risk Factors:
    """
    for risk in risk_factors:
        sector_content += f"• {risk}\n    "
    
    sector_content += f"""
    
    Analysis Framework:
    This sector analysis employs a comprehensive approach examining fundamental metrics, 
    technical indicators, and ESG (Environmental, Social, Governance) factors. The analysis 
    considers both quantitative data and qualitative factors that may impact sector performance.
    
    Market Position:
    The {sector.lower()} sector's position within the broader market context is evaluated 
    through comparative analysis with other sectors, historical performance trends, and 
    forward-looking indicators.
    """
    
    # Draw sector content
    draw_justified_text(pdf, sector_content, 64, height-180, 464, 500, 
                       font_name="Inter", initial_font_size=12, min_font_size=8, line_spacing=3)

def generate_ticker_page(pdf, ticker, height):
    """Generate ticker analysis page"""
    pdf.setFont('Inter-Bold', 24)
    pdf.setFillColor(colors.HexColor("#F0748A"))
    pdf.drawString(64, height-120, f"Ticker Analysis: {ticker}")
    
    # Mock ticker data (in real implementation, this would come from API)
    ticker_content = f"""
    {ticker} - Company Analysis
    
    Ticker Symbol: {ticker}
    Exchange: [Exchange Name]
    Market Cap: [Market Capitalization]
    Industry: [Industry Classification]
    Listing Date: [IPO Date]
    
    Company Overview:
    This analysis covers the fundamental and technical aspects of {ticker}, including 
    financial performance, business model, competitive positioning, and investment outlook.
    
    Key Financial Metrics:
    • Revenue Growth: [YoY Growth %]
    • Profit Margins: [Operating/Net Margins]
    • Return on Equity: [ROE %]
    • Debt-to-Equity Ratio: [D/E Ratio]
    • Price-to-Earnings Ratio: [P/E Ratio]
    
    Business Highlights:
    • Core business operations and revenue streams
    • Recent corporate developments and strategic initiatives
    • Market position and competitive advantages
    • Risk factors and investment considerations
    
    Technical Analysis:
    • Price performance and trading patterns
    • Support and resistance levels
    • Volume analysis and liquidity metrics
    • Moving averages and momentum indicators
    """
    
    # Draw ticker content
    draw_justified_text(pdf, ticker_content, 64, height-180, 464, 500, 
                       font_name="Inter", initial_font_size=12, min_font_size=8, line_spacing=3)

def generate_sector_pdf(title_text, email_text, sector, ticker):
    """Main function to generate sector ticker PDF"""
    buffer = BytesIO()
    width, height = 595, 842

    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('Inter', os.path.join(ASSET_PATH, "font/Inter-Regular.ttf")))
        pdfmetrics.registerFont(TTFont('Inter-Bold', os.path.join(ASSET_PATH, "font/Inter-Bold.ttf")))
    except:
        # Fallback to default fonts if custom fonts are not available
        pass

    pdf = canvas.Canvas(buffer, pagesize=(width, height))

    # Cover Page
    try:
        pdf.drawImage(os.path.join(ASSET_PATH, 'cover.png'), 0, 0, width, height)
    except:
        # If cover image not available, create a simple colored background
        pdf.setFillColor(colors.HexColor("#1A365D"))
        pdf.rect(0, 0, width, height, fill=1)
    
    cover_text_generator(pdf, height, sector, ticker, email_text, title_text)
    pdf.showPage()

    # Sector Analysis Page
    if sector:
        # Create sector page background
        pdf.setFillColor(colors.HexColor("#F7FAFC"))
        pdf.rect(0, 0, width, height, fill=1)
        generate_sector_page(pdf, sector, height)
        pdf.showPage()

    # Ticker Analysis Page
    if ticker:
        # Create ticker page background
        pdf.setFillColor(colors.HexColor("#F7FAFC"))
        pdf.rect(0, 0, width, height, fill=1)
        generate_ticker_page(pdf, ticker, height)
        pdf.showPage()

    # Methodology Page
    pdf.setFillColor(colors.HexColor("#F7FAFC"))
    pdf.rect(0, 0, width, height, fill=1)
    
    pdf.setFont('Inter-Bold', 24)
    pdf.setFillColor(colors.HexColor("#F0748A"))
    pdf.drawString(64, height-120, "Analysis Methodology")
    
    methodology_content = """
    Research Methodology and Disclaimers
    
    This sector and ticker analysis report is generated using a combination of quantitative 
    and qualitative research methodologies, including:
    
    Data Sources:
    • Financial statements and regulatory filings
    • Market data and trading information
    • Industry research and analyst reports
    • Company announcements and press releases
    
    Analytical Framework:
    • Fundamental analysis of financial metrics
    • Technical analysis of price movements
    • Sector comparison and peer analysis
    • Macroeconomic factor assessment
    
    Important Disclaimers:
    
    This report is for informational purposes only and should not be construed as 
    investment advice. Past performance does not guarantee future results. All 
    investments carry risk of loss, and there is no guarantee that any investment 
    strategy will be successful.
    
    The information contained in this report is believed to be accurate at the time 
    of publication but may become outdated. Readers should conduct their own research 
    and consult with qualified financial advisors before making investment decisions.
    
    This analysis is generated using automated systems and may contain errors or 
    omissions. The authors disclaim any liability for decisions made based on this report.
    """
    
    draw_justified_text(pdf, methodology_content, 64, height-180, 464, 500, 
                       font_name="Inter", initial_font_size=11, min_font_size=8, line_spacing=3)
    
    pdf.showPage()

    pdf.save()
    buffer.seek(0)
    return buffer

def contains_non_ascii(text):
    """Check if text contains non-ASCII characters"""
    for char in text:
        code = ord(char)
        if (0x4E00 <= code <= 0x9FFF) or \
            (0xAC00 <= code <= 0xD7A3) or \
            (0x3040 <= code <= 0x309F) or \
            (0x30A0 <= code <= 0x30FF):
            return True
        category = unicodedata.category(char)
        if category.startswith('C'):
            return True
    return False
