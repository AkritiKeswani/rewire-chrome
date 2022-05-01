from django.contrib import admin
from RewireApp.models import Participant, FriendRequest, Friend, Blocklist, Flow

# Register your models here.

admin.site.register(Participant)
admin.site.register(FriendRequest)
admin.site.register(Friend)
admin.site.register(Blocklist)
admin.site.register(Flow)
