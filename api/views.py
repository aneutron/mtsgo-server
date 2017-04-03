from django.views import View
from django.http import JsonResponse
from mtsgo.helpers import handle_exception
from mtsgo.tokenapi.views import token_new
from api.models import *
import math


class AuthView(View):
    def get(self, request):
        """
        Authentifier l'utilisateur.
        :param request: HttpRequest with json_data field.
        :return: c.f. mtsgo.tokenapi.views.token_new
        """
        return token_new(request)

    def post(self, request):
        """
        Crée un compte pour l'utilisateur, et en parallèle, crée une instance de Player liée avec le compte.
        """
        req_data = request.json_data
        if 'creds' not in req_data:
            return JsonResponse('Malformed JSON input', status=401, safe=False)
        req_data = req_data['creds']
        print(repr(req_data))
        if ('email' not in req_data) or ('username' not in req_data) or ('password' not in req_data):
            return JsonResponse('Missing parameters for ', status=401, safe=False)
        try:
            user = User.objects.create_user(username=req_data['username'], email=req_data['email'],
                                            password=req_data['password'])
            player = Player(account=user, nickname=user.username)
            player.save()
        except Exception as e:
            handle_exception(e, request)
            return JsonResponse("Une erreure a eu lieu lors de l'inscription", status=500, safe=False)
        return JsonResponse('', status=200)


class UpdatePosition(View):
    def post(self, req):
        """
        Met à jour la position du joueur.
        """
        player = Player.objects.filter(account=req.user)
        if not player:
            return JsonResponse('Joueur introuvable.', status=500, safe=False)
        if 'position' not in req.json_data:
            return JsonResponse('Malformed JSON Input', status=401, safe=False)
        req_data = req.json_data
        if ('x' not in req_data) or ('y' not in req_data) or ('z' not in req_data):
            return JsonResponse('Malformed JSON Input', status=401, safe=False)
        try:
            x, y, z = float(req_data['x']), float(req_data['y']), float(req_data['z'])
        except ValueError as e1:
            handle_exception(e1, request=req)
            return JsonResponse('Malformed coordinates. Unable to parse to float.', status=401, safe=False)
        if (not math.isfinite(x)) or (not math.isfinite(y)) or (not math.isfinite(z)):
            return JsonResponse('Your coordinates can\'t be infinity or NaN, idiot. Tg.', status=401, safe=False)
        player.positionx = x
        player.positiony = y
        player.positionz = z
        try:
            player.save()
        except Exception as e2:
            handle_exception(e2, req)
            return JsonResponse('Could not update position.', status=500, safe=False)
        return JsonResponse('', status=200, safe=False)


class Questions(View):

    def get(self, request, qid=None):
        if qid:
            return self._get_question_by_id(qid)
        else:
            return self._get_nearby_spots(request)

    def _get_question_by_id(self, qid):
        return JsonResponse("No fucker. "+ str(qid), status=200, safe=False)

    def _get_nearby_spots(self,req):
        return JsonResponse("Hey fucker", status=200, safe=False)

class PlayerInfo(View):
    pass


class PlayerHistory(View):
    pass
