from flask import jsonify

### Helper functions ###

def error_response(message, error_code, status_code=400):
    return jsonify({
        'message': message,
        'error': error_code
    }), status_code

def success_response(message, data=None, status_code=200):
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code