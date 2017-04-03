from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from mtsgo.decorators import decode_json

from functools import wraps

def token_required(view_func):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = None
        token = None

        user = request.json_data['user_id']
        token = request.json_data['token']

        if not (user and token):
            return HttpResponseForbidden("Must include 'user' and 'token' parameters with request.")

        user = authenticate(pk=user, token=token)
        if user:
            request.user = user
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()
    return _wrapped_view
