from dotenv import load_dotenv
import boto3
import os
import requests
import json


load_dotenv()
kinesis_stream = 'weatherKinesisStream'

def getData(event, context):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    kinesis_stream_name = os.getenv('KINESIS_STREAM_NAME')
    kinesis = boto3.client('kinesis')
    lat = '40.71'
    long = '74.00'
    exclude = 'minutely'  
    fecha = '2023-11-16'
    api_url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={long}&date={fecha}&appid={api_key}'

    try:
        response = requests.get(api_url)
        data = response.json()
        kinesis.put_record(
            StreamName=kinesis_stream,
            Data=json.dumps(data),

            PartitionKey=str(data['current']['dt'])  
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

