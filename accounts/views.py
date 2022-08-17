from . import models
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
import random
from django.db.models import Q
from librarian import models as lib_model
import pytz,datetime
import secrets
import bcrypt
from django.core.serializers import serialize
import jwt
from .tools import  code, decode, codetoken, decodetoken, get_user,create_coupon_code,beautify_errors

def login_provider(userid,token=''):
    token=codetoken(userid,type='librarian',token=token)
    return token
def logout_provider(token):
    try:
        data=decodetoken(token)
        uzr=list(models.libra_rian.objects.filter(id=data[1]))

        if uzr!=[]:
            uzr=uzr[0]
            uzr.token.token=''
            uzr.token.save()
            return True
        else:
            return False
    except Exception as e:
        return False

def login_consumer(userid,token=''):
    token=codetoken(userid,type='member',token=token)
    return token

def logout_consumer(token):
    try:
        data=decodetoken(token)
        uzr=list(models.libra_rian.objects.filter(id=data[1]))

        if uzr!=[]:
            uzr=uzr[0]
            uzr.token.token=''
            uzr.token.save()
            return True
        else:
            return False
    except Exception as e:
        return False

def login_not_required(*ag,**kg):
    def inner(func):
        def wrapper(*args,**kwargs):
            if 'HTTP_AUTHORIZATION'not in args[1].META :
                return func(*args,**kwargs)
            else:
                
                if args[1].META['HTTP_AUTHORIZATION']=='':
                    return func(*args,**kwargs)
                else:
                    return Response({'success':'false','error_msg':'USER IS LOGGEDIN','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                return Response({'success':'false','error_msg':'USER IS LOGGEDIN','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)

        return wrapper
    return inner

def login_required(*ag,**kg):
    def inner(func):
        def wrapper(*args,**kwargs):
            if 'HTTP_AUTHORIZATION'in args[1].META :
                try:
                    data=decodetoken(args[1].META['HTTP_AUTHORIZATION'])
                    time=datetime.datetime.strptime(data[2].split('.')[0],'%Y-%m-%d %H:%M:%S')
                except:
                    return Response({'success':'false','error_msg':'invalid token','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                if len(data)==4 and time>datetime.datetime.now():
                    uzr= get_user(*data)
                    if uzr!=[]:
                        if uzr.token.token=='':
                            return Response({'success':'false','error_msg':'USER NOT LOGGEDIN','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                        return func(*args,**kwargs)
                    else:
                        return Response({'success':'false','error_msg':'USER NOT LOGGEDIN','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                return Response({'success':'false','error_msg':'token expire','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'success':'false','error_msg':'no HTTP_AUTHORIZATION ','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
            return func(*args,**kwargs)
        return wrapper
    return inner

class login_labrarian_api(APIView):
    @login_not_required()
    def get(self,request):
        f1=serializers.userlogin()
        return Response(f1.data,status=status.HTTP_202_ACCEPTED)
    @login_not_required()
    def post(self,request):
        f1=serializers.userlogin(data=request.data)
        if (f1.is_valid()):
            user=list(models.libra_rian.objects.filter(username=request.POST['username']))
            print('jjjjjjjjjjjjjjjjjj')
            if user!=[]:
                user=user[0]
            else:
                return Response({'success':'false',
                                    'error_msg':'user_not_exists',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)

            password=str(request.POST['password']).encode('utf-8')
            hash_pass=user.password.encode('utf-8')
            if bcrypt.checkpw(password,hash_pass):
                sec=''
                for i in range(10):
                    sec+=secrets.choice(secrets.choice([chr(ii) for ii in range(45,123)]))

                user.token.token=sec
                user.last_login=datetime.datetime.now()
                user.token.save()
                re=login_provider(user.id,token=sec)
                return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{'user':serialize('json', [user])},
                                    'token':re,},status=status.HTTP_202_ACCEPTED)

            return Response({'success':'false',
                                'error_msg':'user_not_authenticated',
                                'response':{},
                                'errors':dict(f1.errors),

                                },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success':'false',
                                'error_msg':'log_in_parameters_not_correct',
                                'errors':dict(f1.errors),
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)

class logout_labrarian_api(APIView):
    @login_required()
    def get(self,request):
        val=logout_provider(request.META['HTTP_AUTHORIZATION'])
        if val:
            return Response({'success':'true',
            'error_msg':'',
            'response':{},},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'success':'false',
                                'error_msg':'Logout fail',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)

class signup_labrarian_api(APIView):
    def get(self,request):
        f0=serializers.password()
        f1=serializers.create_librarian_form()

        return Response({**f1.data,**f0.data
                            },status=status.HTTP_202_ACCEPTED)

    def post(self, request):
        f1=serializers.create_librarian_form(data=request.POST)
        f0=serializers.password()
        if f1.is_valid():
            
            check_list = list(models.libra_rian.objects.filter((Q(country_code=request.POST['country_code'])&Q(phone_number=request.POST['phone_number']))|
                                                                        Q(email=request.POST['email'])))
            del_acc=[]
            if check_list != []:
                for i in check_list:
                    if i.country_code==request.POST['country_code'] and i.phone_number==request.POST['phone_number']:
                        return Response({'success':'false',
                                        'error_msg':'This phone number already exists',
                                        'errors':{},
                                        'response':{},
                                        },status=status.HTTP_400_BAD_REQUEST)
                    elif i.email==request.POST['email']:
                        return Response({'success':'false',
                                        'error_msg':'This email already exists',
                                        'errors':{},
                                        'response':{},
                                        },status=status.HTTP_400_BAD_REQUEST)
                    else:
                        del_acc.append(i)
            if del_acc!=[]:
                for i in del_acc:
                    i.delete()
            sec=''
            for i in range(5):
                sec+=secrets.choice(secrets.choice([chr(ii) for ii in range(45,123)]))

            try:
                uzr=models.libra_rian()
                uzr.username=request.POST['username']
                uzr.email=request.POST['email']
                uzr.country_code=request.POST['country_code']
                uzr.phone_number=request.POST['phone_number']
                uzr.user_type=request.POST['user_type']
                uzr.otp=sec
                uzr.save()
                password=request.POST['password'].encode('utf-8')
                uzr.password=bcrypt.hashpw(password,bcrypt.gensalt())
                uzr.password=uzr.password.decode("utf-8")
                uzr.save()
                tem=lib_model.authorizations()
                tem.user=uzr
                tem.save()
                # tkn=account_models.admin_token()
                # tkn.admin=user
                # tkn.save()
                uzr_token=models.libra_rian_token(uzr=uzr,token=sec)
                uzr_token.save()
                return Response({'success':'True',
                                'error_msg':'',
                                'errors':{},
                                'response':'',
                                },status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'success':'false',
                                'error_msg':"Something Bad happened",
                                'errors':{},
                                'response':{str(e)},
                                },status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success':'false',
                                'error_msg':beautify_errors({**dict(f1.errors)}),
                                'errors':{**dict(f1.errors)},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)


    