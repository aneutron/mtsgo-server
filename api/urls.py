from django.conf.urls import url
from mtsgo.tokenapi.decorators import token_required
from mtsgo.decorators import try_decode_json
from api import views

urlpatterns = [
    url(r'^auth/new/', try_decode_json(views.AuthNewView.as_view()), name="auth"),
    url(r'^auth/$', try_decode_json(views.AuthView.as_view()), name="auth"),
    url(r'^position/', try_decode_json(token_required(views.UpdatePosition.as_view())), name='update_position'),
    url(r'^questions/$', try_decode_json(token_required(views.Questions.as_view())), name='questions'),
    url(r'^questions/(?P<qid>[0-9]+)/$', try_decode_json(token_required(views.Questions.as_view())), name='question_by_id'),
    url(r'^player/', try_decode_json(token_required(views.PlayerInfo.as_view())), name='player_info'),
    url(r'^history/', try_decode_json(token_required(views.PlayerHistory.as_view())), name='player_history')
]
