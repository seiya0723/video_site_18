from rest_framework import status,views,response

from django.shortcuts import render, redirect

from django.db.models import Q,Count

from django.http.response import JsonResponse

from django.template.loader import render_to_string

from django.core.paginator import Paginator

from django.conf import settings

#TIPS:ログイン状態かチェックする。ビュークラスに継承元として指定する(多重継承なので順番に注意)。未ログインであればログインページへリダイレクト。
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import Video,VideoCategory,VideoComment,VideoCommentReply,VideoCommentReplyToReply,MyList,History,GoodVideo,NotifyTarget,Notify,ReportCategory,Report,UserPolicy

from users.models import CustomUser,FollowUser,BlockUser

from .serializer import VideoSerializer,VideoEditSerializer,VideoCommentSerializer,VideoCommentEditSerializer,VideoCommentReplyEditSerializer,VideoCommentReplyToReplyEditSerializer,VideoCommentReplySerializer,VideoCommentReplyToReplySerializer,MyListSerializer,HistorySerializer,RateSerializer,GoodSerializer,IconSerializer,FollowUserSerializer,BlockUserSerializer,UserInformationSerializer,NotifyTargetSerializer,ReportSerializer

from .forms import UserPolicyForm,ReportCategoryForm

DEFAULT_VIDEO_AMOUNT = 10
COMMENTS_AMOUNT_PAGE = 10

#python-magicで受け取ったファイルのMIMEをチェックする。
#MIMEについては https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types を参照。

from PIL import Image
import qrcode
from io import BytesIO
import base64

import magic
ALLOWED_MIME   = ["video/mp4"]

# アップロードの上限
LIMIT_SIZE     = 2000 * 1000 * 1000

SEARCH_AMOUNT_PAGE  = 20

#トップページ
class IndexView(views.APIView):

    def get(self, request,*args, **kwargs):

        # 新着順
        latests = Video.objects.all().order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]
        latests = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).all().order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

        if request.user.is_authenticated:

            # 最近見た動画
            histories = History.objects.filter(user=request.user.id).exclude(target__user__blocked=request.user.id).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

            hist_id_list   = []
            for history in histories:
                hist_id_list.append(history.target.id)

            histories = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).filter(id__in=hist_id_list).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

            # フォローユーザーの動画
            follows = Video.objects.filter(user__followed=request.user.id).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]
            follows = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).filter(user__followed=request.user.id).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

            # 新着順(ブロックしたユーザーは除外)
            latests = Video.objects.exclude(user__blocked=request.user.id).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

            latests = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).exclude(user__blocked=request.user.id).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]
            # これで動画一覧表示時に、マイリス数とコメント数をセットで表示できる。

        else:
            histories = False
            follows = False

        context = {"latests": latests,
                   "histories": histories,
                   "follows": follows,
                   }

        return render(request, "tube/index.html", context)

index = IndexView.as_view()

#アップロードページ
class UploadView(LoginRequiredMixin,views.APIView):

    def get(self,request, *args, **kwargs):

        categories = VideoCategory.objects.all()
        context = {"categories": categories}

        return render(request, "tube/upload.html", context)


    def post(self, request, *args, **kwargs):

        print(request.data)

        request.data["user"]    = request.user.id
        serializer              = VideoSerializer(data=request.data)
        mime_type               = magic.from_buffer(request.FILES["movie"].read(1024), mime=True)

        print(request.data["movie"].size)
        print(type(request.data["movie"].size))

        if request.FILES["movie"].size >= LIMIT_SIZE:
            mb = str(LIMIT_SIZE / 1000000)

            json = {"error": True,
                    "message": "The maximum file size is " + mb + "MB"}

            return JsonResponse(json)

        if mime_type not in ALLOWED_MIME:
            mime = str(ALLOWED_MIME)
            json = {"error": True,
                    "message": "The file you can post is " + mime + "."}

            return JsonResponse(json)

        if serializer.is_valid():
            serializer.save()
        else:
            json    = { "error":True,
                        "message":"入力内容に誤りがあります。" }
            return JsonResponse(json)

        json    = { "error":False,
                    "message":"アップロード完了しました。" }

        return JsonResponse(json)


