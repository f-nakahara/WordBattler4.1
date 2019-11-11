from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from main.models import Player, Room, Stage, Ranking, Theme, Back
import random
from gensim.models import word2vec
from threading import Thread
import time


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

    player_id1 = None
    player_id2 = None
    stage_id = None
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
    before_theme = None
    theme = {}
    theme_list = list(Theme.objects.all().values("name"))
    # print(theme_list)
    model = W2V()
    time_limit = 0

    def init(self):
        self.flag = False
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
        self.theme[str(self.player_id1)] = random.choice(
            self.theme_list)["name"]
        self.theme[str(self.player_id2)] = random.choice(
            self.theme_list)["name"]
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
                    "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme}
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
        else:
            print("ゲームクリアの方")
            self.mode = "clear"
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme}
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

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                "data": data
            }
        )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    # Receive message from WebSocket

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        if text_data_json["mode"] == "play":
            self.before_theme = self.theme[str(text_data_json["player_id"])]
            self.theme[str(text_data_json["player_id"])] = random.choice(
                self.theme_list)["name"]
            damage = int(self.model.cal(
                text_data_json["word"][1], text_data_json["word"][0]) * 100)
            self.input_word = text_data_json["word"][0]
            self.enemy_hp -= damage
            self.write_id = text_data_json["player_id"]
            print("敵に与えたダメージ：" + str(damage))
            print("敵の体力：" + str(self.enemy_hp))
            self.damage = damage
            self.score += damage
            self.mode = "play"
            if self.enemy_hp <= 0:
                self.enemy_hp = 0
                self.mode = "clear"
                self.flag = True
                self.score += self.stage_id * 20
                self.record_score()
            if "回" in self.term:
                turn = int(self.term.split("回")[0]) - 1
                if turn <= 0 and self.enemy_hp != 0:
                    print("ゲームオーバー")
                    self.mode = "end"
                    self.record_score()
                self.term = str(turn) + "回"
        elif text_data_json["mode"] == "next_stage":
            self.stage_id += 1
            self.init()
        # Send message to room group
        data = {"enemy_img": self.enemy_img, "enemy_hp": self.enemy_hp,
                "term": self.term, "mode": self.mode, "text": self.text, "damage": self.damage, "score": self.score, "theme": self.theme, "back": self.back_img, "p1_id": self.player_id1, "p2_id": self.player_id2, "write_id": self.write_id, "input_word": self.input_word, "before_theme": self.before_theme}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'data': data
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        print(event)
        data = event["data"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))
