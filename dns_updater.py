import requests

from settings import my_settings
from db import Log

def updateRecord(stringIP: str, linodeToken: str):

    # Replace these variables with your information
    LINODE_TOKEN = linodeToken
    DOMAIN_ID = '2978739'
    RECORD_ID = '35481449'

    # Linode API endpoint for updating a DNS record
    url = f'https://api.linode.com/v4/domains/{DOMAIN_ID}/records/{RECORD_ID}'

    # Headers for authentication
    headers = {
        'Authorization': f'Bearer {LINODE_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Data to update the DNS record
    data = {
        'target': stringIP,
    }

    # Make the PUT request to update the DNS record
    response = requests.put(url, headers=headers, json=data)

    # Check if the update was successful
    if response.status_code == 200:
        Log.write('DNS record updated successfully!')
        Log.write(response.json())
    else:
        Log.write(f'Failed to update DNS record: {response.status_code}')
        Log.write(response.json())
        

