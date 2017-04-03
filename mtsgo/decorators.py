import json
from functools import wraps
from django.conf import settings
from django.http import HttpResponse
from django.http.request import bytes_to_text
from django.views.decorators.csrf import csrf_exempt


def decode_json(view_func):
    """
    Décorateur pour décoder les paramètres en JSON.
    :param view_func: La vue à traiter
    :return: Le vue avec un attribut json_data décodé.
    """
    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Excellent documentation at https://docs.djangoproject.com/fr/1.10/_modules/django/http/request/
        try:
            raw_d = bytes_to_text(request.body, settings.DEFAULT_CHARSET)
            #FIXME: raw_d returns a weirdly formatted string, calling json.load two times seems to resolve the problem.
            data = json.loads(json.loads(raw_d))
        except Exception as e:
            return HttpResponse('JSON input absent or not encoded correctly' , status=400)
        request.json_data = data
        return view_func(request, *args, **kwargs)
    return _wrapped_view