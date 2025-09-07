"""
Lambda handler for the AI Bias Psychologist application.
This handler processes API Gateway requests and routes them to appropriate functions.
"""

import json
import logging
import os
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method and path
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        # Parse JSON body if present
        try:
            if body:
                parsed_body = json.loads(body)
            else:
                parsed_body = {}
        except json.JSONDecodeError:
            parsed_body = {}
        
        # Route the request
        response = route_request(
            http_method=http_method,
            path=path,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
            body=parsed_body
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_error_response(500, f"Internal server error: {str(e)}")

def route_request(
    http_method: str,
    path: str,
    path_parameters: Dict[str, str],
    query_parameters: Dict[str, str],
    body: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Route the request to appropriate handler based on path and method.
    
    Args:
        http_method: HTTP method (GET, POST, etc.)
        path: Request path
        path_parameters: Path parameters
        query_parameters: Query parameters
        body: Request body
        
    Returns:
        API Gateway response
    """
    
    # Health check endpoint
    if path == '/' and http_method == 'GET':
        return health_check()
    
    # API endpoints
    if path.startswith('/api/'):
        api_path = path[4:]  # Remove '/api/' prefix
        
        if api_path == 'health' and http_method == 'GET':
            return health_check()
        
        elif api_path == 'probes' and http_method == 'GET':
            return get_probes(query_parameters)
        
        elif api_path == 'probes' and http_method == 'POST':
            return create_probe(body)
        
        elif api_path.startswith('probes/') and http_method == 'GET':
            probe_id = path_parameters.get('proxy', '').split('/')[-1]
            return get_probe(probe_id)
        
        elif api_path.startswith('probes/') and http_method == 'PUT':
            probe_id = path_parameters.get('proxy', '').split('/')[-1]
            return update_probe(probe_id, body)
        
        elif api_path.startswith('probes/') and http_method == 'DELETE':
            probe_id = path_parameters.get('proxy', '').split('/')[-1]
            return delete_probe(probe_id)
        
        elif api_path == 'responses' and http_method == 'GET':
            return get_responses(query_parameters)
        
        elif api_path == 'responses' and http_method == 'POST':
            return create_response(body)
        
        elif api_path == 'analytics' and http_method == 'GET':
            return get_analytics(query_parameters)
    
    # Default 404 response
    return create_error_response(404, "Not Found")

def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return create_success_response({
        "status": "healthy",
        "service": "ai-bias-psychologist",
        "version": os.environ.get('APP_VERSION', '1.0.0'),
        "environment": os.environ.get('ENVIRONMENT', 'unknown')
    })

def get_probes(query_parameters: Dict[str, str]) -> Dict[str, Any]:
    """Get list of probes."""
    # TODO: Implement actual probe retrieval logic
    return create_success_response({
        "probes": [
            {
                "id": "1",
                "name": "Anchoring Bias",
                "description": "Test for anchoring bias in decision making",
                "status": "active"
            },
            {
                "id": "2", 
                "name": "Confirmation Bias",
                "description": "Test for confirmation bias in information processing",
                "status": "active"
            }
        ]
    })

def create_probe(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new probe."""
    # TODO: Implement probe creation logic
    return create_success_response({
        "message": "Probe created successfully",
        "probe_id": "new-probe-id"
    }, status_code=201)

def get_probe(probe_id: str) -> Dict[str, Any]:
    """Get a specific probe by ID."""
    # TODO: Implement probe retrieval logic
    return create_success_response({
        "id": probe_id,
        "name": f"Probe {probe_id}",
        "description": "Sample probe description",
        "status": "active"
    })

def update_probe(probe_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Update a specific probe."""
    # TODO: Implement probe update logic
    return create_success_response({
        "message": f"Probe {probe_id} updated successfully"
    })

def delete_probe(probe_id: str) -> Dict[str, Any]:
    """Delete a specific probe."""
    # TODO: Implement probe deletion logic
    return create_success_response({
        "message": f"Probe {probe_id} deleted successfully"
    })

def get_responses(query_parameters: Dict[str, str]) -> Dict[str, Any]:
    """Get list of responses."""
    # TODO: Implement response retrieval logic
    return create_success_response({
        "responses": []
    })

def create_response(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new response."""
    # TODO: Implement response creation logic
    return create_success_response({
        "message": "Response created successfully",
        "response_id": "new-response-id"
    }, status_code=201)

def get_analytics(query_parameters: Dict[str, str]) -> Dict[str, Any]:
    """Get analytics data."""
    # TODO: Implement analytics logic
    return create_success_response({
        "analytics": {
            "total_probes": 0,
            "total_responses": 0,
            "bias_scores": {}
        }
    })

def create_success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """Create a successful API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data)
    }

def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create an error API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'statusCode': status_code
        })
    }
