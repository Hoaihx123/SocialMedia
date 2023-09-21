from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('setting/', views.setting, name='setting'),
    path('upload', views.upload, name='upload'),
    path('like_post', views.like_post, name='like_post'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('follow/<str:username>', views.follow_index, name='follow_index'),
    path('delete_post/<str:user>/<str:post_id>', views.delect_post, name='delect_post'),
    path('search', views.search, name='search')
]
