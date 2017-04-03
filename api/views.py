from django.views import View
from django.http import JsonResponse
from django.http import QueryDict


class NewAccount(View):
    pass


class UpdatePosition(View):
    def post(self, request):
        r=QueryDict(request.body)

        x, y, z = r['x'], r['y'], r['z']

        print(x,y,z)

        return JsonResponse({})

class Questions(View):

    def get(self, request):
        return JsonResponse({
            'hey': 'hey you!',
        })
    pass


class PlayerInfo(View):
    pass


class PlayerHistory(View):
    pass
