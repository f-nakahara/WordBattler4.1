from django.contrib import admin
from .models import Player, Room, Back, Stage, Ranking, Theme, Effect

# Register your models here.

admin.site.register(Player)
admin.site.register(Room)
admin.site.register(Stage)
admin.site.register(Effect)
admin.site.register(Back)
admin.site.register(Ranking)
admin.site.register(Theme)