upload = UploadView.as_view()



#検索結果表示ページ
class SearchView(views.APIView):

    def get(self, request, *args, **kwargs):

        query = Q()
        page = 1

        if "word" in request.GET:

            word_list = request.GET["word"].replace("　", " ").split(" ")
            for w in word_list:
                query &= Q(Q(title__icontains=w) | Q(description__icontains=w))

        if "page" in request.GET:
            page = request.GET["page"]

        # TODO:ここでログインしていれば、ブロックユーザーを除外した検索をする。
        if request.user.is_authenticated:
            videos = Video.objects.filter(query).exclude(user__blocked=request.user.id).order_by("-dt")

            videos = Video.objects.filter(query).annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).exclude(user__blocked=request.user.id).order_by("-dt")

        else:
            videos = Video.objects.filter(query).order_by("-dt")

        amount = len(videos)

        videos_paginator = Paginator(videos, SEARCH_AMOUNT_PAGE)
        videos           = videos_paginator.get_page(page)

        context = {"videos": videos,
                   "amount": amount}

        return render(request, "tube/search.html", context)

search = SearchView.as_view()


#動画個別ページ
class SingleView(views.APIView):

    def get(self,request, video_pk,*args, **kwargs):

        print(request.user.username)

        video = Video.objects.filter(id=video_pk).first()

        blockeduser = CustomUser.objects.filter(blocked=video.user.id)
        print(blockeduser)

        if request.user in blockeduser:
            print("ブロックされています")
            return redirect( "tube:index" )
        else:
            print("ブロックされていません")

        #Todo:F5で再生回数水増し可能。
        video.views = video.views + 1
        video.save()

        if request.user.is_authenticated:
            print("認証済みユーザーです")

            history = History.objects.filter(user=request.user.id, target=video_pk).first()

            if history:
                print("存在する場合の処理")
                history.views   = history.views + 1
                history.dt      = timezone.now()
                history.save()
            else:
                print("履歴に存在しない場合の処理")
                data        = { "target":video_pk,
                                "user":request.user.id,}
                serializer  = HistorySerializer(data=data)

                if serializer.is_valid():
                    serializer.save()


        img   = qrcode.make(request.build_absolute_uri()) #動画のQRコード
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr = base64.b64encode(buffer.getvalue()).decode().replace("'", "")

        counts = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).filter(id=video_pk).first()

        comments = VideoComment.objects.filter(target=video_pk).order_by("-dt")
        comments = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(target=video_pk).order_by("-dt")

        good        = GoodVideo.objects.filter(target=video_pk)
        already_good    = GoodVideo.objects.filter(target=video_pk, user=request.user.id)

        relates         = Video.objects.filter(category=video.category).prefetch_related('category').order_by("-dt")

        mylist          = MyList.objects.filter(target=video_pk)
        already_mylist  = MyList.objects.filter(target=video_pk, user=request.user.id)

        categories      = VideoCategory.objects.all()

        paginator = Paginator(comments, 10)
        comments  = paginator.get_page(1)


        form = ReportCategoryForm()
        userpolicy = UserPolicy.objects.filter(user=request.user.id).first()

        context = {"video": video,
                   "comments": comments,
                   "good": good,
                   "already_good": already_good,
                   "mylist":mylist,
                   "already_mylist":already_mylist,
                   "relates": relates,
                   "qr":qr,
                   "counts":counts,
                   "categories":categories,
                   "form":form,
                   "userpolicy":userpolicy,
                   }

        return render(request, "tube/single/single.html", context)


single = SingleView.as_view()


