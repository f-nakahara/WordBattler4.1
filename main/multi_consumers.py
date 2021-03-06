from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from main.models import Player, Room, Stage, Ranking, Theme, Back, Effect
import random
from gensim.models import word2vec
from threading import Thread
import time
import copy


class ChatConsumer(WebsocketConsumer):
    # word2vecのクラス
    class W2V():
        def __init__(self):
            self.model = word2vec.Word2Vec.load("main/model/wiki.model")

        def cal(self, thema="", word=""):
            try:
                self.results = self.model.wv.similarity(thema, word)
                return self.results
            except:
                self.results = 0
                return self.results
    my_id = None
    player_id1 = None
    player_id2 = None
    stage_id = 1
    write_id = None
    flag = False
    enemy_img = None
    enemy_hp = None
    back_img = None
    term = None
    text = None
    mode = None
    input_word = None
    damage = None
    score = 0
    effect = None
    before_theme = None
    theme = {}
    game = False
    theme_list = list(Theme.objects.all().values("name"))
    theme_list2 = copy.deepcopy(theme_list)
    # print(theme_list)
    model = W2V()
    time_limit = 0

    def init(self):
        self.flag = False
        effect = random.choice(
            list(Effect.objects.all().filter(level=5).values()))
        self.effect = effect["img"]
        self.enemy_img = Stage.objects.all().filter(
            id=self.stage_id).values()[0]["enemy"]
        print("敵画像のパス：" + self.enemy_img)
        self.back_img = random.choice(list(Back.objects.all().values()))["img"]
        print("背景のパス：" + self.back_img)
        self.enemy_hp = Stage.objects.all().filter(
            id=self.stage_id).values()[0]["hp"]
        print("敵の体力：" + str(self.enemy_hp))
        term = []
        term.append(str(int(Stage.objects.all().filter(
            id=self.stage_id).values()[0]["time"]/1.7))+"秒")
        term.append(str(Stage.objects.all().filter(
            id=self.stage_id).values()[0]["turn"])+"回")
        self.term = random.choice(term)
        print("条件：" + str(self.term))
        if len(self.theme_list) < 10:
            self.theme_list = copy.deepcopy(self.theme_list2)
        theme = random.choice(self.theme_list)
        self.theme[str(self.player_id1)] = theme["name"]
        theme = random.choice(self.theme_list)
        self.theme[str(self.player_id2)] = theme["name"]
        print("お題："+str(self.theme))
        self.mode = "init"
        self.text = "敵画像をセットしました。"
        if "秒" in self.term:
            self.time_limit = int(self.term.split("秒")[0])
            self.threads = Thread(target=self.cal_time)
            self.threads.start()

    def cal_time(self):
        self.time_limit = int(self.time_limit)
        while self.time_limit >= 0 and not self.flag:
            time.sleep(1)
            self.term = str(self.time_limit) + "秒"
            self.time_limit -= 1
            self.mode = "time"
            data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                    "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme, "my_id": self.my_id}
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "data": data
                }
            )
        if not self.flag:
            print("ゲームオーバーの方")
            self.mode = "end"
            self.record_score()
        else:
            print("ゲームクリアの方")
            self.mode = "clear"
            self.record_score()
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme, "my_id": self.my_id}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                "data": data
            }
        )

    def connect(self):
        print(self.scope)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'solo_%d' % self.room_id
        print(self.room_group_name)
        players = list(Player.objects.all().filter(
            room_id=self.room_id).values())
        print(players)
        if len(players) >= 2:
            self.player_id1 = players[0]["id"]
            self.player_id2 = players[1]["id"]
        print(self.player_id1, self.player_id2)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        if self.player_id1 != None and self.player_id2 != None:
            print("ルームID："+str(self.room_id))
            self.stage_id = 1
            print("ステージID："+str(self.stage_id))
            self.init()

            self.back_img = "back/sougen.png"
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme, "my_id": self.my_id, "effect": self.effect, "stage_id": self.stage_id}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                "data": data
            }
        )

    def disconnect(self, close_code):
        # Leave room group
        self.time_limit = 0
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    # Receive message from WebSocket

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.my_id = text_data_json["player_id"]
        print(text_data_json)
        if text_data_json["mode"] == "clear":
            print("ゲームをクリアしました")
            self.mode = "clear"
            self.flag = True
            self.record_score()
        elif text_data_json["mode"] == "end":
            print("ゲームオーバーになりました。")
            self.mode = "end"
            self.record_score()
        elif text_data_json["mode"] == "play":
            self.before_theme = self.theme[str(text_data_json["player_id"])]
            if len(self.theme_list) < 10:
                self.theme_list = copy.deepcopy(self.theme_list2)
            theme = random.choice(self.theme_list)
            self.theme[str(text_data_json["player_id"])] = theme["name"]
            damage = int(self.model.cal(
                text_data_json["word"][1], text_data_json["word"][0]) * 100)
            if damage >= 60:
                effect = random.choice(
                    list(Effect.objects.all().filter(level=2).values()))
            elif damage > 0:
                effect = random.choice(
                    list(Effect.objects.all().filter(level=1).values()))
            elif damage == 0:
                effect = random.choice(
                    list(Effect.objects.all().filter(level=4).values()))
            elif damage < 0:
                effect = random.choice(
                    list(Effect.objects.all().filter(level=3).values()))
            self.effect = effect["img"]
            self.input_word = text_data_json["word"][0]
            self.write_id = text_data_json["player_id"]
            print("敵に与えたダメージ：" + str(damage))
            print("敵の体力：" + str(self.enemy_hp))
            self.damage = damage
            self.score += damage
            self.mode = "play"
        elif text_data_json["mode"] == "next_stage":
            self.stage_id += 1
            self.init()
        # Send message to room group
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme, "my_id": self.my_id, "effect": self.effect, "stage_id": self.stage_id}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'data': data
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        print(self.my_id)
        print(event)
        data = event["data"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))

    def record_score(self):
        obj = Player.objects.get(id=self.my_id)
        obj.score = self.score
        obj.save()
