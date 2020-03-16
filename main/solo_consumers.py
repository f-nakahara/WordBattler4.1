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

    player_id = None
    stage_id = 1
    flag = False
    enemy_img = None
    enemy_hp = None
    back_img = None
    term = None
    text = None
    damage = None
    score = 0
    theme = None
    effect = None
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
        term.append(str(Stage.objects.all().filter(
            id=self.stage_id).values()[0]["time"])+"秒")
        term.append(str(Stage.objects.all().filter(
            id=self.stage_id).values()[0]["turn"])+"回")
        self.term = random.choice(term)
        print("条件：" + str(self.term))
        if len(self.theme_list) < 10:
            self.theme_list = copy.deepcopy(self.theme_list2)
        theme = random.choice(self.theme_list)
        self.theme = theme["name"]
        self.theme_list.remove(theme)

        print("お題："+self.theme)
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
                    "term": self.term, "mode": "time", "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img}
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
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                "data": data
            }
        )

    def connect(self):
        print(self.scope)
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.room_group_name = 'solo_%d' % self.player_id
        print(self.room_group_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        print("プレイヤーID："+str(self.player_id))
        self.stage_id = 1
        print("ステージID："+str(self.stage_id))
        self.init()
        print(self.theme_list)
        self.back_img = "back/sougen.png"
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "effect": self.effect, "stage_id": self.stage_id}
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
            if len(self.theme_list) < 10:
                self.theme_list = copy.deepcopy(self.theme_list2)
            theme = random.choice(self.theme_list)
            self.theme = theme["name"]
            self.theme_list.remove(theme)
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
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "effect": self.effect, "stage_id": self.stage_id}
        print("メッセージを送信しました")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'data': data
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        print("メッセージを受信")
        print(event)
        data = event["data"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))

    def record_score(self):
        obj = Player.objects.get(id=self.player_id)
        obj.score = self.score
        obj.save()
