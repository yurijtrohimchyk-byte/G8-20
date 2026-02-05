import json
from skyfield import api, almanac
from datetime import datetime, timedelta

# --- ВАШІ КООРДИНАТИ (Редагуйте тут) ---
LAT = 49.8500  # deviceLat
LON = 29.9100  # deviceLon
ALT = 180.0    # deviceAlt (висота у метрах)

def get_astro():
    ts = api.load.timescale()
    # Завантаження ефемерид NASA (найвища точність)
    eph = api.load('de421.bsp')
    earth = eph['earth']
    location = earth + api.Topos(latitude_degrees=LAT, longitude_degrees=LON, elevation_m=ALT)

    now = datetime.utcnow()
    # Рахуємо на сьогодні і на завтра, щоб завжди був запас
    t0 = ts.utc(now.year, now.month, now.day)
    t1 = ts.utc(now.year, now.month, now.day + 2)

    def find_events(body_obj):
        t, y = almanac.find_discrete(t0, t1, almanac.meridian_transits(eph, body_obj, location))
        # Фільтруємо події саме для поточної доби
        zenith = int(t[y == 1][0].utc_datetime().timestamp()) if any(y==1) else 0
        nadir = int(t[y == 0][0].utc_datetime().timestamp()) if any(y==0) else 0
        return zenith, nadir

    sz, sn = find_events(eph['sun'])
    mz, mn = find_events(eph['moon'])

    data = {
        "sz": sz, "sn": sn,
        "mz": mz, "mn": mn,
        "lat": LAT, "lon": LON, "alt": ALT,
        "updated_utc": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('astro_data.json', 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    get_astro()
