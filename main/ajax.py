from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from main.models import Player, Room, Stage, Ranking, Theme
import json
import time


def login_player(request):
    t = str(time.time())
    player_name = request.POST["player_name"]
    request.session["player_name"] = player_name
    request.session["mode"] = request.POST["mode"]
    request.session["room_id"] = None
    if request.POST["mode"] == "solo":
        player = Player(name=player_name, created_at=t)
        player.save()
        request.session["player_id"] = list(Player.objects.all().filter(
            created_at=t).values("id"))[0]["id"]
    elif request.POST["mode"] == "multi":
        room_name = request.POST["room_name"]
        room_id = list(Room.objects.all().filter(
            name=room_name).values())[0]["id"]
        room_num = list(Room.objects.all().filter(
            name=room_name).values())[0]["num"]
        player_num = len(
            list(Player.objects.all().filter(room_id=room_id).values()))
        if player_num >= room_num:
            return HttpResponse("false")
        request.session["room_id"] = room_id
        player = Player(name=player_name, created_at=t)
        player.save()
        request.session["player_id"] = list(Player.objects.all().filter(
            created_at=t).values("id"))[0]["id"]
        obj = Player.objects.get(id=request.session["player_id"])
        obj.room_id = room_id
        obj.save()
    # return HttpResponseRedirect("/mode/solo")
    return HttpResponse("true")


def view_login(request):
    room_name = request.POST["room_name"]
    room_id = Room.objects.all().filter(name=room_name).values()[0]["id"]
    request.session["room_id"] = room_id
    request.session["room_name"] = room_name
    print(room_name)
    print(room_id)
    return HttpResponse(True)


def logout_player(request):
    try:
        print("OKOKOK")
        player_id = request.POST["player_id"]
        mode = request.session["mode"]
        score = None
        if mode == "solo":
            player_info = Player.objects.all().filter(id=player_id).values()[0]
            score = player_info["score"]
            player_name = player_info["name"]
            ranking = Ranking(name1=player_name, score=score, mode=mode)
            ranking.save()
        else:
            room_id = request.session["room_id"]
            player_infos = list(Player.objects.all().filter(
                room_id=room_id).values())
            player_name = []
            score = 0
            for player_info in player_infos:
                player_name.append(player_info["name"])
                idx = player_info["id"]
                score += player_info["score"]
                obj = Player.objects.get(id=idx)
                obj.room_id = None
                obj.save()
            ranking = Ranking(name1=player_name[0],
                              name2=player_name[1], score=score, mode=mode)
            ranking.save()

        return HttpResponse(True)
    except:
        print("NONONO")
        return HttpResponse(True)


def create_theme(request):
    path = "main/all_theme.txt"
    f = open(path, "r", errors="ignore", encoding="utf-8")
    line = f.readline()
    while line:
        keyword = line.strip()
        print(keyword)
        check = list(Theme.objects.all().filter(name=keyword).values())
        if len(check) == 0:
            theme = Theme(name=keyword)
            theme.save()
        line = f.readline()
    f.close()
    HttpResponseRedirect("/")


def exit_room(request):
    player_id = request.session["player_id"]
    obj = Player.objects.get(id=player_id)
    obj.room_id = None
    obj.save()


def get_player_name(request):
    print("OKOKOKOKOKOKOKOKO")
    p1_id = request.POST["p1_id"]
    p2_id = request.POST["p2_id"]
    p1_name = Player.objects.all().filter(id=p1_id).values()[0]["name"]
    p2_name = Player.objects.all().filter(id=p2_id).values()[0]["name"]
    data = {"p1_name": p1_name, "p2_name": p2_name}
    print(data)
    return HttpResponse(json.dumps(data, ensure_ascii=False))


def get_score(request):
    score = 0
    p1_id = request.POST["p1_id"]
    p2_id = request.POST["p2_id"]
    p1_score = Player.objects.all().filter(id=p1_id).values()[0]["score"]
    p2_score = Player.objects.all().filter(id=p2_id).values()[0]["score"]
    score = p1_score+p2_score
    return HttpResponse(score)
