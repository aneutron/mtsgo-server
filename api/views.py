# -*- coding: utf8 -*-
from django.core.exceptions import ValidationError
from django.core import serializers
from django.core.validators import EmailValidator
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from mtsgo.tokenapi.views import token_new
from mtsgo.geocalc import *
from mtsgo.helpers import handle_exception
from api.models import *
from math import isfinite
import json, random, logging

# One logger is enough for the whole project.
logger = logging.getLogger('mtsgo')


class AuthView(View):
    def post(self, request):
        """
        Authentifier l'utilisateur.
        :param request: HttpRequest with json_data field.
        :return: c.f. mtsgo.tokenapi.views.token_new
        """
        return token_new(request)


class AuthNewView(View):
    def post(self, request):
        """
        Crée un compte pour l'utilisateur, et en parallèle, crée une instance de Player liée avec le compte.
        """
        # Vérifier que les données nécessaires aux requêtes sont là.
        req_data = request.json_data
        if 'creds' not in req_data:
            return JsonResponse(_('Malformed JSON input'), status=401, safe=False)
        req_data = req_data['creds']

        if ('email' not in req_data) or ('username' not in req_data) or ('password' not in req_data):
            return JsonResponse(_('Missing parameters for registration'), status=401, safe=False)
        # Vérifier que le non d'utilisateur n'existe pas.
        user = User.objects.filter(username=req_data['username'])
        if user.exists():
            return JsonResponse(_("Username already in use."), status=401, safe=False)
        # Vérifier que le mot de passe et l'email sont conforme à la politique de vérification.
        # TODO: Tests for this validation block.
        try:
            is_email = EmailValidator()
            is_email(req_data['email'])
            validate_password(req_data['password'])
        except ValidationError as e :
            return JsonResponse(e.messages[0], status=401, safe=False)
        try:
            user = User.objects.create_user(username=req_data['username'], email=req_data['email'],
                                            password=req_data['password'])
            player = Player(account=user, nickname=user.username)
            player.save()
        except Exception as e:
            handle_exception(e, request)
            return JsonResponse(_("An error internal error occurred during the operation."), status=500, safe=False)
        return JsonResponse(_('Account creation successful.'), status=200, safe=False)


class UpdatePosition(View):
    def post(self, req):
        """
        Met à jour la position du joueur.
        """
        player = Player.objects.get(account=req.user)
        if 'position' not in req.json_data:
            return JsonResponse(_('Malformed JSON Input'), status=401, safe=False)
        req_data = req.json_data['position']
        if ('x' not in req_data) or ('y' not in req_data) or ('z' not in req_data):
            return JsonResponse(_('Malformed JSON Input'), status=401, safe=False)
        try:
            x, y, z = float(req_data['x']), float(req_data['y']), int(req_data['z'])
        except ValueError as e1:
            handle_exception(e1, request=req)
            return JsonResponse(_('Malformed coordinates. Unable to parse to float.'), status=401, safe=False)
        if (not isfinite(x)) or (not isfinite(y)) or (not isfinite(z)):
            return JsonResponse(_('Your coordinates can\'t be infinity or NaN, idiot. TG.'), status=401, safe=False)
        if (not -180 <= y <= 180) or (not -90 <= x <= 90):
            return JsonResponse(_('Coordinates out of range.'), status=401, safe=False)
        player.positionx = x
        player.positiony = y
        player.positionz = z
        player.lastActivity = get_time()
        try:
            player.save()
        except Exception as e2:
            handle_exception(e2, req)
            return JsonResponse(_('Could not update position.'), status=500, safe=False)
        return JsonResponse(_('Position updated successfully.'), status=200, safe=False)


