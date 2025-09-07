import json


def lambda_handler(event, context):
    """
    AWS Lambda handler for ThinkingTest API.
    
    Returns a simple Hello World response.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
        },
        'body': json.dumps({
            'message': 'Hello from ThinkingTest!'
        })
    }