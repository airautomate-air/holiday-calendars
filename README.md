# Holiday Calendars

A web application for generating, viewing, and subscribing to holiday calendars for any country. Built with Flask and the `holidays` library.

## Features

- 📅 Generate and download ICS calendar files for any country/region
- 🌍 Support for dozens of countries and their subdivisions (states, provinces, etc.)
- 📋 Detailed holiday information including descriptions, traditions, and observance types
- 🔍 Subdivision filtering (e.g., view holidays for California vs. Texas)
- 📱 Responsive design that works on mobile and desktop
- 🔌 JSON API for developers to access holiday data
- ⏰ Countdown timers showing time until upcoming holidays
- 🎯 "Today's holiday" highlighting
- 🖨️ Print-friendly views

## Live Demo

Visit the live site: https://airautomate-air.github.io/holiday-calendars/

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/airautomate-air/holiday-calendars.git
cd holiday-calendars

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py
```

The application will be available at http://localhost:5000

## Usage

### Web Interface

1. Visit the homepage and enter a country code (e.g., `US`, `UK`, `CA`) or select from popular countries
2. Optionally select a subdivision (state/province) if available for that country
3. View the holiday calendar for the current year or specify a different year
4. Click on any holiday to see detailed information about it
5. Download the ICS file to subscribe to the calendar in your preferred calendar app (Google Calendar, Apple Calendar, Outlook, etc.)

### API Endpoints

- `GET /api/holidays/<country>` - Get holidays for current year
- `GET /api/holidays/<country>/<int:year>` - Get holidays for specific year
- `GET /api/holidays/<country>/<string:subdiv>` - Get holidays for subdivision, current year
- `GET /api/holidays/<country>/<string:subdiv>/<int:year>` - Get holidays for subdivision and year

Returns JSON with country, year, and list of holidays.

### ICS Download

- `GET /download/<country>` - Download ICS for current year
- `GET /download/<country>/<int:year>` - Download ICS for specific year
- `GET /download/<country>/<string:subdiv>` - Download ICS for subdivision, current year
- `GET /download/<country>/<string:subdiv>/<int:year>` - Download ICS for subdivision and year

## Supported Countries

The application supports all countries available in the `holidays` library. Popular examples include:

- US (United States) - with state subdivisions
- UK (United Kingdom) 
- CA (Canada) - with province subdivisions
- AU (Australia)
- DE (Germany)
- FR (France)
- JP (Japan)
- IN (India)
- MX (Mexico)
- BR (Brazil)

## Development

### Project Structure

```
holiday-calendars/
├── src/
│   ├── app.py              # Main Flask application
│   └── ics_generator.py    # ICS generation and holiday data logic
├── templates/              # HTML templates
│   ├── index.html          # Homepage
│   ├── calendar.html       # Holiday calendar view
│   ├── holiday.html        # Holiday detail page
│   └── error.html          # Error pages
├── static/                 # Static assets (CSS, JS, images)
├── data/
│   └── holiday_info.json   # Holiday descriptions and traditions
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Adding Holiday Information

Holiday descriptions and traditions are stored in `data/holiday_info.json`. To add information for a new holiday:

1. Open `data/holiday_info.json`
2. Add the country code as a top-level key if it doesn't exist
3. Add the holiday name as a key under the country
4. Provide description, traditions array, observance, and source

Example:
```json
{
  "US": {
    "New Holiday": {
      "description": "Description of the holiday...",
      "traditions": ["Tradition 1", "Tradition 2"],
      "observance": "Federal holiday",
      "source": "Source attribution"
    }
  }
}
```

## Deployment

### GitHub Pages (Static)

For static deployment, you can use GitHub Actions to pre-generate holiday calendars for common countries/years.

### Platform-as-a-Service

Deploy to platforms like Render, Heroku, or Fly.io that support Python applications:

1. Ensure your `requirements.txt` is up to date
2. Set any necessary environment variables (PORT, etc.)
3. Deploy using the platform's preferred method

## License

MIT License - feel free to use, modify, and distribute this project.

## Acknowledgments

- Holiday data powered by the [python-holidays](https://github.com/dr-prodigy/python-holidays) library
- ICS file generation using [icalendar](https://github.com/icalendar/icalendar)
- Inspired by sites like timeanddate.com and calendar-365.com