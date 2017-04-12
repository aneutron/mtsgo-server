# -*- coding: utf8 -*-
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from tokenapi.tokens import token_generator

User = get_user_model()


# Creates a token if the correct username and password is given
# Required: username&password
# Returns: success&token&user

def token_new(request, admin=False):
    if ('username' in request.json_data) or ('password' in request.json_data):
        username = request.json_data['username']
        password = request.json_data['password']
    else:
        username = None
        password = None

    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            if admin:
                if not user.is_staff:
                    return HttpResponseForbidden("Not an admin.")
            data = {
                'token': token_generator.make_token(user),
                'user_id': user.pk,
            }
            return JsonResponse(data)
        else:
            return JsonResponse("Unable to log you in, please try again.", status=403, safe=False)
    else:
        return JsonResponse("Must include 'username' and 'password' as parameters.", status=403, safe=False)