class SingleModView(LoginRequiredMixin,views.APIView):

    #ここでコメントのページネーション↑ のクラス名変えるべきでは？
    def get(self,request,video_pk,*args,**kwargs):

        page        = 1
        if "page" in request.GET:
            page    = request.GET["page"]

        video               = Video.objects.filter(id=video_pk).first()
        comments            = VideoComment.objects.filter(target=video_pk).order_by("-dt")
        comments            = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(target=video_pk).order_by("-dt")

        comments_paginator  = Paginator(comments,COMMENTS_AMOUNT_PAGE)
        comments            = comments_paginator.get_page(page)



        #コメントをrender_to_stringテンプレートを文字列化、json化させ返却
        context     = { "comments":comments,
                        "video":video,
                        }
        content     = render_to_string('tube/single/comments.html', context ,request)

        json        = { "error":False,
                        "content":content,
                        }

        return JsonResponse(json)


    def post(self, request, video_pk, *args, **kwargs):

        copied   = request.POST.copy()

        copied["target"]  = video_pk
        copied["user"]    = request.user.id

        serializer  = VideoCommentSerializer(data=copied)
        json        = {}

        if serializer.is_valid():
            print("コメントバリデーションOK")
            serializer.save()

            comments    = VideoComment.objects.filter(target=video_pk).order_by("-dt")
            comments = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(
                target=video_pk).order_by("-dt")

            comments_paginator  = Paginator(comments,COMMENTS_AMOUNT_PAGE)
            comments            = comments_paginator.get_page(1)
            video               = Video.objects.filter(id=video_pk).first()

            context     = { "comments":comments,
                            "video":video,
                            }

            content     = render_to_string('tube/single/comments.html', context, request)

            json        = { "error":False,
                            "message":"投稿完了",
                            "content":content,
                            }

        else:
            print("コメントバリデーションNG")
            json        = {"error":True,
                           "message":"入力内容に誤りがあります。",
                           "content":"",
                           }


        return JsonResponse(json)

    def patch(self,request,video_pk,*args,**kwargs):

        serializer  = RateSerializer(data=request.data)

        if not serializer.is_valid():

            json = {"error": True,
                    "message": "入力内容に誤りがあります。",
                    "content": "",
                    }

            return JsonResponse(json)

        validated_data  = serializer.validated_data

        if validated_data["flag"]:

            data    = GoodVideo.objects.filter(user=request.user.id, target=video_pk).first()
            if data:
                data.delete()
                print("削除")
                error = False
                message = "「いいね」を取り消しました。"

            else:
                data    = { "user":request.user.id,
                            "target":video_pk,
                            }
                serializer  = GoodSerializer(data=data)

                if serializer.is_valid():
                    print("セーブ")
                    serializer.save()
                    error = False
                    message = "「いいね」しました。"
                else:
                    print("バリデーションエラー")
                    error = True
                    message = "登録に失敗しました。"

        else:
            data    = MyList.objects.filter(user=request.user.id, target=video_pk).first()
            if data:
                data.delete()
                print("削除")
                error = False
                message = "マイリストから削除しました。"
            else:
                data = {"user": request.user.id,
                        "target": video_pk,
                        }
                serializer = MyListSerializer(data=data)

                if serializer.is_valid():
                    print("セーブ")
                    serializer.save()
                    error = False
                    message = "マイリストに登録しました。"
                else:
                    print("バリデーションエラー")
                    error = True
                    message = "登録に失敗しました。"

        good            = GoodVideo.objects.filter(target=video_pk)
        mylist          = MyList.objects.filter(target=video_pk)
        already_good    = GoodVideo.objects.filter(target=video_pk, user=request.user.id)
        already_mylist  = MyList.objects.filter(target=video_pk, user=request.user.id)
        video           = Video.objects.filter(id=video_pk).first()

        context = {"good": good,
                   "mylist": mylist,
                   "already_good": already_good,
                   "already_mylist": already_mylist,
                   "video": video,
                   }

        content = render_to_string('tube/single/rate.html', context, request)

        json = {"error": error,
                "message": message,
                "content": content,
                }

        return JsonResponse(json)

    #動画に対する編集処理（リクエストユーザーが動画投稿者であることを確認して実行）
    def put(self,request,video_pk,*args,**kwargs):

        json = {"error":True }

        # 編集対象の動画を特定する。
        instance = Video.objects.filter(id=video_pk).first()

        # 無い場合はそのまま返す
        if not instance:
            return JsonResponse(json)

        # TIPS:get_object_or_404を使う方法もある、いずれにせよレコード単体のオブジェクトをシリアライザの第一引数に指定して、編集対象を指定する必要がある点で同じ。こちらは存在しない場合404をリターンするためif文で分岐させる必要はない。
        # instance    = get_object_or_404(Video.objects.all(), pk=video_pk)

        # 受け取ったリクエストのdataにAjaxの送信内容が含まれているのでこれをバリデーション。編集対象は先ほどvideo_pkで特定したレコード単体
        serializer = VideoEditSerializer(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            json = {"error": False}
            Video.objects.filter(id=video_pk).update(edited=True)

        return JsonResponse(json)

    #動画に対する削除処理
    def delete(self,request,video_pk,*args,**kwargs):

        video   = Video.objects.filter(id=video_pk).first()

        if video.user.id == request.user.id:
            print("削除")
            video.delete()
            error   = False
            message = "削除しました。"

        else:
            print("拒否")
            error   = True
            message = "削除できませんでした。"

        json        = {"error":error,
                       "message":message,}

        return JsonResponse(json)

single_mod = SingleModView.as_view()


# コメントの削除、編集
class VideoCommentEditView(LoginRequiredMixin,views.APIView):

    def delete(self, request, comment_pk, *args, **kwargs):

        v_comment = VideoComment.objects.filter(id=comment_pk).first()

        v_comment.delete()
        print("コメント削除")

        error = False
        message = "削除しました。"

        json = {"error": error,
                "message": message,}

        return JsonResponse(json)


    def put(self,request,comment_pk,*args,**kwargs):

        print(request.data)

        comment = VideoComment.objects.filter(id=comment_pk).first()
        video_pk = comment.target.id
        print(video_pk)

        json = {"error":True }

        # 無い場合はそのまま返す
        if not comment:
            return JsonResponse(json)

        copied   = request.data.copy()
        copied["target"]  = video_pk
        copied["user"]    = request.user.id

        print(copied)

        serializer  = VideoCommentEditSerializer(comment, data=copied)

        if serializer.is_valid():
            print(serializer.validated_data)

            serializer.save()
            print("コメント編集バリデーションOK")


            comments    = VideoComment.objects.filter(target=video_pk).order_by("-dt")
            comments = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(
                target=video_pk).order_by("-dt")

            comments_paginator  = Paginator(comments,COMMENTS_AMOUNT_PAGE)
            comments            = comments_paginator.get_page(1)
            video               = Video.objects.filter(id=video_pk).first()

            context     = { "comments":comments,
                            "video":video,
                            }

            content     = render_to_string('tube/single/comments.html', context, request)

            json        = { "error":False,
                            "message":"コメント編集完了しました。",
                            "content":content,
                            }

        else:
            print("コメント編集バリデーションNG")
            json        = {"error":True,
                           "message": "入力内容に誤りがあります。",
                           "content": "",
                           }


        return JsonResponse(json)

video_comment_edit = VideoCommentEditView.as_view()


# 動画コメントのリプライの削除、編集
class VideoCommentReplyEditView(LoginRequiredMixin,views.APIView):

    def delete(self, request, reply_pk, *args, **kwargs):

        comment_reply = VideoCommentReply.objects.filter(id=reply_pk).first()

        comment_reply.delete()
        print("コメント削除")

        error = False
        message = "削除しました。"

        json = {"error": error,
                "message": message,}

        return JsonResponse(json)


    def put(self,request,reply_pk,*args,**kwargs):
        print(request.data)


        reply = VideoCommentReply.objects.filter(id=reply_pk).first()
        print(reply)
        comment_pk = reply.target.id

        video_pk = reply.target.target.id

        json = {"error":True }

        # 無い場合はそのまま返す
        if not reply:
            return JsonResponse(json)

        copied   = request.data.copy()
        copied["target"]  = comment_pk
        copied["user"]    = request.user.id

        serializer  = VideoCommentReplyEditSerializer(reply, data=copied)

        if serializer.is_valid():

            serializer.save()
            print("リプライ編集バリデーションOK")

            replies    = VideoCommentReply.objects.filter(target=comment_pk).order_by("-dt")

            comments  = VideoComment.objects.filter(target=video_pk).order_by("-dt")
            comments = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(
                target=video_pk).order_by("-dt")

            comments_paginator  = Paginator(comments,COMMENTS_AMOUNT_PAGE)
            comments            = comments_paginator.get_page(1)
            video               = Video.objects.filter(id=video_pk).first()

            context     = { "replies":replies,
                            "comments":comments,
                            "video":video,
                            }

            content     = render_to_string('tube/single/comments.html', context, request)

            json        = { "error":False,
                            "message":"編集完了しました。",
                            "content":content,
                            }

        else:
            print("コメント編集バリデーションNG")
            json        = {"error":True,
                           "message": "入力内容に誤りがあります。",
                           "content": "",
                           }

        return JsonResponse(json)


video_comment_reply_edit = VideoCommentReplyEditView.as_view()



# 動画コメントのリプに対するリプライの削除、編集
class VideoCommentReplyToReplyEditView(LoginRequiredMixin,views.APIView):

    def delete(self, request, r_to_reply_pk, *args, **kwargs):

        r_to_reply = VideoCommentReplyToReply.objects.filter(id=r_to_reply_pk).first()
        r_to_reply.delete()
        print("コメント削除")

        error = False
        message = "削除しました。"

        json = {"error": error,
                "message": message,}

        return JsonResponse(json)


    def put(self,request,r_to_reply_pk,*args,**kwargs):
        print(request.data)

        r_to_reply = VideoCommentReplyToReply.objects.filter(id=r_to_reply_pk).first()
        print(r_to_reply)

        reply_pk   = r_to_reply.target.id
        comment_pk = r_to_reply.target.target.id
        video_pk   = r_to_reply.target.target.target.id

        json = {"error":True }

        # 無い場合はそのまま返す
        if not r_to_reply:
            return JsonResponse(json)

        copied   = request.data.copy()
        copied["target"]  = reply_pk
        copied["user"]    = request.user.id

        serializer  = VideoCommentReplyToReplyEditSerializer(r_to_reply, data=copied)

        if serializer.is_valid():

            serializer.save()
            print("リプライ編集バリデーションOK")

            r_to_replies    = VideoCommentReplyToReply.objects.filter(target=reply_pk).order_by("-dt")
            replies         = VideoCommentReply.objects.filter(target=comment_pk).order_by("-dt")

            comments  = VideoComment.objects.filter(target=video_pk).order_by("-dt")
            comments = VideoComment.objects.annotate(num_reply=Count("videocommentreply", distinct=True)).filter(
                target=video_pk).order_by("-dt")

            comments_paginator  = Paginator(comments,COMMENTS_AMOUNT_PAGE)
            comments            = comments_paginator.get_page(1)
            video               = Video.objects.filter(id=video_pk).first()

            context     = { "r_to_replies":r_to_replies,
                            "replies":replies,
                            "comments":comments,
                            "video":video,
                            }

            content     = render_to_string('tube/single/comments.html', context, request)

            json        = { "error":False,
                            "message":"編集完了しました。",
                            "content":content,
                            }

        else:
            print("リプライ編集バリデーションNG")
            json        = {"error":True,
                           "message": "入力内容に誤りがあります。",
                           "content": "",
                           }

        return JsonResponse(json)


video_comment_r_to_reply_edit = VideoCommentReplyToReplyEditView.as_view()




# GET:リプライの参照、レンダリングして返す。POST:リプライの送信とバリデーション保存。いずれもAjaxで実装させる

# CHECK:ここのcomment_pkはコメントのID意味している。
class VideoCommentReplyView(LoginRequiredMixin,views.APIView):

    def get(self, request, comment_pk, *args, **kwargs):

        json = {"error": True, }

        replies = VideoCommentReply.objects.filter(target=comment_pk).order_by("-dt")
        replies = VideoCommentReply.objects.annotate(num_reply=Count("videocommentreplytoreply", distinct=True)).filter(target=comment_pk).order_by("-dt")

        form = ReportCategoryForm()

        context = {"replies": replies,
                   "form":form,}
        content = render_to_string('tube/single/comments_reply.html', context, request)

        json["error"] = False
        json["content"] = content

        return JsonResponse(json)

    def post(self, request, comment_pk, *args, **kwargs):

        # TODO:ユーザーがブロックしている場合、コメント投稿できないようにするのは？
        copied = request.POST.copy()
        copied["target"] = comment_pk
        copied["user"] = request.user.id

        serializer = VideoCommentReplySerializer(data=copied)

        json = {"error": True}

        if serializer.is_valid():
            print("リプライバリデーションOK")
            json["error"] = False
            serializer.save()
        else:
            print("リプライバリデーションNG")

        replies = VideoCommentReply.objects.filter(target=comment_pk).order_by("-dt")

        context = {"replies": replies}
        content = render_to_string('tube/single/comments_reply.html', context, request)

        json["content"] = content

        return JsonResponse(json)


video_comment_reply = VideoCommentReplyView.as_view()


# CHECK:ここのvideocommentreply_pkはコメントへのリプライのIDを意味している。
class VideoCommentReplyToReplyView(LoginRequiredMixin,views.APIView):

    def get(self, request, videocommentreply_pk, *args, **kwargs):

        json = {"error": True, }

        r_to_replies = VideoCommentReplyToReply.objects.filter(target=videocommentreply_pk).order_by("-dt")
        form = ReportCategoryForm()

        context = {"r_to_replies": r_to_replies,
                   "form":form,}
        content = render_to_string('tube/single/comments_reply_to_reply.html', context, request)

        json["error"] = False
        json["content"] = content

        return JsonResponse(json)

    def post(self, request, videocommentreply_pk, *args, **kwargs):

        # TODO:ユーザーがブロックしている場合、コメント投稿できないようにするのは？

        copied = request.POST.copy()
        copied["target"] = videocommentreply_pk
        copied["user"] = request.user.id

        serializer = VideoCommentReplyToReplySerializer(data=copied)

        json = {"error": True}

        if serializer.is_valid():
            print("リプライへのリプライバリデーションOK")

            json["error"] = False
            serializer.save()
        else:
            print("リプライへのリプライバリデーションNG")

        r_to_replies = VideoCommentReplyToReply.objects.filter(target=videocommentreply_pk).order_by("-dt")

        context = {"r_to_replies": r_to_replies}
        content = render_to_string('tube/single/comments_reply_to_reply.html', context, request)

        json["content"] = content

        return JsonResponse(json)


video_comment_reply_to_reply = VideoCommentReplyToReplyView.as_view()


class RankingView(views.APIView):

    def get(self,request,*args,**kwargs):

        return render(request,"tube/rank.html")

rank    = RankingView.as_view()


class UserPolicyView(views.APIView):

    def get(self,request,*args,**kwargs):

        userpolicy = UserPolicy.objects.filter(user=request.user.id).first()

        form = UserPolicyForm()
        context = { "userpolicy":userpolicy,
                    "form":form, }

        return render(request,"tube/user_policy.html", context )


    def post(self,request,*args,**kwargs):
        print(request.data)
        print(request.user)

        formset = UserPolicyForm(request.POST)

        if formset.is_valid():
            print("バリデーションOK")
            f = formset.save(commit=False)
            f.user = request.user
            f.save()

        else:
            print("バリデーションエラー")

        return redirect("tube:index")


user_policy   = UserPolicyView.as_view()


class MyPageView(LoginRequiredMixin, views.APIView):

    def get(self, request,*args, **kwargs):

        videos = Video.objects.filter(user=request.user.id).order_by("-dt")
        good_videos = GoodVideo.objects.filter(user=request.user.id).order_by("-dt")
        custom_user  = CustomUser.objects.filter(id=request.user.id).first()


        videos = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),num_mylists=Count("mylist", distinct=True)).filter(user=request.user.id).order_by("-dt")

        good_video_id_list = []
        for good_video in good_videos:
            good_video_id_list.append(good_video.target.id)

        good_videos = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),
                                           num_mylists=Count("mylist", distinct=True)).filter(
            id__in=good_video_id_list).order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]
        print(good_videos)

        context = {"videos": videos,
                   "good_videos": good_videos,
                   "custom_user": custom_user,
                   }

        return render(request, "tube/mypage/mypage.html", context)


    def post(self,request, *args,**kwargs):

        print(request.data)
        print(request.user.id)

        instance = CustomUser.objects.get(id=request.user.id)

        serializer = IconSerializer(instance, data=request.data)

        if serializer.is_valid():
            print("validation OK")
            serializer.save()

            custom_user = CustomUser.objects.filter(id=request.user.id).first()
            context     = {"custom_user":custom_user}
            print(context)

            content     = render_to_string('tube/mypage/mypage_usericon.html', context ,request)
            print(content)

            json = {"error": False,
                    "message":"アイコンが登録されました。",
                    "content":content,
                    }

        else:
            print("バリデーションエラー")
            json = {"error": True,
                    "message": "アイコン登録に失敗しました。",
                    }

        return JsonResponse(json)


