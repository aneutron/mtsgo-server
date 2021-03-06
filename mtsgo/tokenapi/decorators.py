# -*- coding: utf8 -*-
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from functools import wraps


def token_required(view_func, admin=False):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = None
        token = None

        if ('user_id' in request.json_data) and ('token' in request.json_data):
            user = request.json_data['user_id']
            token = request.json_data['token']
            del request.json_data['token'], request.json_data['user_id']

        # Now that I think about it, it's a bad idea to get data on JSON reqs.
        if ('user_id' in request.GET) or ('token' in request.GET):
            user = request.GET.get('user_id')
            token = request.GET.get('token')

        if not (user and token):
            return HttpResponseForbidden("Must include 'user_id' and 'token' parameters with request.")

        user = authenticate(pk=user, token=token)
        if user:
            if admin:
                if not user.is_staff:
                    return HttpResponseForbidden("Not an admin.")
            request.user = user
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()

    return _wrapped_view
