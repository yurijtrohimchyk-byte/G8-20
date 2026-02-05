import json
from skyfield import api, almanac
from datetime import datetime

# Координати Володарка
LAT = 49.85
LON = 29.91
ALT = 180.0

def get_astro():
    try:
        # Створюємо завантажувач у папці 'data'
        loader = api.Loader('data')
        ts = loader.timescale()
        eph = loader('de421.bsp')
        
        # Правильний спосіб створення об'єкта локації за стандартом WGS84
        location = api.wgs84.latlon(LAT, LON, elevation_m=ALT)

        now = datetime.utcnow()
        # Розрахунок на поточну добу
        t0 = ts.utc(now.year, now.month, now.day)
        t1 = ts.utc(now.year, now.month, now.day + 1)

        def find_events(body_obj):
            # Використовуємо функцію meridian_transits з коректним об'єктом локації
            f = almanac.meridian_transits(eph, body_obj, location)
            t, y = almanac.find_discrete(t0, t1, f)
            
            # y=1 - зеніт (кульмінація), y=0 - надир
            zen = int(t[y == 1][0].utc_datetime().timestamp()) if any(y==1) else 0
            nad = int(t[y == 0][0].utc_datetime().timestamp()) if any(y==0) else 0
            return zen, nad

        sz, sn = find_events(eph['sun'])
        mz, mn = find_events(eph['moon'])

        res = {
            "sz": sz, "sn": sn,
            "mz": mz, "mn": mn,
            "updated": int(now.timestamp()),
            "date": now.strftime('%Y-%m-%d'),
            "info": "Calculated using Skyfield and NASA JPL DE421"
        }

        # Записуємо результат у файл
        with open('astro_data.json', 'w') as f:
            json.dump(res, f, indent=2)
            
        print("Success: astro_data.json has been updated.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    get_astro()
