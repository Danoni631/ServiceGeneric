import sys
import subprocess

required_packages = ['flask', 'flask_cors', 'requests']

def install_missing_packages():
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Library '{package}' don't finded. Installing automatically...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_missing_packages()

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

WMO_CODES = {
    0: "Céu Limpo",
    1: "Predominantemente Limpo",
    2: "Parcialmente Nublado",
    3: "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com Geada",
    51: "Garoa Leve",
    53: "Garoa Moderada",
    55: "Garoa Densa",
    61: "Chuva Leve",
    63: "Chuva Moderada",
    65: "Chuva Forte",
    80: "Pancadas de Chuva Leves",
    81: "Pancadas de Chuva Moderadas",
    82: "Pancadas de Chuva Violentas",
    95: "Trovoada Leve/Moderada",
    96: "Trovoada com Granizo Leve",
    99: "Trovoada com Granizo Forte"
}

def get_coordinates(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'WeatherAppPython/1.0'}
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name']
    except Exception as e:
        print(f"Geolocalization error: {e}")
    return None, None, None

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')

    if not city:
        return jsonify({
            "success": False,
            "error": "Inform 'city' parametter. Example: /api/weather?city=Fortaleza"
        }), 400

    lat, lon, display_name = get_coordinates(city)
    
    if not lat or not lon:
        return jsonify({
            "success": False,
            "error": "City don't finded"
        }), 404

    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
        'timezone': 'auto'
    }

    try:
        response = requests.get(weather_url, params=params, timeout=5)
        weather_data = response.json()
        current = weather_data.get('current', {})

        code = current.get('weather_code', -1)
        condition = WMO_CODES.get(code, "Unknown")

        formatted_response = {
            "success": True,
            "data": {
                "city": display_name.split(',')[0],
                "full_address": display_name,
                "coordinates": {"lat": lat, "lon": lon},
                "temperature": current.get('temperature_2m'),
                "feels_like": current.get('apparent_temperature'),
                "humidity": current.get('relative_humidity_2m'),
                "wind_speed_kmh": current.get('wind_speed_10m'),
                "condition": condition,
                "weather_code": code,
                "unit": {
                    "temperature": "°C",
                    "wind_speed": "km/h",
                    "humidity": "%"
                }
            }
        }
        return jsonify(formatted_response)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Fail to get meteorologic data: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Weather server :D 🌦️"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
