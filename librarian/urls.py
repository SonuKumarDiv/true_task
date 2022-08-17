from django.urls import path, re_path
from . import views
app_name='lib_dash'

urlpatterns = [
    path('lib_dash/book_data',views.my_book.as_view(),name='book_data'),
    path('lib_dash/my_book_data-<id>',views.my_book_urd.as_view(),name='book_data'),
    path('lib_dash/edit_member_user-<id>',views.edit_member_by_labrarian.as_view(),name='edit_member_user-<id>'),
    path('lib_dash/add_member_user',views.add_member_api_by_librarian.as_view(),name='edit_member_user-<id>'),
    path('lib_dash/del_member_user-<id>',views.delete_member_from_labrarian.as_view(),name='edit_member_user-<id>'),
    path('lib_dash/get_member_user',views.get_all_member.as_view(),name='edit_member_user-<id>'),
    path('lib_dash/show_book',views.get_member_own_book_detail.as_view(),name='book_data'),
    path('lib_dash/del_account-<id>',views.delete_account.as_view(),name='book_data'),
    path('lib_dash/return_book',views.book_return_from_member.as_view(),name='edit_member_user-<id>'),
    path('lib_dash/barrow_book',views.barrow_member_book.as_view(),name='edit_member_user-<id>')
    
    
]

