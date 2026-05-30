import sys
sys.path.append('src')
from ics_generator import HolidayCalendarGenerator

from flask import Flask, render_template, send_file, request, jsonify, make_response
import os
import tempfile
from datetime import date

# Set template and static folders relative to this file's location
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

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
@app.route('/calendar/<country>/<int:year>')
def holiday_calendar(country, year=None):
    """Display holiday calendar for a country and year"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper())
        holidays_data = generator.get_holidays(year)
        
        # If no year specified, use current year
        display_year = year or date.today().year
        
        return render_template('calendar.html', 
                             country=country.upper(),
                             country_name=get_country_name(country.upper()),
                             year=display_year,
                             holidays=holidays_data,
                             today=date.today())
    except ValueError as e:
        return render_template('error.html', 
                             message=str(e), 
                             error_code=400), 400
    except Exception as e:
        return render_template('error.html', 
                             message="An unexpected error occurred", 
                             error_code=500), 500

@app.route('/download/<country>')
@app.route('/download/<country>/<int:year>')
def download_ics(country, year=None):
    """Download ICS file for holidays"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper())
        ics_data = generator.generate_ics(year)
        
        filename = f"{country.upper()}_holidays"
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
@app.route('/api/holidays/<country>/<int:year>')
def api_holidays(country, year=None):
    """API endpoint to get holiday data as JSON"""
    try:
        generator = HolidayCalendarGenerator(country=country.upper())
        holidays_data = generator.get_holidays(year)
        return jsonify({
            'country': country.upper(),
            'year': year or date.today().year,
            'holidays': holidays_data
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/holiday/<country>/<string:holiday_name>')
def holiday_detail(country, holiday_name):
    """Show detailed information about a specific holiday"""
    # For now, we'll show basic info - this can be expanded later
    try:
        generator = HolidayCalendarGenerator(country=country.upper())
        holidays_data = generator.get_holidays()
        
        # Find the specific holiday
        holiday_info = None
        for h in holidays_data:
            if h['name'].lower() == holiday_name.replace('-', ' ').lower():
                holiday_info = h
                break
        
        if not holiday_info:
            return render_template('error.html', 
                                 message="Holiday not found", 
                                 error_code=404), 404
                                 
        return render_template('holiday.html',
                             country=country.upper(),
                             country_name=get_country_name(country.upper()),
                             holiday=holiday_info)
    except ValueError as e:
        return render_template('error.html', 
                             message=str(e), 
                             error_code=400), 400
    except Exception as e:
        return render_template('error.html', 
                             message="An unexpected error occurred", 
                             error_code=500), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)