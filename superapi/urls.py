from django.conf.urls import url
from mtsgo.tokenapi.decorators import token_required
from tokenapi.views import token
from mtsgo.tokenapi.views import token_new
from mtsgo.decorators import try_decode_json
from superapi import views

urlpatterns = [
    url(r'state/', views.ServerState.as_view(), name='server_state'),
]