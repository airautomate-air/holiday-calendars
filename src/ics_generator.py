import holidays
from icalendar import Calendar, Event
from datetime import date, datetime

class HolidayCalendarGenerator:
    def __init__(self, country='US', subdiv=None):
        self.country = country.upper()
        self.subdiv = subdiv
        # Load holidays for a reasonable range of years
        current_year = date.today().year
        years_range = list(range(current_year - 5, current_year + 10))  # 5 years back, 10 years forward
        try:
            self.holiday_lib = holidays.country_holidays(self.country, subdiv=subdiv, years=years_range)
        except NotImplementedError:
            raise ValueError(f"Holidays for country {self.country} are not supported.")

    def generate_ics(self, year=None):
        """Generate ICS calendar for given year"""
        if year is None:
            year = date.today().year

        cal = Calendar()
        cal.add('prodid', '-//Holiday Calendar Generator//holidays.example.com//')
        cal.add('version', '2.0')

        for dt, name in sorted(self.holiday_lib.items()):
            if dt.year == year:
                event = Event()
                event.add('summary', name)
                event.add('dtstart', dt)
                event.add('dtend', dt)  # All-day event
                event.add('dtstamp', datetime.now())
                event.add('uid', f'{dt.strftime("%Y%m%d")}-{hash(name) % 10000}@holidays.example.com')
                cal.add_component(event)

        return cal.to_ical()

    def get_holidays(self, year=None):
        """Get holiday data for given year"""
        if year is None:
            year = date.today().year

        return [
            {
                'date': dt.isoformat(),
                'name': name,
                'day_of_week': dt.strftime('%A'),
                'days_until': (dt - date.today()).days if dt >= date.today() else None
            }
            for dt, name in sorted(self.holiday_lib.items())
            if dt.year == year
        ]

    @classmethod
    def get_supported_countries(cls):
        """Return a list of supported country codes"""
        try:
            return holidays.list_supported_countries()
        except AttributeError:
            # Fallback for older versions
            return ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'IN', 'MX', 'BR']  # common ones