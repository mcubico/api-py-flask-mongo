def make_api_http_response(status: int, message: str = None, data: object = None, error: bool = False):
    return {
        "status": status,
        "message": message,
        "data": data,
        "error": error
    }
