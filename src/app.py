import sys
import json
sys.path.append('src')
from ics_generator import HolidayCalendarGenerator

from flask import Flask, render_template, send_file, request, jsonify, make_response
import os
import tempfile
from datetime import date

# Load holiday info once at startup
HOLIDAY_INFO_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'holiday_info.json')
with open(HOLIDAY_INFO_PATH, 'r') as f:
    HOLIDAY_INFO = json.load(f)

# Set template and static folders relative to this file's location
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

def get_subdivision_info(country_code):
    """Get subdivision list and name mapping for a country"""
    subdivisions = []
    subdivision_name_map = {}
    try:
        temp_gen = HolidayCalendarGenerator(country=country_code.upper())
        if hasattr(temp_gen.holiday_lib, 'subdivisions'):
            subdivisions = list(temp_gen.holiday_lib.subdivisions)
            subdivision_name_map = getattr(temp_gen.holiday_lib, 'subdivisions_aliases', {})
    except:
        pass  # Some countries might not support subdivisions
    return subdivisions, subdivision_name_map

def get_country_name(code):
    """Convert country code to full name (basic mapping)"""
    country_names = {
        'US': 'United States',
        'UK': 'United Kingdom',
        'CA': 'Canada',
        'AU': 'Australia',
        'DE': 'Germany',
        'FR': 'France',
        'JP': 'Japan',
        'IN': 'India',
        'MX': 'Mexico',
        'BR': 'Brazil'
    }
    return country_names.get(code.upper(), code.upper())

@app.route('/')
def index():
    """Homepage with country selector"""
    # Get some popular countries for quick access
    popular_countries = [
        {'code': 'US', 'name': 'United States'},
        {'code': 'UK', 'name': 'United Kingdom'}, 
        {'code': 'CA', 'name': 'Canada'},
        {'code': 'AU', 'name': 'Australia'},
        {'code': 'DE', 'name': 'Germany'},
        {'code': 'FR', 'name': 'France'},
        {'code': 'JP', 'name': 'Japan'},
        {'code': 'IN', 'name': 'India'},
        {'code': 'MX', 'name': 'Mexico'},
        {'code': 'BR', 'name': 'Brazil'}
    ]
    
    return render_template('index.html', popular_countries=popular_countries, current_year=date.today().year)

@app.route('/calendar/<country>')
@app.route('/calendar/<country>/<string:subdiv>')
@app.route('/calendar/<country>/<string:subdiv>/<int:year>')
@app.route('/calendar/<country>/<int:year>')
def holiday_calendar(country, subdiv=None, year=None):
    """Display holiday calendar for a country and year"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper(), subdiv=subdiv.upper() if subdiv else None)
        holidays_data = generator.get_holidays(year)
        
        # If no year specified, use current year
        display_year = year or date.today().year
        
        # Get subdivisions for this country if available
        subdivisions, subdivision_name_map = get_subdivision_info(country)
        
        return render_template('calendar.html', 
                             country=country.upper(),
                             subdiv=subdiv.upper() if subdiv else None,
                             country_name=get_country_name(country.upper()),
                             subdivision_name=subdivision_name_map.get(subdiv.upper(), subdiv.upper()) if subdiv else None,
                             year=display_year,
                             holidays=holidays_data,
                             today=date.today(),
                             subdivisions=subdivisions,
                             subdivision_name_map=subdivision_name_map)
    except ValueError as e:
        return render_template('error.html', 
                             message=str(e), 
                             error_code=400), 400
    except Exception as e:
        return render_template('error.html', 
                             message="An unexpected error occurred", 
                             error_code=500), 500

@app.route('/download/<country>')
@app.route('/download/<country>/<string:subdiv>')
@app.route('/download/<country>/<string:subdiv>/<int:year>')
@app.route('/download/<country>/<int:year>')
def download_ics(country, subdiv=None, year=None):
    """Download ICS file for holidays"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper(), subdiv=subdiv.upper() if subdiv else None)
        ics_data = generator.generate_ics(year)
        
        filename = f"{country.upper()}_holidays"
        if subdiv:
            filename += f"_{subdiv.upper()}"
        if year:
            filename += f"_{year}"
        filename += ".ics"
        
        response = make_response(ics_data)
        response.headers['Content-Type'] = 'text/calendar'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/holidays/<country>')
@app.route('/api/holidays/<country>/<string:subdiv>')
@app.route('/api/holidays/<country>/<string:subdiv>/<int:year>')
@app.route('/api/holidays/<country>/<int:year>')
def api_holidays(country, subdiv=None, year=None):
    """API endpoint to get holiday data as JSON"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper(), subdiv=subdiv.upper() if subdiv else None)
        holidays_data = generator.get_holidays(year)
        return jsonify({
            'country': country.upper(),
            'subdiv': subdiv.upper() if subdiv else None,
            'year': year or date.today().year,
            'holidays': holidays_data
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/holiday/<country>/<string:holiday_name>')
@app.route('/holiday/<country>/<string:subdiv>/<string:holiday_name>')
def holiday_detail(country, holiday_name, subdiv=None):
    """Show detailed information about a specific holiday"""
    country_key = country.upper()
    subdiv_key = subdiv.upper() if subdiv else None
    # Normalize the holiday name for matching: replace hyphens with spaces
    normalized_name = holiday_name.replace('-', ' ').strip()
    try:
        generator = HolidayCalendarGenerator(country=country_key, subdiv=subdiv_key)
        holidays_data = generator.get_holidays()
        
        # Find the specific holiday (case-insensitive match)
        holiday_info = None
        for h in holidays_data:
            if h['name'].lower() == normalized_name.lower():
                holiday_info = h
                break
        
        if not holiday_info:
            return render_template('error.html', 
                                 message="Holiday not found", 
                                 error_code=404), 404
                                 
        # Get detailed info from our JSON
        details = HOLIDAY_INFO.get(country_key, {}).get(holiday_info['name'], {
            'description': 'Information not available.',
            'traditions': [],
            'observance': 'Unknown',
            'source': 'No source information available.'
        })
        
        # Get subdivision info for display
        _, subdivision_name_map = get_subdivision_info(country_key)
                                 
        return render_template('holiday.html',
                             country=country_key,
                             subdiv=subdiv_key,
                             country_name=get_country_name(country_key),
                             subdivision_name=subdivision_name_map.get(subdiv_key, subdiv_key) if subdiv_key else None,
                             holiday=holiday_info,
                             details=details)
    except ValueError as e:
        return render_template('error.html', 
                             message=str(e), 
                             error_code=400), 400
    except Exception as e:
        return render_template('error.html', 
                             message="An unexpected error occurred", 
                             error_code=500), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)