import os
from flask import Flask, render_template, request
import requests
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Aether-Track', version='1.0.0')
API_KEY = os.getenv('WEATHER_API_KEY')

@app.route('/')
def index():
    # Default to Bengaluru if no city is searched
    city = request.args.get('city', 'Bengaluru')
    
    if not API_KEY:
        return render_template('index.html', error="System Error: Weather API Key is missing in environment variables.")

    # OpenWeatherMap API Call
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Handle "City Not Found" or Invalid API Key
        if data.get("cod") != 200:
            return render_template('index.html', error=f"Error: {data.get('message', 'City not found')}")

        # Data structure for the UI
        weather_context = {
            'city': data['name'],
            'temp': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'main': data['weather'][0]['main'].lower(), # This triggers the UI animations
            'icon': data['weather'][0]['icon']
        }
        return render_template('index.html', weather=weather_context)
    
    except Exception as e:
        return render_template('index.html', error=f"Connection Error: {str(e)}")

# --- SRE BEST PRACTICES: HEALTH CHECKS ---
# Kubernetes will use this to monitor the pod's health
@app.route('/health')
def health_check():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    # Running on 0.0.0.0 is required for Docker/Kubernetes accessibility
    app.run(host='0.0.0.0', port=5000)