mypage = MyPageView.as_view()



# 閲覧履歴表示
class HistoryView(LoginRequiredMixin, views.APIView):

    def get(self, request, *args, **kwargs):
        histories = History.objects.filter(user=request.user.id).order_by("-dt")
        amount    = len(histories)

        paginator = Paginator(histories, 10)

        if "page" in request.GET:
            histories = paginator.get_page(request.GET["page"])
        else:
            histories = paginator.get_page(1)

        context = {"histories": histories,
                   "amount": amount}

        return render(request, "tube/history.html", context)


history = HistoryView.as_view()


# おすすめ動画
class RecommendView(LoginRequiredMixin,views.APIView):

    def get(self,request,*args,**kwargs):

        return render(request, "tube/recommend.html")

recommend = RecommendView.as_view()


# 通知表示
class NotifyView(LoginRequiredMixin, views.APIView):

    def get(self, request, *args, **kwargs):

        # アクセスしたユーザーの通知を
        notify_targets = NotifyTarget.objects.filter(user=request.user.id).order_by("-dt")

        context = {"notify_targets": notify_targets}

        return render(request, "tube/notify.html", context)

    def patch(self, request, *args, **kwargs):

        json = {"error": True}

        data = request.data.copy()
        data["user"] = request.user.id
        print(data)

        serializer = NotifyTargetSerializer(data=data)

        if serializer.is_valid():
            validated = serializer.validated_data

            # TIPS:notify_targetのidで指定すると、通知を受け取ったユーザー以外が既読にされてしまう可能性があるため、
            # unique_togetherを実装した場合、.first()でひとつだけでいい。
            notify_target = NotifyTarget.objects.filter(notify=validated["notify"], user=validated["user"]).first()

            if notify_target:
                notify_target.read = True
                notify_target.save()

                json["error"] = False
                print("バリデーションOK")
            else:
                print("存在しないNotify")

        else:
            print("バリデーションNG")

        return JsonResponse(json)

    def delete(self, request, *args, **kwargs):

        json = {"error": True}

        # TODO:ここに通知の削除機能を

        return JsonResponse(json)


