import json
import boto3
import os

def lambda_handler(event, context):
    # Obtiene la IP pública de la instancia
    
    ec2 = boto3.client('ec2')

    instance_id = event['detail']['instance-id'][0]

    instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

    public_ip = instance.get('PublicIpAddress', '' )

    # Envía la IP pública a la URL
    data = {
        'nueva_ip': public_ip,
        'clave' : os.environ.get('MASTER_KEY','')
        }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(os.environ.get('UPDATE_URL',''), data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        print()
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'IP pública enviada correctamente.'})
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f"Error al enviar la IP pública: {response.status_code}"
                })
        }
