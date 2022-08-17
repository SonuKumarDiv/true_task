import email
from django.shortcuts import render
from accounts import serializers as ac_serializers
from accounts import models as ac_models
from librarian import serializers as lib_serializers
#from accounts import models as ac_models
from librarian import models as lib_models
from . import models 
from . import serializers
from django.db.models import Q
import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.serializers import serialize
import secrets
from accounts.tools import  code, decode, codetoken, decodetoken, get_user,create_coupon_code,beautify_errors

#from librarian.tools import code, decode, codetoken, decodetoken, get_user
import datetime,pytz
from itertools import chain
import time
import jwt
#from jose import jwt
from django.http import HttpResponse
from django.core.mail import send_mail

def is_authenticate(*Dargs,**Dkwargs):
    def inner(fun):
        def wrapper(*args,**kwargs):
            if 'HTTP_AUTHORIZATION'in args[1].META :
                try:
                    data=decodetoken(args[1].META['HTTP_AUTHORIZATION'])
                    time=datetime.datetime.strptime(data[2].split('.')[0],'%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    return Response({'success':'false','error_msg':'invalid token','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)

                if len(data)==4 and time>datetime.datetime.now():
                    uzr= get_user(*data)
                    if uzr!=[]:
                        if uzr.is_user_blocked :
                            return Response({'success':'false','error_msg':'USER BLOCKED','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                        if uzr.is_active==False:
                            return Response({'success':'false','error_msg':'USER DEACTIVATED','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                        return fun(*args,**kwargs)
                    else:
                        return Response({'success':'false','error_msg':'USER NOT LOGGEDIN','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
                return Response({'success':'false','error_msg':'token expire','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'success':'false','error_msg':'no HTTP_AUTHORIZATION ','errors':{},'response':{}},status=status.HTTP_401_UNAUTHORIZED)
            # return fun(*args,**kwargs)
        return wrapper
    return inner

@is_authenticate()
def get_JWT(request):
    data=decodetoken(request.META['HTTP_AUTHORIZATION'])
    requstuser=get_user(*data)
    payload = {
        'name': requstuser.first_name,
        'email': requstuser.email,
        'iat': int(time.time()), 
        'external_id': "pro-"+requstuser.id,
        'exp': int(time.time()) + 3000
        }
    token = jwt.encode(payload, 'C47D02EDD664451E50C908A3FFE36D3A6978953A41418D012B8B656370D05168')
    return HttpResponse(token, content_type="text/plain")


class my_book(APIView):
    @is_authenticate(view_book=True)
    def get(self,request):
        result= models.Book_detail.objects.all()
        return Response({'success':'true',
                        'error_msg':'',
                        'errors':{},
                        'response':serializers.book_forms(result,many=True).data

                        },status=status.HTTP_202_ACCEPTED)
                        
    @is_authenticate(add_book=True)
    def post(self,request):
        f1=serializers.book_forms(data=request.POST)
        if f1.is_valid():
            print('llllllllllllllll')
            f1.save()
            return Response({'success':'true',
                                'error_msg':'',
                                'errors':{},
                                'response':'',
                                },status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'success':'false',
                                'error_msg':'invalid_input',
                                'errors':{},
                                'response':{**dict(f1.errors)}},
                                status=status.HTTP_400_BAD_REQUEST)

class my_book_urd(APIView):
    @is_authenticate(manage_book=True)
    def get(self,request,id):
        vechicle=list(models.Book_detail.objects.filter(id=id))
        if vechicle==[]:
            return Response({'success':'false',
                                'error_msg':'invalid id',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)
        vechicle=vechicle[0]
        return Response({'success':'true',
                    'error_msg':'',
                    'errors':{},
                    'response':serializers.book__forms(vechicle).data,
                    },status=status.HTTP_202_ACCEPTED)#

    @is_authenticate(manage_book=True)
    def put(self,request,id):
        vechicle=list(models.Book_detail.objects.filter(id=id))
        if vechicle==[]:
            return Response({'success':'false',
                                'error_msg':'invalid id',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)
        vechicle=vechicle[0]
        f1=serializers.book_forms(data=request.POST,instance=vechicle)
        if f1.is_valid():
            vechicle=f1.save()
            return Response({'success':'true',
                        'error_msg':'',
                        'errors':{},
                        'response':serializers.book_forms(vechicle).data,
                        },status=status.HTTP_202_ACCEPTED)#
        else:
            return Response({'success':'false',
                                'error_msg':'invalid_input',
                                'errors':{},
                                'response':{**dict(f1.errors),
                                }},status=status.HTTP_400_BAD_REQUEST)

    @is_authenticate(remove_book=True)
    def delete(self,request,id):
        vechicle=list(models.Book_detail.objects.filter(id=id))
        if vechicle==[]:
            return Response({'success':'false',
                                'error_msg':'invalid id',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)
        vechicle=vechicle[0]
        vechicle.delete()
        return Response({'success':'true',
                    'error_msg':'',
                    'errors':{},
                    'response':serializers.book_forms(vechicle).data,
                    },status=status.HTTP_202_ACCEPTED)#

class add_member_api_by_librarian(APIView):
    @is_authenticate(add_member=True)
    def get(self,request):
        f0=serializers.password()
        f1=ac_serializers.create_member_form()

        return Response({**f1.data,**f0.data
                            },status=status.HTTP_202_ACCEPTED)
    @is_authenticate(add_member=True)
    def post(self, request):
        f1=ac_serializers.create_librarian_form(data=request.POST)
        if f1.is_valid():
            check_list = list(ac_models.libra_rian.objects.filter((Q(country_code=request.POST['country_code'])&Q(phone_number=request.POST['phone_number']))|
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
            print('lllll',check_list)
            try:
                uzr=ac_models.libra_rian()
                uzr.username=request.POST['username']
                uzr.email=request.POST['email']
                uzr.country_code=request.POST['country_code']
                uzr.phone_number=request.POST['phone_number']
                uzr.user_type=request.POST['user_type']
                uzr.otp=sec
                uzr.is_verified=True
                password=request.POST['password'].encode('utf-8')
                uzr.password=bcrypt.hashpw(password,bcrypt.gensalt())
                uzr.password=uzr.password.decode("utf-8")
                uzr.save()
                tem=models.authorizations()
                tem.user=uzr
                tem.save()
                uzr_token=ac_models.libra_rian_token(uzr=uzr,token=sec)
                uzr_token.save()
                return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_202_ACCEPTED)
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

class edit_member_by_labrarian(APIView):
    @is_authenticate(edit_provider =True,)
    def get(self,request,id):
        try:
            user=list(ac_models.libra_rian.objects.filter(id=id))
            if user!=[]:
                user=user[0]
                return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{'user':[ac_serializers.member_forms(user).data]},
                                    },status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'success':'false',
                                    'error_msg':'user_not_exist',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'success':'false',
                            'error_msg':' invalid id',
                            'errors':{},
                            'response':{},
                            },status=status.HTTP_400_BAD_REQUEST)


    @is_authenticate(update=True)
    def post(self,request,id):
        
        user=list(ac_models.libra_rian.objects.filter(id=id))
        x=(Q(country_code=request.data['country_code'])&Q(phone_number=request.data['phone_number']))&~Q(email=email)
        subadmin=list(ac_models.libra_rian.objects.filter(x))
        if user!=[]:
            user=user[0]
            tem_user={**user.__dict__}
            if subadmin!=[]:
                return Response({'success':'false',
                                'error_msg':'phone number already exist',
                                'errors':'',
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST) 
            f1=serializers.member_forms(data=request.POST,instance=user)
            if f1.is_valid():
                uzr=f1.save()
                uzr.save()
                return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_202_ACCEPTED)
            else:
                f1.is_valid()
                return Response({'success':'false',
                                    'error_msg':beautify_errors({**dict(f1.errors)}),
                                    'errors':{**dict(f1.errors)},
                                    'response':{},

                                    },status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'success':'false',
                                'error_msg':'user_not_exis',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_400_BAD_REQUEST)

class delete_member_from_labrarian(APIView):
    @is_authenticate(delete_member=True,)
    def delete(self,request,id):
        try:
            
            user=list(ac_models.libra_rian.objects.filter(id=id))
            if user==[]:
                return Response({'success':'false',
                                    'error_msg':'invalid ID',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)
            user=user[0]
            user.delete()
            return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_200_OK)
        except:
            return Response({'success':'false',
                                'error_msg':'',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_200_OK)

class get_all_member(APIView):
    @is_authenticate(view_member=True)
    def get(self,request):
        result= ac_models.libra_rian.objects.all()
        return Response({'success':'true',
                        'error_msg':'',
                        'errors':{},
                        'response':ac_serializers.member_forms(result,many=True).data

                        },status=status.HTTP_202_ACCEPTED)
            
class get_member_own_book_detail(APIView):
    @is_authenticate(view_member=True)
    def post(self, request):
        data=decodetoken(request.META['HTTP_AUTHORIZATION'])
        requstuser=get_user(*data)
        provider=list(lib_models.Book_detail.objects.filter(book_used_by=requstuser))
        if provider==[]:
            return Response({'success':'false',
                    'error_msg':"Member noy book issu",
                    'errors':{},
                    'response':{}
                    },status=status.HTTP_400_BAD_REQUEST) 
        f1=lib_serializers.book__forms(provider[0])     
        return Response({'success':'true',
                    'error_msg':'',
                    'errors':{},
                    'response':{"provider_data":f1.data}
                    },status=status.HTTP_200_OK)

class book_return_from_member(APIView):
    @is_authenticate(return_book=True)
    def put(self,request):
        try:
            book=lib_models.Book_detail.objects.get(id=int(request.POST["book_id"]))
            member=ac_models.libra_rian.objects.get(id=int(request.POST["member_id"]))
            member_books=lib_models.Book_detail.objects.filter(book_used_by=int(request.POST["member_id"]))
            print('hhhhhh',member_books,'gggggggggggggggggg',book,member)
            if book in member_books:
                book.book_used_by.remove(member)
                book.status='AVAILABLE'
                book.save()
                return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':serializers.book(book).data
                                    },status=status.HTTP_200_OK)
            return Response({'success':'false',
                                    'error_msg':'book is not linked with member',
                                    'errors':{},
                                    'response':{}
                                    },status=status.HTTP_200_OK)
       
        except:
            return Response({'success':'false',
                                    'error_msg':'book id and member id does not exist',
                                    'errors':{},
                                    'response':{}
                                    },status=status.HTTP_200_OK)

class barrow_member_book(APIView):
    @is_authenticate(barrow_book=True)
    def post(self,request):
        f1=lib_serializers.booking(data=request.POST)
        if f1.is_valid():
            result=lib_models.Book_detail.objects.get(id=int(request.POST["book_data"]))
            uzr_id=request.POST['user_id']
            uzr=list(ac_models.libra_rian.objects.filter(id=uzr_id))
            if uzr==[]:
                return Response({'success':'false',
                                    'error_msg':'invalid user id',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)
            uzr=uzr[0]
            if result==[]:
                return Response({'success':'false',
                                    'error_msg':'invalid book id',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)
            result=lib_models.Book_detail.objects.get(pk=int(request.POST["book_data"]))
            uzr=ac_models.libra_rian.objects.get(pk=int(request.POST["user_id"]))
           
            exist = list(result.book_used_by.all())
            if(uzr in exist):
                return Response({'success':'false',
                                'error_msg':"book alrady issu from this member",
                                'errors':{},
                                'response':{}
                                },status=status.HTTP_400_BAD_REQUEST) 
            print('gggggggggggggggg',result)
            result.book_used_by.add(uzr)
            result.book_issue_date=datetime.datetime.strptime(request.POST['book_issue_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)
            result.book_returned_date=datetime.datetime.strptime(request.POST['book_returned_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)
            result.status='BORROWED'
            result.save()

            return Response({'success':'true',
                            'error_msg':'',
                            'errors':{},
                            'response':serializers.book(result).data,
                            },status=status.HTTP_202_ACCEPTED)#
            
        else:
            return Response({'success':'false',
                                'error_msg':'invalid_input',
                                'errors':{},
                                'response':{**dict(f1.errors)},
                                },status=status.HTTP_400_BAD_REQUEST)

class delete_account(APIView):
    @is_authenticate(delete_member=True)
    def delete(self,request,id):
        try:
            user=list(ac_models.libra_rian.objects.filter(id=id))
            if user==[]:
                return Response({'success':'false',
                                    'error_msg':'invalid ID',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_400_BAD_REQUEST)
            user=user[0]
            user.delete()
            return Response({'success':'true',
                                    'error_msg':'',
                                    'errors':{},
                                    'response':{},
                                    },status=status.HTTP_200_OK)
        except:
            return Response({'success':'false',
                                'error_msg':'',
                                'errors':{},
                                'response':{},
                                },status=status.HTTP_200_OK)
        