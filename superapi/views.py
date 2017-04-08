import math

from django.core.exceptions import ValidationError
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from mtsgo.tokenapi.views import token_new
from api.models import *
import psutil, json


class AuthView(View):
    def post(self, req):
        return token_new(req, True)

# FIXME: Edit to support **kwargs constructors.
class SpotsView(View):
    def get(self, request, spot_id=None):
        if spot_id:
            try:
                data = self._get_spot_by_id(spot_id)
                return JsonResponse(data, status=200)
            except Spot.DoesNotExist:
                return JsonResponse(_('Spot not found'), status=404, safe=False)
            except Question.DoesNotExist:
                # FIXME: Handle properly, shouldn't happen if everything was done through the API
                pass
        else:
            return self._get_all_spots()

    def post(self, request, spot_id=None):
        if spot_id:
            return self._update_spot_by_id(request, spot_id)
        else:
            return self._insert_spot(request)

    def delete(self, request, spot_id):
        try:
            spot = Spot.objects.get(pk=spot_id)
            spot.delete()
            return JsonResponse(_('Spot successfully deleted.'), status=200, safe=False)
        except Spot.DoesNotExist:
            return JsonResponse(_('Spot with ID=' + str(spot_id) + ' not found.'), status=404, safe=False)

    def _get_spot_by_id(self, spot_id):
        spot = Spot.objects.get(pk=spot_id)
        spot.loadQuestions()
        # TODO: Add a spot.packWithQuestions() method.
        data = {
            "centrex": spot.centrex,
            "centrey": spot.centrey,
            "centrez": spot.centrez,
            "rayon": spot.rayon,
            "startTime": spot.startTime,
            "delay": spot.delay,
            "currentQuestion": {
                'id': spot.currentQuestion.id,
                'question': spot.currentQuestion.questionText,
                'answer1': spot.currentQuestion.answer1,
                'answer2': spot.currentQuestion.answer2,
                'answer3': spot.currentQuestion.answer3,
                'answer4': spot.currentQuestion.answer4,
                'score': spot.currentQuestion.score,
                'difficulty': spot.currentQuestion.difficulty,
                'topic': spot.currentQuestion.topic
            },
            "questions": []
        }
        for quest in spot.questions:
            data["questions"].append({
                'id': quest.id,
                'question': quest.questionText,
                'answer1': quest.answer1,
                'answer2': quest.answer2,
                'answer3': quest.answer3,
                'answer4': quest.answer4,
                'score': quest.score,
                'difficulty': quest.difficulty,
                'topic': quest.topic
            })
        return data

    def _get_all_spots(self):
        spots_id = [s.pk for s in Spot.objects.all()]
        spots = []
        for spot_id in spots_id:
            spots.append(self._get_spot_by_id(spot_id))
        data = {"spots": spots}
        return JsonResponse(data, status=200)

    def _update_spot_by_id(self, request, spot_id):
        return JsonResponse(_('Not yet implemented.'), status=500, safe=False)

    def _insert_spot(self, request):
        if 'spot' not in request.json_data:
            return JsonResponse(_('Malformed JSON input.'), status=401, safe=False)
        data = request.json_data['spot']
        validated_spot = self._validate_spot_data(data)
        if type(validated_spot) is not type(Spot()):
            return validated_spot
        try:
            validated_spot.save()
            return JsonResponse(_('Spot inserted successfully.'), status=200, safe=False)
        except Exception:
            # FIXME: Shouldn't happen, but handle correctly.
            pass

    def _validate_spot_data(self, data):
        """
        Validates a spot's data and returns an error message in case it was impossible.
        :param data: Dict of data that the spot should be populated with.
        :return: In case of no error encountered, return an instance of Spot populated with appropriate data. Otherwise,
        returns a JsonResponse with an error message.
        """
        # FIXME: This is gonna be fun to test ...
        needed_keys = ['centrex', 'centrey', 'centrez', 'rayon', 'currentQuestion', 'questionList', 'startTime',
                       'delay']
        # If the first one fails first, the second is not verified, hence it's more economic this way.
        if type(data) is not type({}):
            return JsonResponse(_('Malformed JSON input.'), status=401, safe=False)
        for k in needed_keys:
            if k not in data.keys():
                return JsonResponse(_('Malformed JSON input.'), status=401, safe=False)
        # Try parsing all numeric literals.
        try:
            x, y, z = float(data['centrex']), float(data['centrey']), int(data['centrez'])
            rayon = int(data['rayon'])
            int(data['currentQuestion'])
            startTime, delay = int(data['startTime']), int(data['delay'])
        except ValueError:
            return JsonResponse(_('Unable to parse correct numeric literals.'), status=401, safe=False)
        # Validate question list format.
        # NOTE: The "spot" field is decoded so if the questionList was encoded as a list as it should be, this is the
        # right way to test it.
        # TODO: More tolerance towards questionList format.
        if type(data['questionList']) != type(''):
            return JsonResponse(_('Unable to parse correct question list.'), status=401, safe=False)
        # Validate numeric values.
        if (not math.isfinite(x)) or (not math.isfinite(y)) or (not math.isfinite(z)):
            return JsonResponse(_('Spot coordinates can\'t be infinity or NaN.'), status=401, safe=False)
        if (not -180 <= y <= 180) or (not -90 <= x <= 90):
            return JsonResponse(_('Latitude and Longitude are out of range.'), status=401, safe=False)
        # Verify that the chosen current question exists.
        currentQuestion = Question.objects.filter(pk=int(data['currentQuestion']))
        if not currentQuestion.exists():
            return JsonResponse(_('Unable find chosen currentQuestion with provided ID.'), status=401, safe=False)
        currentQuestion = Question.objects.get(pk=int(data['currentQuestion']))
        # Verify that questions in list exist.
        if len(data['questionList']) == 0:
            return JsonResponse(_('A spot needs at least one question.'), status=401, safe=False)
        questions = Question.objects.filter(id__in=data['questionList'])
        if questions.count() != len(data['questionList']):
            return JsonResponse(_('Incorrect question IDs in questionList.'), status=401, safe=False)
        questionList = ','.join([str(i) for i in data['questionList']])
        # If all is well, return a Spot instance.
        return Spot(
            centrex=x,
            centrey=y,
            centrez=z,
            rayon=rayon,
            startTime=startTime,
            delay=delay,
            questionList=questionList,
            currentQuestion=currentQuestion
        )


