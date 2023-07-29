from .models import Proxy, SiteUser
from datetime import datetime
from src.my_parser.models import ParserSite


def getProxy():
    proxy = Proxy.objects.order_by("request_count").filter(status=True, isUsed=False).first()
    if(proxy):
        proxy.isUsed = True
        proxy.request_count = proxy.request_count + 1
        proxy.request_time = datetime.now()
        proxy.save()
        return {
            'https': f'{proxy.type}://{proxy.login}:{proxy.password}@{proxy.ip}:{proxy.port}',
            'http': f'{proxy.type}://{proxy.login}:{proxy.password}@{proxy.ip}:{proxy.port}'
        }
    else:
        return False
        
                


def getUser(site):
    site = ParserSite.objects.get(name=site)
    user = SiteUser.objects.order_by("?").filter(site=site).first()
    return {'login': user.login, 'password': user.password }
