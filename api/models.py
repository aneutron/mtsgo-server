from django.db import models
from django.core.validators import validate_comma_separated_integer_list


# Create your models here.
class Player(models.Model):
    nickname = models.CharField(max_length=20)
    firstName = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    positionx = models.FloatField()
    positiony = models.FloatField()
    positionz = models.FloatField(default=0)
    score = models.IntegerField(default=0)
    questionHistoric = models.CharField(max_length=20, validators=[validate_comma_separated_integer_list])

    def __str__(self):
        return self.nickname

class Question(models.Model):
    questionText = models.CharField(max_length=100)
    answer1 = models.CharField(max_length=20)
    answer2 = models.CharField(max_length=20)
    answer3 = models.CharField(max_length=20)
    answer4 = models.CharField(max_length=20)
    CHOICES = (
        ('1', answer1),
        ('2', answer2),
        ('3', answer3),
        ('4', answer4),
    )
    rightAnswer = models.CharField(max_length=20, choices=CHOICES)
    difficulty = models.IntegerField()
    topic = models.CharField(max_length=20)     # theme de la question
    score = models.IntegerField()   # points rapportes

    def __str__(self):
        return self.questionText

class Spot(models.Model):
    centrex = models.FloatField()
    centrey = models.FloatField()
    centrez = models.FloatField(default=0)
    rayon = models.IntegerField()
    CurrentQuestion = models.ForeignKey('Question')
    questionList = models.CharField(max_length=20, validators=[validate_comma_separated_integer_list])
    startTime = models.TimeField()  # je suis pas sur de ce models

    def __str__(self):
        return 'x='+str(self.centrex)+' y='+str(self.centrey)+' z='+str(self.centrez)

class Zone(models.Model):
    name = models.CharField(max_length=20)
    # points = { [ [ , , ] ] }   je ne vois pas comment faire

    def __str__(self):
        return self.name