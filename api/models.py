from django.db import models
from django.core.validators import validate_comma_separated_integer_list, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
import time


class Player(models.Model):
    account = models.ForeignKey(User)
    nickname = models.CharField(max_length=20)
    firstName = models.CharField(max_length=20, default='')
    name = models.CharField(max_length=20, default='')
    positionx = models.FloatField(default=0.0, validators = [MinValueValidator(-90.0), MaxValueValidator(90.0)])
    positiony = models.FloatField(default=0.0, validators = [MinValueValidator(-180.0), MaxValueValidator(180.0)])
    positionz = models.FloatField(default=0.0)
    score = models.IntegerField(default=0)
    questionHistory = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list])
    lastActivity = models.IntegerField(default=time.time)

    #TODO: Test this method
    def getPosition(self):
        return (self.positionx, self.positiony, self.positionz)

    #TODO: Test this method.
    def addQuestionToHistory(self, qid):
        qids = []
        if len(self.questionHistory) > 0:
            try:
                qids = self.questionHistory.split(',')
            except ValueError as e:
                # This should not happen as entries are validated before insertion by Django.
                pass
        if len(qids) >= getattr(settings, 'MTSGO_PLAYER_HISTORY_LIMIT', 10):
            qids.pop(0)
        qids.append(str(qid))
        self.questionHistory = ','.join(qids)

    # TODO: Test this method
    def __str__(self):
        return self.nickname


class Question(models.Model):
    # Il faut garder à l'esprit que ça pourrait contenir du Latex.
    questionText = models.CharField(max_length=255)
    answer1 = models.CharField(max_length=100)
    answer2 = models.CharField(max_length=100)
    answer3 = models.CharField(max_length=100)
    answer4 = models.CharField(max_length=100)
    CHOICES = (
        (1, answer1),
        (2, answer2),
        (3, answer3),
        (4, answer4),
    )
    rightAnswer = models.IntegerField(choices=CHOICES)
    difficulty = models.IntegerField()
    topic = models.CharField(max_length=20)  # theme de la question
    score = models.IntegerField()  # points rapportes

    # TODO: Test this method
    def __str__(self):
        return self.questionText


class Spot(models.Model):
    centrex = models.FloatField(validators = [MinValueValidator(-90.0), MaxValueValidator(90.0)])
    centrey = models.FloatField(validators = [MinValueValidator(-180.0), MaxValueValidator(180.0)])
    centrez = models.IntegerField(default=0)
    rayon = models.IntegerField(validators=[MinValueValidator(0)])
    currentQuestion = models.ForeignKey('Question')
    questionList = models.CharField(max_length=255, validators=[validate_comma_separated_integer_list])
    startTime = models.IntegerField(default=time.time)
    delay = models.IntegerField()

    # TODO: Test this method too.
    def getPosition(self):
        return [self.centrex, self.centrey, self.centrez]

    def loadQuestions(self):
        self.questions = []
        if len(self.questionList) == 0:
            return
        questions_ids = [int(y) for y in self.questionList.split(',')]
        self.questions = Question.objects.filter(id__in=questions_ids)


class ExclusionZone(models.Model):
    name = models.CharField(max_length=20)
    points = models.TextField()

    #TODO: Test this method
    def __str__(self):
        return self.name
