"""
Source: https://stackoverflow.com/questions/52711580/how-to-see-graphene-django-debug-logs

Does not work yet
"""
from django.core.handlers.wsgi import WSGIRequest
from promise import is_thenable
from functools import partial
import logging
import sys
import json

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class DebugMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request:WSGIRequest):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)


        # Code to be executed for each request/response after
        # the view is called.

        return response

    def on_error(self, error, info):
        log_request_body(info)

    def resolve(self, next, root, info, **args):
        result = next(root, info, **args)
        if is_thenable(result):
            result.catch(partial(self.on_error, info=info))
        return result


def log_request_body(info):
    body = info.context._body.decode("utf-8")
    try:
        json_body = json.loads(body)
        logging.error(
            " User: %s \n Action: %s \n Variables: %s \n Body: %s",
            info.context.user,
            json_body["operationName"],
            json_body["variables"],
            json_body["query"],
        )
    except:
        logging.error(body)
