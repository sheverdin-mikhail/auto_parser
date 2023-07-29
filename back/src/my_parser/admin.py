from email.parser import Parser
from django.contrib import admin

from .models import ParserInputFile, ParserTask, ParserFindItem, ParserOutputTask, ParserSite

admin.site.register(ParserInputFile)
admin.site.register(ParserTask)
admin.site.register(ParserFindItem)
admin.site.register(ParserOutputTask)
admin.site.register(ParserSite)