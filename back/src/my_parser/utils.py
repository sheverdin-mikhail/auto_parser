import src.my_parser.models as m

def firstParserSite():
    return m.ParserSite.objects.all().first()


