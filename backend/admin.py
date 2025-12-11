from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Movies)
admin.site.register(UserProfile)
admin.site.register(Type)
admin.site.register(Cast)
admin.site.register(WatchHistory)
admin.site.register(Watchlist)