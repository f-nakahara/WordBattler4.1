from django.urls import path
from . import views, ajax

urlpatterns = [
    path("multi", views.player, name="player"),
    path("solo", views.player, name="player"),
    path("get_score", ajax.get_score, name="get_score"),
    path("get_player_name", ajax.get_player_name, name="get_player_name"),
    path("exit_room", ajax.exit_room, name="exit_room"),
    path("create_theme", ajax.create_theme, name="create_theme"),
    path("logout_player", ajax.logout_player, name="logout_player"),
    path("login_player", ajax.login_player, name="login_player"),
    path("view_login", ajax.view_login, name="view_login"),
    path('view', views.view, name='view'),
    path('ranking', views.ranking, name='ranking'),
    path('', views.index, name='index'),
]
