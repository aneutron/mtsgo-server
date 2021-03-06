# -*- coding: utf8 -*-
from django.conf.urls import url
from mtsgo.decorators import try_decode_json
from mtsgo.tokenapi.decorators import token_required
from superapi import views


urlpatterns = [
    url(r'^auth/$', try_decode_json(views.AuthView.as_view()), name='admin_auth'),
    url(r'^spots/$',try_decode_json(token_required(views.SpotsView.as_view(), True)), name='admin_spots_global'),
    url(r'^spots/(?P<spot_id>[0-9]+)/$', try_decode_json(token_required(views.SpotsView.as_view(), True)),name='admin_spots_by_id'),
    url(r'^spots/delete/(?P<spot_id>[0-9]+)/$', try_decode_json(token_required(views.SpotDeleteView.as_view(), True)), name="admin_delete_spot"),
    url(r'^questions/$',try_decode_json(token_required(views.QuestionsView.as_view(), True)), name='admin_questions_global'),
    url(r'^questions/(?P<qid>[0-9]+)/$', try_decode_json(token_required(views.QuestionsView.as_view(), True)),name='admin_question_by_id'),
    url(r'^questions/delete/(?P<qid>[0-9]+)/$', try_decode_json(token_required(views.QuestionDeleteView.as_view(), True)), name="admin_delete_question"),
    url(r'^carte/$', try_decode_json(token_required(views.CarteView.as_view(), True)), name="admin_carte"),
    url(r'^position/$', try_decode_json(token_required(views.PlayerPositionView.as_view(), True)), name='admin_position'),
    url(r'^position/(?P<pid>[0-9]+)/$', try_decode_json(token_required(views.PlayerPositionView.as_view(), True)),name='admin_position_by_id'),
    url(r'^state/', try_decode_json(token_required(views.ServerStateView.as_view(), True)), name='admin_server_state'),
    url(r'^stats/', try_decode_json(token_required(views.StatsView.as_view())), name='admin_server_stats'),
    url(r'^zones/$',try_decode_json(token_required(views.ExclusionZoneView.as_view(), True)), name='admin_exclusion_zone_global'),
    url(r'^zones/(?P<zone_id>[0-9]+)/$',try_decode_json(token_required(views.ExclusionZoneView.as_view(), True)), name='admin_exclusion_zone_by_id'),
    url(r'^zones/delete/(?P<zone_id>[0-9]+)/$',try_decode_json(token_required(views.ExclusionZoneDeleteView.as_view(), True)), name='admin_delete_zone'),
]