notify = NotifyView.as_view()



#マイリスト
class MyListView(LoginRequiredMixin,views.APIView):

    def get(self,request,*args,**kwargs):

        mylists = MyList.objects.filter(user=request.user.id).order_by("-dt")

        context = {"mylists":mylists}

        return render(request,"tube/mylist.html",context)

mylist = MyListView.as_view()




class ConfigViews(LoginRequiredMixin,views.APIView):

    def get(self, request, *args, **kwargs):

        # 自分がフォローしているユーザー、ブロックしているユーザーの一覧
        follow_users = FollowUser.objects.filter(from_user=request.user.id)
        block_users = BlockUser.objects.filter(from_user=request.user.id)

        # 自分をフォローしているユーザーしているユーザーの一覧
        follower_users = FollowUser.objects.filter(to_user=request.user.id)


        context = {"follow_users":follow_users,
                   "block_users":block_users,
                   "follower_users":follower_users,
                  }

        return render(request, "tube/config.html", context)

config = ConfigViews.as_view()



#ユーザーページの表示
class UserSingleView(LoginRequiredMixin,views.APIView):

    def get(self, request, pk, *args, **kwargs):

        user    = CustomUser.objects.filter(id=pk).first()

        blockeduser = CustomUser.objects.filter(blocked=user.id)
        print(blockeduser)

        if request.user in blockeduser:
            print("ブロックされています")
            return redirect( "tube:index" )
        else:
            print("ブロックされていません")


        #このユーザーがフォローしているユーザー、ブロックしているユーザーの一覧
        follow_users = FollowUser.objects.filter(from_user=pk)
        block_users  = BlockUser.objects.filter(from_user=pk)

        #このユーザーをフォローしているユーザーしているユーザーの一覧
        follower_users    = FollowUser.objects.filter(to_user=pk)

        videos = Video.objects.annotate(num_comments=Count("videocomment", distinct=True),
                                        num_mylists=Count("mylist", distinct=True)).filter(user=pk).order_by("-dt")

        context = { "user":user,
                    "follow_users":follow_users,
                    "block_users":block_users,
                    "follower_users":follower_users,
                    "videos":videos,
                  }

        return render(request, "tube/usersingle.html", context)

