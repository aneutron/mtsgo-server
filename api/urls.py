from django.conf.urls import url
from mtsgo.tokenapi.decorators import token_required
from tokenapi.views import token
from mtsgo.tokenapi.views import token_new
from mtsgo.decorators import decode_json
from api import views

urlpatterns = [
    url(r'^auth/', decode_json(views.AuthView.as_view()), name="auth"),
    url(r'^auth/verify/(?P<token>.{24})/(?P<user>\d+).json$', token, name='auth_token_verify'),
    url(r'^position/', decode_json(token_required(views.UpdatePosition.as_view())), name='update_position'),
    url(r'^questions/$', views.Questions.as_view(), name='questions'),
    url(r'^questions/(?P<qid>\d+)/', views.Questions.as_view(), name='question_by_id'),
    url(r'^player/', decode_json(token_required(views.PlayerInfo.as_view())), name='player_info'),
    url(r'^history/', decode_json(token_required(views.PlayerHistory.as_view())), name='player_history')
]
