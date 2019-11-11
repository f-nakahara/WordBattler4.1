from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from main.models import Player, Room, Ranking
from django.utils.safestring import mark_safe
# Create your views here.
import json


def index(request):
    return render(request, "main/index.html", {})


def player(request):
    player_name = request.session["player_name"]
    player_id = request.session["player_id"]
    room_id = request.session["room_id"]
    mode = "協力モード"
    player_id = request.session["player_id"]
    if request.session["mode"] == "solo":
        mode = "ソロモード"
    else:
        obj = Player.objects.get(id=player_id)
        obj.room_id = room_id
        obj.save()

    return render(request, "main/player.html", {"player_name": player_name, "mode": mode, "player_id": player_id, "room_id": room_id})


def view(request):
    room_id = request.session["room_id"]
    mode = "観戦モード"
    room_name = request.session["room_name"]
    return render(request, "main/view.html", {"mode": mode, "room_id": room_id, "room_name": room_name})


def ranking(request):
    # ソロ用
    solo_info = list(Ranking.objects.all(
    ).values().order_by("score").reverse())
    solo_lists = []
    rank = 1
    for i in solo_info:
        if i["score"] != None and i["mode"] == "solo":
            solo_lists.append([i["name1"], i["score"], i["created_at"], rank])
            rank += 1
    print(solo_lists)
    solo_length = len(solo_lists)

    # マルチ用
    multi_info = list(Ranking.objects.all(
    ).values().order_by("score").reverse())
    multi_lists = []
    rank = 1
    for i in multi_info:
        if i["score"] != None and i["mode"] == "multi":
            multi_lists.append(
                [i["name1"], i["name2"], i["score"], i["created_at"], rank])
            rank += 1
    print(multi_lists)
    multi_length = len(multi_lists)
    return render(request, "main/ranking.html", {"solo_lists": solo_lists, "solo_length": solo_length, "multi_lists": multi_lists, "multi_length": multi_length})
