from django.urls import path
from . import views


app_name = "tube"
urlpatterns =[
    path('', views.index, name="index"),

    path('search/', views.search, name="search"),

    # TIPS:<型:変数名>とすることでビューに変数を与えることができる
    #idをuuidにするので、intをuuidに変える。

    path('single/<uuid:video_pk>/', views.single, name="single"),
    path('single_mod/<uuid:video_pk>/', views.single_mod, name="single_mod"),


    ##ランキングページ。DBからデータ抜き取って表示するだけ。GET文だけ
    path('rank/', views.rank, name="rank"),
    path('user_policy/', views.user_policy, name="user_policy"),

    # 以下認証済みユーザー専用
    path('video_comment_reply/<uuid:comment_pk>/', views.video_comment_reply, name="video_comment_reply"),
    path('video_comment_reply_to_reply/<uuid:videocommentreply_pk>/', views.video_comment_reply_to_reply,
         name="video_comment_reply_to_reply"),
    path('video_comment_edit/<uuid:comment_pk>/', views.video_comment_edit, name="video_comment_edit"),
    path('video_comment_reply_edit/<uuid:reply_pk>/', views.video_comment_reply_edit, name="video_comment_reply_edit"),
    path('video_comment_r_to_reply_edit/<uuid:r_to_reply_pk>/', views.video_comment_r_to_reply_edit,
         name="video_comment_r_to_reply_edit"),

    path('mypage/', views.mypage, name="mypage"),
    path('history/', views.history, name="history"),
    path('recommend/', views.recommend, name="recommend"),
    path('notify/', views.notify, name="notify"),
    path('mylist/', views.mylist, name="mylist"),
    path('upload', views.upload, name="upload"),
    path('config/', views.config, name="config"),
    path('report/<uuid:pk>/', views.report, name="report"),


    path('usersingle/<uuid:pk>/', views.usersingle, name="usersingle"),
    path('userfollow/<uuid:pk>/', views.userfollow, name="userfollow"),
    path('userblock/<uuid:pk>/', views.userblock, name="userblock"),
    path('useredit/<uuid:pk>/', views.useredit, name="useredit"),
]