class Questions(View):
    def get(self, request, qid=None):
        """
        Selon la présence d'un id ou pas, retourne soit les spots environnants, soit la question spécifique.
        """
        if qid:
            return self._get_question_by_id(qid)
        else:
            return self._get_nearby_spots(request)

    def _get_question_by_id(self, qid):
        # Validated by the router.
        qid = int(qid)
        quest = Question.objects.filter(pk=qid)
        if not quest.exists():
            return JsonResponse(_('Question non trouvée.'), status=404, safe=False)
        quest = Question.objects.get(pk=qid)
        return JsonResponse({
            'question': quest.questionText,
            'answer1': quest.answer1,
            'answer2': quest.answer2,
            'answer3': quest.answer3,
            'answer4': quest.answer4,
            'score': quest.score,
            'difficulty': quest.difficulty,
            'topic': quest.topic
        }, status=200)

    def _get_nearby_spots(self, req):
        # FIXME: This bad boy is gonna need to be optimized, A LOT.
        # Ronan suggested that we cluster the map, and only compare the questions from neighboring clusters,
        # which is a very good idea. Could be done with Django's in-mem cache.
        player = Player.objects.get(account=req.user)
        # Note from a.boudhar: I should be in jail for the code I will be writing. Don't judge us. We need a v0.
        spots = Spot.objects.all()
        neighboring = []
        for spot in spots:
            if geo_distance_between_points(player.getPosition(), spot.getPosition()) < spot.rayon:
                neighboring.append({
                    'id': spot.pk,
                    'question': spot.currentQuestion.questionText,
                    'resp1': spot.currentQuestion.answer1,
                    'resp2': spot.currentQuestion.answer2,
                    'resp3': spot.currentQuestion.answer3,
                    'resp4': spot.currentQuestion.answer4,
                    'score': spot.currentQuestion.score,
                    'difficulty': spot.currentQuestion.difficulty,
                    'position': spot.getPosition(),
                })
        return JsonResponse({'questions': neighboring}, status=200)

    def post(self, req):
        """
        Traiter l'essai de réponse à une question (à un spot).
        """
        # First check the parameters are sent correctly
        if 'answer' not in req.json_data:
            return JsonResponse(_('Malformed JSON input.'), status=401, safe=False)
        if ('qid' not in req.json_data['answer']) or ('answ_number' not in req.json_data['answer']):
            return JsonResponse(_('Malformed JSON input.'), status=401, safe=False)
        try:
            spotid = int(req.json_data['answer']['qid'])
            answ_id = int(req.json_data['answer']['answ_number'])
        except ValueError:
            return JsonResponse(_('Unable to parse numeric literals from the request.'), status=401, safe=False)
        player = Player.objects.get(account=req.user)
        # Check that user is not in an exclusion zone.
        # FIXME: Use django in-memory cache, it will accelerate this a LOT. Especially zone unloading.
        zones = ExclusionZone.objects.all()
        for z in zones:
            sommets = json.loads(z.points)
            if geo_point_in_polygon(player.getPosition(), sommets):
                return JsonResponse(_('Cannot play in an exclusion zone.'), status=401, safe=False)
        # Check if spot exists
        # FIXME: Use heuristics to keep a low but frequented cache of spots. Maybe cache all until a threshold.
        try:
            spot = Spot.objects.get(pk=spotid)
        except Spot.DoesNotExist:
            return JsonResponse(_('Spot not found.'), status=404, safe=False)
        # Check if spot is active
        if spot.startTime > time.time():
            return JsonResponse(_('Spot not found.'), status=404, safe=False)
        # Check if user is within answering distance
        if geo_distance_between_points(spot.getPosition(), player.getPosition()) > spot.rayon:
            return JsonResponse(_('Too far to answer this question.'), status=401, safe=False)
        # Finally check is the answer is correct.
        if spot.currentQuestion.rightAnswer != answ_id:
            return JsonResponse(_('Sorry wrong answer.'), status=402, safe=False)
        # If the user answered correctly, add score points, and add question to history.
        player.score = player.score + spot.currentQuestion.score
        player.addQuestionToHistory(spot.currentQuestion.pk)
        try:
            player.save()
        except Exception as e:
            logger.error("[INTERNAL ERR] Unable to update player " + str(player.pk))
            handle_exception(e, req)
            return JsonResponse('Unable to update player.', status=500, safe=False)
        # Update the spot with a question and add a delay.
        # (No try try/except block as validation would be enforced at creation by django)
        spotQuestions = [int(i) for i in spot.questionList.split(',')]
        questionId = random.choice(spotQuestions)
        try:
            question = Question.objects.get(pk=questionId)
        # In case the question reference is wrong.
        except Exception:
            logger.error("[INTERNAL ERR] Bad question reference on spot " + str(spotid) + ": " + str(questionId))
            return JsonResponse(_("An error internal error occurred during the operation."), status=500, safe=False)
        spot.currentQuestion = question
        spot.startTime = int(time.time()) + spot.delay
        try:
            spot.save()
        except Exception as e:
            handle_exception(e, req)
            return JsonResponse(_("An error internal error occurred during the operation."), status=500, safe=False)
        # If we're here, then everything (hopefully) is checked. Let's congratulate him.
        return JsonResponse('Successfully answered the question.', status=200, safe=False)


class PlayerInfo(View):
    """
    Renvoie certaines stats du joueur qui en fait la demande
    """

    def get(self, req):
        player = Player.objects.get(account=req.user)
        return JsonResponse({
            'nickname': req.user.username,
            'score': player.score,
        }, status=200, safe=False)


class PlayerHistory(View):
    def get(self, req):
        player = Player.objects.get(account=req.user)
        hist = player.questionHistory
        if len(hist) == 0:
            return JsonResponse({}, status=200)
        questions_ids = [int(y) for y in hist.split(',')]
        questions = Question.objects.filter(pk__in=questions_ids)
        history = [{
                       'question': x.questionText,
                       'score': x.score,
                       'difficulty': x.difficulty,
                       'topic': x.topic,
                   } for x in questions]
        return JsonResponse({'history': history}, status=200)
