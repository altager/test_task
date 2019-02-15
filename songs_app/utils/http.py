import ujson as json
from werkzeug.wrappers import Response


class JSONHttpResponse(Response):
    """
    Custom class for json http response
    """

    def __init__(self, response=None, status=None):
        super().__init__(response=response, content_type='application/json', status=status)


# wrapper function for JSONHttpResponse
def json_response(data):
    return JSONHttpResponse(json.dumps(data))
