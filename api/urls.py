from django.conf.urls import url
from tokenapi.decorators import token_required

from api import views

from tokenapi.views import token
from tokenapi.views import token_new

urlpatterns = [
    url(r'^auth$', token_new, name="auth_token_new"),
    url(r'^auth/verify/(?P<token>.{24})/(?P<user>\d+).json$', token, name='auth_token_verify'),
    url(r'^auth/new/', views.NewAccount.as_view(), name='auth_new_account'),
    url(r'^position/', token_required(views.UpdatePosition.as_view()), name='update_position'),
    url(r'^questions/', token_required(views.Questions.as_view()), name='questions'),
    url(r'^player/', token_required(views.PlayerInfo.as_view()), name='player_info'),
    url(r'^history/', token_required(views.PlayerHistory.as_view()), name='player_history')
]
