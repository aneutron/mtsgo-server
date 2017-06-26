from django.contrib import admin
import datetime
from .models import *
# -*- coding: utf8 -*-

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ('current_question', 'centrex', 'centrey', 'centrez', 'start_time')

    def current_question(self, obj):
        return obj.currentQuestion.questionText

    def start_time(self, obj):
        return datetime.datetime.utcfromtimestamp(obj.startTime)

    current_question.short_description = 'Question active'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('questionText', 'difficulty', 'topic', 'score')

@admin.register(ExclusionZone)
class ExclusionZoneAdmin(admin.ModelAdmin):
    list_fields = ('name', 'number_of_summits')

    def number_of_summits(self, obj):
        return(len(json_decode(obj.points)))
    number_of_summits.short_description = 'Nb. de sommets'


# Register your models here.