usersingle  = UserSingleView.as_view()


class UserFollowView(LoginRequiredMixin,views.APIView):

    def post(self,request,pk,*args,**kwargs):

        followusers  = FollowUser.objects.filter(from_user=request.user.id,to_user=pk) #from_userは自分自身。to_user はフォローした相手。

        json    = { "error":False }

        #すでにある場合は該当レコードを削除、無い場合は挿入
        #TIPS:↑メソッドやビュークラスを切り分けてしまうと、多重に中間テーブルへレコードが挿入されてしまう可能性があるため1つのメソッド内で分岐するやり方が無難。
        if followusers:
            print("ある。フォロー解除。")
            followusers.delete()

            return JsonResponse(json)
        else:
            print("無い")

        data        = { "from_user":request.user.id,"to_user":pk }
        serializer  = FollowUserSerializer(data=data)

        if serializer.is_valid():
            print("フォローOK")
            serializer.save()
        else:
            print("フォロー失敗")
            json["error"]   = True

        return JsonResponse(json)


userfollow   = UserFollowView.as_view()


class UserBlockView(LoginRequiredMixin,views.APIView):

    def post(self,request,pk,*args,**kwargs):

        blockusers  = BlockUser.objects.filter(from_user=request.user.id,to_user=pk)

        json    = { "error":False }

        if blockusers:
            print("ある。ブロック解除。")
            blockusers.delete()

            return JsonResponse(json)
        else:
            print("無い")

        data        = { "from_user":request.user.id,"to_user":pk }
        serializer  = BlockUserSerializer(data=data)

        if serializer.is_valid():
            print("ブロックOK")
            serializer.save()
        else:
            print("ブロック失敗")
            json["error"]   = True

        return JsonResponse(json)


