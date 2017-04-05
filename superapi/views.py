from django.views import View
from django.http import JsonResponse
from mtsgo.helpers import handle_exception
from mtsgo.tokenapi.views import token_new
from api.models import *
from django.core import serializers
import psutil
import json


class ServerState(View):
    def get(self, request):
        cpuPercent = psutil.cpu_percent(interval=1, percpu=True)
        mem = psutil.virtual_memory()
        memPercent = mem.percent
        disk = psutil.disk_usage('/')
        diskTotal = disk.total
        diskUsed = disk.used
        stats = {}
        stats["cpuPercent"] = cpuPercent
        stats["memPercent"] = memPercent
        stats["diskTotal"] = diskTotal
        stats["diskUsed"] = diskUsed
        data = json.dumps(stats)
        return JsonResponse(data, status=200, safe=False)


class Questions(View):
    def get(self, request, qid=None):
        if qid:
            try:
                question = Question.objects.get(pk=qid)
                data = serializers.serialize('json', question)
                return JsonResponse(data, status=200, safe=False)
            except Question.DoesNotExist:
                return JsonResponse(status=404, safe=False)
        else:
            data = serializers.serialize('json', Question.objects.all())
            return JsonResponse(data, status=200, safe=False)

    def post(self, request, qid=None):
        pass


class PlayerPosition(View):
    pass


class Stats(View):
    pass
