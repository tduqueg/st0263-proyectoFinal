import os
import requests
import json
from dotenv import load_dotenv
import boto3

load_dotenv()
kinesis_stream = 'weatherKinesisStream'

def get_data(event, context):
    # Configura las variables de entorno
    openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
    kinesis_stream_name = os.getenv('KINESIS_STREAM_NAME')
    kinesis = boto3.client('kinesis')
    latitude = '6.25'
    longitude = '-75.56'
    exclude = 'minutely'  # Puedes ajustar las partes a excluir según tus necesidades
    date = '2023-11-16'
    # Realiza la llamada a la API de OpenWeather One Call 3.0
    # api_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude={exclude}&appid={openweather_api_key}'
    api_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&date={date}&appid={openweather_api_key}'

    try:
        response = requests.get(api_url)
        data = response.json()
        # print(data)
        # Configura el productor de Kinesis

        # Envia cada registro al flujo de Kinesis
        # print(data)
        # print(data['current']['dt'])
        kinesis.put_record(
            StreamName=kinesis_stream,
            Data=json.dumps(data),
            # Specify PartitionKey for each record
            PartitionKey=str(data['current']['dt'])  # Use record timestamp as PartitionKey
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Datos enviados exitosamente a Kinesis'})
        }

    except Exception as e:
        print(f"Error en la solicitud a la API de OpenWeather o al enviar datos a Kinesis: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }

