import os
import requests
import json
from datetime import datetime
import boto3


kinesis_stream = 'weatherKinesisStream'
openweather_api_key = os.environ['weather']

def analyze_weather_sentiment(weather_data):
    current_weather = weather_data['current']
    temp = current_weather['temp'] - 273.15  # Convertir de Kelvin a Celsius
    humidity = current_weather['humidity']
    clouds = current_weather['clouds']
    weather_condition = current_weather['weather'][0]['main']

    sentiment = ''

    # Análisis de la temperatura
    if temp < 10:
        sentiment += 'Cold, '
    elif 10 <= temp <= 25:
        sentiment += 'Pleasant, '
    else:
        sentiment += 'Hot, '

    # Análisis de la humedad
    if humidity > 80:
        sentiment += 'Humid, '
    elif humidity < 30:
        sentiment += 'Dry, '
    else:
        sentiment += 'Comfortable Humidity, '

    # Análisis de nubosidad
    if clouds > 80:
        sentiment += 'Cloudy, '
    elif clouds < 20:
        sentiment += 'Clear, '
    else:
        sentiment += 'Partly Cloudy, '

    # Condición general del clima
    if weather_condition in ['Rain', 'Snow', 'Thunderstorm']:
        sentiment += 'Bad Weather'
    else:
        sentiment += 'Good Weather'

    return sentiment.strip(', ')

def get_data(event, context):
    kinesis = boto3.client('kinesis')
    lat = '40.71'
    long = '74.00'
    exclude = 'minutely'
    fecha = datetime.now().strftime('%Y-%m-%d')

    api_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={long}&date={fecha}&appid={openweather_api_key}'

    try:
        response = requests.get(api_url)
        weather_data = response.json()

        # Imprimir los datos meteorológicos recolectados
        print("Datos Meteorológicos Recolectados:", json.dumps(weather_data, indent=4))

        # Realizar análisis de sentimientos
        weather_sentiment = analyze_weather_sentiment(weather_data)
        print('Weather Sentiment:', weather_sentiment)

        # Enviar datos a Kinesis
        kinesis.put_record(
            StreamName=kinesis_stream,
            Data=json.dumps(weather_data),
            PartitionKey=str(weather_data['current']['dt'])
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Se enviaron los datos a Kinesis'})
        }

    except Exception as e:
        print(f"Error en la solicitud a la API de OpenWeather o al enviar datos a Kinesis: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }

