from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from . import models
#from . import forms
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
import random
from django.contrib.auth import login,logout,authenticate
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect
from twilio.rest import Client
from django.db.models import Q
from django.conf import settings

from django.forms.models import model_to_dict
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
import pytz,datetime
from django.views.decorators.csrf import ensure_csrf_cookie
import secrets
import math
import bcrypt
from google.auth.transport import requests
from google.oauth2 import id_token
def create_coupon_code(instance):
    print(instance.id)
    s=''
    for i in range(7):
        s+= secrets.choice([secrets.choice([chr(ii) for ii in range(48,57)]),secrets.choice([chr(ii) for ii in range(97,122)])])
    return str(instance.id)+s


def code(data):
    def code_(num):
        key=[
        ['x', 'K', '7', 'A', 'Z', '-'],
        ['U', 'd', 'B', 'w', 'i', 'C'],
        ['y', 'J', 'V', 'e', 'o', '1'],
        ['m', '_', 'f', '.', 'F', '2'],
        ['Y', 'D', 'E', 'r', 'T', '~'],
        ['t', 'O', 'z', 's', 'b', '5'],
        ['j', 'h', 'H', 'L', 'P', '3'],
        ['G', 'p', 'u', '8', 'N', 'I'],
        ['R', '0', 'l', '6', 'v', 'q'],
        ['W', 'Q', 'M', 'k', 'n', 'g']]
        ln=10
        s=[]
        while True:
            if num<=1:
                s.append(key[num][random.randint(0,5)])
                break
            t1=num//ln
            a=num%ln
            s.append(key[a][random.randint(0,5)])
            num=t1
        e=''
        for i in s[::-1]:
           e+=i
        return e
    spacer=['a', 'X', '4', 'S', 'c', '9']
    s=''
    for i in str(data):
        s+=code_(ord(i))+spacer[random.randint(0,5)]
    print(s)
    return s


def decode(data):
    key={'x': 0, 'K': 0, '7': 0, 'A': 0, 'Z': 0, '-': 0, 'U': 1, 'd': 1, 'B': 1, 'w': 1, 'i': 1, 'C': 1, 'y': 2, 'J': 2, 'V': 2, 'e': 2, 'o': 2, '1': 2, 'm': 3, '_': 3, 'f': 3, '.': 3, 'F': 3, '2': 3, 'Y': 4, 'D': 4, 'E': 4, 'r': 4, 'T': 4, '~': 4, 't': 5, 'O': 5, 'z': 5, 's': 5, 'b': 5, '5': 5, 'j': 6, 'h': 6, 'H': 6, 'L': 6, 'P': 6, '3': 6, 'G': 7, 'p': 7, 'u': 7, '8': 7, 'N': 7, 'I': 7, 'R': 8, '0': 8, 'l': 8, '6': 8, 'v': 8, 'q': 8, 'W': 9, 'Q': 9, 'M': 9, 'k': 9, 'n': 9, 'g': 9}
    spacer=['a', 'X', '4', 'S', 'c', '9']
    ln=10
    for i in spacer:
        data=data.replace(i,'#')
    data=data[:len(data)-1].split('#')
    op=''
    for i in data:
        l=0
        g=0
        for k in list(i)[::-1]:
           l+=key[k]*(ln**g)
           g+=1
        op+=chr(l)
    print(op)
    return(op)

def codetoken(id,type='User',time=1,token=''):
    return code(type+'='+code(str(id))+','+
        str(datetime.datetime.now(tz=pytz.UTC)+datetime.timedelta(days=time))+','+token)

def decodetoken(data):

    r= decode(data).split(',')
    print(r)
    r[0]=r[0].split('=')
    r[0][1]=decode(r[0][1])
    return [*r[0],r[1],r[2]]

def get_user(usertype,id,time,token):
    if usertype=='member':
        user=list(models.Member.objects.filter(id=id))
        if user!=[]:
            user=user[0]
            if user.token.token==token:
                return user
            else:
                return []
        else:
            return []
    elif usertype=='librarian':
        user=list(models.libra_rian.objects.filter(id=id))
        if user!=[]:
            user=user[0]
            if user.token.token==token:
                return user
            else:
                return []
        else:
            return []
    

def get_base64_to_img(image_data):
    formats, imgstr = image_data.split(';base64,')
    ext = formats.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr))
    return( data,ext)

def beautify_variable(s):
    return s.replace('_',' ').capitalize()
def beautify_errors(*args):
    s=''
    for i in args:
        for k in i:
            s+=beautify_variable(k)+' : '+i[k][0]+'\n'
    return s
def distance(origin, destination):

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def give_range_block(lat,long,radious=1):#miles
    a=distance((lat, long),(lat+1, long))
    b=distance((lat, long),(lat, long+1))
    unit_a=1/a
    unit_b=1/b
    # print(a,b)
    # print(unit_a,unit_b)
    # print(unit_a*10,unit_b*10)
    # print(lat+unit_a*(radious*1.60934),long+unit_b*(radious*1.60934))
    return ([lat-unit_a*(radious*1.60934),long-unit_b*(radious*1.60934)],
            [lat+unit_a*(radious*1.60934),long+unit_b*(radious*1.60934)]
        )
def is_in_ellips(x,y,cx,cy,a,b):
    a=((x-cx)**2/a**2)+((y-cy)**2/a**2)
    if a<=1:
        return True
    else:
        return False

def get_range_box(lat,long,zoom_level,width_in_px):
    area={'0': [59959.436, 29979.718, 14989.859, 7494.929, 3747.465, 1873.732, 936.866, 468.433, 234.217, 117.108, 58.554, 29.277, 14.639, 7.319, 3.66, 1.83, 0.915, 0.457, 0.229, 0.114, 0.057, 0.029, 0.014], '20': [78271.484, 39135.742, 19567.871, 9783.936, 4891.968, 2445.984, 1222.992, 611.496, 305.748, 152.874, 76.437, 38.218, 19.109, 9.555, 4.777, 2.389, 1.194, 0.597, 0.299, 0.149, 0.075, 0.037, 0.019], '40': [73551.136, 36775.568, 18387.784, 9193.892, 4596.946, 2298.473, 1149.237, 574.618, 287.309, 143.655, 71.827, 35.914, 17.957, 8.978, 4.489, 2.245, 1.122, 0.561, 0.281, 0.14, 0.07, 0.035, 0.018], '60': [39135.742, 19567.871, 9783.936, 4891.968, 2445.984, 1222.992, 611.496, 305.748, 152.874, 76.437, 38.218, 19.109, 9.555, 4.777, 2.389, 1.194, 0.597, 0.299, 0.149, 0.075, 0.037, 0.019, 0.009], '80': [13591.701, 6795.85, 3397.925, 1698.963, 849.481, 424.741, 212.37, 106.185, 53.093, 26.546, 13.273, 6.637, 3.318, 1.659, 0.83, 0.415, 0.207, 0.104, 0.052, 0.026, 0.013, 0.006, 0.003]}
    if '-' in str(lat):
        com_lat=str(lat)[1:]
    else:
        com_lat=str(lat)
    if com_lat>=0 and com_lat<20:
        side=((area['0'][zoom_level]*width_in_px)/111000)/2
    return [(lat-com_lat,long-com_lat),(lat+com_lat,long+com_lat)]
