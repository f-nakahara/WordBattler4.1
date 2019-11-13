from django.db import models

# Create your models here.


class Player(models.Model):
    name = models.CharField(max_length=20)  # 名前
    room_id = models.IntegerField(null=True, blank=True)  # 入室している部屋
    created_at = models.CharField(max_length=50)
    score = models.IntegerField(null=True, blank=True)  # 最終スコア

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=20, unique=True)  # 名前
    num = models.IntegerField()

    def __str__(self):
        return self.name


class Back(models.Model):
    name = models.CharField(max_length=20)  # 名前
    img = models.ImageField(upload_to="back")  # 背景

    def __str__(self):
        return self.name


class Stage(models.Model):
    id = models.IntegerField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20)
    enemy = models.ImageField(upload_to="enemy")  # 敵の画像
    hp = models.IntegerField()  # 敵の体力
    turn = models.IntegerField()  # ターン数
    time = models.IntegerField()  # 制限時間

    def __str__(self):
        return self.name


class Effect(models.Model):
    name = models.CharField(max_length=20)
    img = models.ImageField(upload_to="effect")  # 攻撃エフェクトgif
    level = models.IntegerField()  # エフェクトレベル（1～4）

    def __str__(self):
        return self.name


class Ranking(models.Model):
    mode = models.CharField(max_length=10)  # solo , multi
    name1 = models.CharField(max_length=20, null=True, blank=True)  # プレイヤー名1
    name2 = models.CharField(max_length=20, null=True, blank=True)  # プレイヤー名2
    score = models.IntegerField(null=True, blank=True)  # 記録
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.mode


class Theme(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
