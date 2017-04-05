import json
from functools import wraps
from django.conf import settings
from django.http import HttpResponse
from django.http.request import bytes_to_text
from django.views.decorators.csrf import csrf_exempt

# Préférer celle là aux autres. On n'aura besoin d'entrées JSON qu'en POST.
def try_decode_json(view_func):
    """
    Décorateur pour décoder les paramètres en JSON non obligatoirement.
    :param view_func: La vue à traiter
    :return: Le vue avec un attribut json_data décodé.
    """

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        request.json_data = {}
        # Excellent documentation at https://docs.djangoproject.com/fr/1.10/_modules/django/http/request/
        if request.method == 'POST':
            try:
                raw_d = bytes_to_text(request.body, settings.DEFAULT_CHARSET)
                data = {}
                if len(raw_d) > 0:
                    data = json.loads(raw_d)
                request.json_data = data
            except Exception as e:
                return HttpResponse('JSON input absent or not encoded correctly for a POST request. '+e.__str__(), status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
