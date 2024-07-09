import json
import boto3
import os
import urllib3

def lambda_handler(event, context):
    # Obtiene la IP pública de la instancia
    
    print("Update URL: ",os.environ.get('UPDATE_URL','Update URL Not Found'))
    
    ec2 = boto3.client('ec2')

    instance_id = event['detail']['instance-id'][0]
    
    instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

    public_ip = instance.get('PublicIpAddress', '' )
    
    print("Instance_id: ", instance_id)
    print("Public IP:", public_ip)

    # Envía la IP pública a la URL
    data = {
        'nueva_ip': public_ip,
        'clave' : os.environ.get('MASTER_KEY','')
        }
    headers = {'Content-Type': 'application/json'}
    
    http = urllib3.PoolManager()
 
    response = http.request('POST', os.environ.get('UPDATE_URL',''), body=json.dumps(data).encode('utf-8'), headers=headers)

    if response.status == 200:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'IP pública enviada correctamente.'})
        }
    else:
        return {
            'statusCode': response.status,
            'body': json.dumps({
                'message': f"Error al enviar la IP pública: {json.loads(response.data.decode('utf'))}"
                })
        }
