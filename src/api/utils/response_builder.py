from flask import jsonify

### Helper functions ###

def error_response(message, error_code, status_code=400):
    """
    Generates a JSON error response with a given message, error code, and status code.
        
    Args:
        message (str): The error message to be included in the response.
        error_code (str): The specific error code representing the error type.
        status_code (int, optional): The HTTP status code for the response. Defaults to 400.

    
    Returns:
        tuple: A tuple containing a JSON response and the HTTP status code.
    """
    return jsonify({
        'message': message,
        'error': error_code
    }), status_code

def success_response(message, data=None, status_code=200):
    """Build a success response for an API request.

    Args:
        message (str): The success message to include in the response.
        data (dict, optional): Additional data to include in the response. Defaults to None.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.
        
    Returns:
        tuple: A tuple containing the JSON response and the HTTP status code.
    """
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code