userblock   = UserBlockView.as_view()


class UserEditView(LoginRequiredMixin,views.APIView):

    def put(self, request, pk, *args, **kwargs):

        print(request.user.id)

        json = {"error": True}

        # 編集対象の動画を特定する。
        instance = CustomUser.objects.filter(id=request.user.id).first()

        # 無い場合はそのまま返す
        if not instance:
            print('ない')
            return JsonResponse(json)

        # 受け取ったリクエストのdataにAjaxの送信内容が含まれているのでこれをバリデーション。
        serializer = UserInformationSerializer(instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            print('バリデーションOK')
            json = {"error": False,
                    "message":"登録しました。",
                    }

        else:
            print('バリデーションエラー')
            json = {"error": True,
                    "message": "登録に失敗しました。",
                    }

        return JsonResponse(json)

useredit = UserEditView.as_view()

class ReportView(LoginRequiredMixin,views.APIView):

    def post(self,request,pk,*args,**kwargs):
        print(pk,request.user.id)
        print(request.data)
        print(request.POST.get("target_id"))

        id = request.POST.get("target_id")

        reported = VideoComment.objects.filter(id=id).first()
        print(reported.user)
        print(reported.user.id)

        copied = request.POST.copy()
        copied["reported_user"] = reported.user.id
        copied["report_user"]   = request.user.id

        serializer = ReportSerializer(data=copied)

        if serializer.is_valid():
            print("通報バリデーションOK")

            serializer.save()
            json = {"error": False,
                    "message": "通報内容を受け取りました。当社にて内容を吟味し、対応致します。",
                    }
        else:
            print("通報バリデーションNG")
            json = { "error" :True,
                     "message":"通報内容に誤りがあります。"}

        return JsonResponse(json)


report  = ReportView.as_view()