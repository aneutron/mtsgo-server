from django.db import models
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.auth.models import User


class Player(models.Model):
    account = models.ForeignKey(User)
    nickname = models.CharField(max_length=20)
    firstName = models.CharField(max_length=20, default='')
    name = models.CharField(max_length=20, default='')
    positionx = models.FloatField(default=0.0)
    positiony = models.FloatField(default=0.0)
    positionz = models.FloatField(default=0.0)
    score = models.IntegerField(default=0)
    questionHistoric = models.CharField(max_length=55, validators=[validate_comma_separated_integer_list], default='[]')

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
        ('1', answer1),
        ('2', answer2),
        ('3', answer3),
        ('4', answer4),
    )
    rightAnswer = models.CharField(max_length=20, choices=CHOICES)
    difficulty = models.IntegerField()
    topic = models.CharField(max_length=20)  # theme de la question
    score = models.IntegerField()  # points rapportes

    def __str__(self):
        return self.questionText


class Spot(models.Model):
    centrex = models.FloatField()
    centrey = models.FloatField()
    centrez = models.FloatField(default=0)
    rayon = models.IntegerField()
    currentQuestion = models.ForeignKey('Question')
    questionList = models.CharField(max_length=20, validators=[validate_comma_separated_integer_list])
    startTime = models.IntegerField()

    def __str__(self):
        return 'x=' + str(self.centrex) + ' y=' + str(self.centrey) + ' z=' + str(self.centrez)


class Zone(models.Model):
    name = models.CharField(max_length=20)
    points = models.TextField()

    def __str__(self):
        return self.name
