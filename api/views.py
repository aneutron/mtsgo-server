from django.views import View
from django.http import JsonResponse


class NewAccount(View):
    pass


class UpdatePosition(View):
    pass


class Questions(View):

    def get(self, request):
        return JsonResponse({
            'hey': 'hey you!',
        })


class PlayerInfo(View):
    pass


class PlayerHistory(View):
    pass