# FIXME: Add a Question.packAsDict() method.
class QuestionsView(View):
    def get(self, request, qid=None):
        if qid:
            try:
                quest = Question.objects.get(pk=qid)
                data = {
                    'id': quest.id,
                    'question': quest.questionText,
                    'answer1': quest.answer1,
                    'answer2': quest.answer2,
                    'answer3': quest.answer3,
                    'answer4': quest.answer4,
                    'score': quest.score,
                    'difficulty': quest.difficulty,
                    'topic': quest.topic
                }
                return JsonResponse(data, status=200)
            except Question.DoesNotExist:
                return JsonResponse(status=404, safe=False)
        else:
            data = {'questions': []}
            for quest in Question.objects.all():
                data['questions'].append({
                    'id': quest.id,
                    'question': quest.questionText,
                    'answer1': quest.answer1,
                    'answer2': quest.answer2,
                    'answer3': quest.answer3,
                    'answer4': quest.answer4,
                    'score': quest.score,
                    'difficulty': quest.difficulty,
                    'topic': quest.topic
                })
            return JsonResponse(data, status=200)

    def post(self, request, qid=None):
        if qid:
            self._update_question(request, qid)
        else:
            self._insert_question(request)

    def _update_question(self, req, qid):
        needed_keys = ['questionText', 'answer1', 'answer2', 'answer3', 'answer4', 'rightAnswer', 'difficulty', 'score',
                       'topic']
        if ('question' not in req.json_data) or (type(req.json_data['question']) != type(dict)) or (
            req.json_data['question'].keys() != needed_keys):
            return JsonResponse(_('Invalid JSON input.'), status=401, safe=False)
        try:
            # TODO: Rewrite the previously coded APIs to support this.
            # http://stackoverflow.com/questions/5503925/how-do-i-use-a-dictionary-to-update-fields-in-django-models
            Question.objects.filter(pk=qid).update(**req['question'])
            return JsonResponse(_('Question updated successfully.'), status=200, safe=False)
        except Question.DoesNotExist:
            return JsonResponse(_('Question with ID='+str(qid)+' not found.'), status=404, safe=False)
        except ValidationError as e:
            return JsonResponse(_('Question parameters are not correctly set: '+e.message()), status=401, safe=False)
        except Exception:
            return JsonResponse(_('Unable to update the question.'), status=500, safe=False)

    def _insert_question(self, req):
        needed_keys = ['questionText', 'answer1', 'answer2', 'answer3', 'answer4', 'rightAnswer', 'difficulty', 'score',
                       'topic']
        if ('question' not in req.json_data) or (type(req.json_data['question']) != type(dict)) or (
                    req.json_data['question'].keys() != needed_keys):
            return JsonResponse(_('Invalid JSON input.'), status=401, safe=False)
        try:
            quest = Question(**req['question'])
            quest.save()
            return JsonResponse(_('Question added successfully.'), status=200, safe=False)
        except ValidationError as e:
            return JsonResponse(_('Question parameters are not correctly set: ' + e.message()), status=401, safe=False)
        except Exception:
            return JsonResponse(_('Unable to update the question.'), status=500, safe=False)


class CarteView(View):
    pass


class ServerStateView(View):
    def get(self, request):
        cpuPercent = psutil.cpu_percent(interval=1, percpu=True)
        mem = psutil.virtual_memory()
        memPercent = mem.percent
        disk = psutil.disk_usage('/')
        diskTotal = disk.total
        diskUsed = disk.used
        stats = {
            "cpuPercent": cpuPercent,
            "memPercent": memPercent,
            "diskTotal": diskTotal,
            "diskUsed": diskUsed
        }
        data = json.dumps(stats)
        return JsonResponse(data, status=200, safe=False)


class PlayerPositionView(View):
    def get(self, req, pid=None):
        if pid:
            return self._get_player_position(pid)
        else:
            return self._all_players_positions()

    def _get_player_position(self, pid):
        try:
            player = Player.objects.get(pk=pid)
            return JsonResponse(data={
                'id': player.account.id,
                'x': player.positionx,
                'y': player.positiony,
                'z': player.positionz
            }, status=200)
        except Player.DoesNotExist:
            return JsonResponse(_('Unable to find player with ID='+str(pid)+'.'), status=404, safe=False)

    def _all_players_positions(self):
        players = Player.objects.all()
        data = []
        for player in players:
            data.append({
                'id': player.account.id,
                'x': player.positionx,
                'y': player.positiony,
                'z': player.positionz
            })
        return JsonResponse(data, status=200, safe=False)


class StatsView(View):
    def get(self, req):
        consideredActive = 600
        data = {
            'nbrQ': Question.objects.count(),
            'nbrJ': Player.objects.count(),
            'nbrJConnected': Player.objects.filter(lastActivity__gte=time.time()-consideredActive)
        }
        return JsonResponse(data, status=200)