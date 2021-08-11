from rest_framework import serializers

from .models import Video,VideoComment,VideoCommentReply,VideoCommentReplyToReply,MyList,History,GoodVideo,Report
from users.models import CustomUser,FollowUser,BlockUser

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Video
        fields =["title","description","category","movie","thumbnail","user",]

class VideoEditSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Video
        fields =[ "title","description","category", ]


class VideoCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoComment
        fields = ["content","target","user",]

class VideoCommentEditSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoComment
        fields = [ "content","target","user",]

class VideoCommentReplyEditSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoCommentReply
        fields = [ "content","target","user",]

class VideoCommentReplyToReplyEditSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoCommentReplyToReply
        fields = [ "content","target","user",]

#TIPS:フィールド名はVideoCommentSerializerと全く同じだが、外部キーで繋がっているものが全く違うので、リプライのバリデーションにVideoCommentSerializerを流用してはならない
class VideoCommentReplySerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoCommentReply
        fields = ["content","target","user",]

class VideoCommentReplyToReplySerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoCommentReplyToReply
        fields = ["content","target","user",]


class MyListSerializer(serializers.ModelSerializer):

    class Meta:
        model   = MyList
        fields  = ["target","user",]

class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model   = History
        fields  = ["target","user",]

class RateSerializer(serializers.Serializer):

    flag    = serializers.BooleanField()

class GoodSerializer(serializers.ModelSerializer):

    class Meta:
        model   = GoodVideo
        fields  = [ "target","user",]


class IconSerializer(serializers.ModelSerializer):

    class Meta:
        model  = CustomUser
        fields = ["usericon",]

class FollowUserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = FollowUser
        fields =[ "from_user","to_user" ]

class BlockUserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = BlockUser
        fields =[ "from_user","to_user" ]


class UserInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = CustomUser
        fields =[ "handle_name","self_introduction" ]


#unique_togetherを実装しているので、普通のモデルを継承したシリアライザでは既読処理は重複判定され、バリデーションNGになる。
"""
class NotifyTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model   = NotifyTarget
        fields  = [ "notify","user"  ]
"""

#モデルとは紐付かないシリアライザを作る。
class NotifyTargetSerializer(serializers.Serializer):
    notify  = serializers.UUIDField()
    user    = serializers.UUIDField()

class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Report
        fields = [ "report_user","reported_user","reason","category","target" ]


    #シリアライザクラスはモデルクラスのsaveメソッドを継承していないため、モデルのセーブメソッドをオーバーライドしても意味ない。
    #備考: ↑フォームクラスはモデルクラスのsaveメソッドを継承する。故にフォームクラスを使用してバリデーションする場合はモデルクラスのsaveメソッドオーバーライドが有効

    #TODO:通報が保存される度、メール送信を行う。
    def save(self, *args, **kwargs):

        #instanceがNoneじゃない(編集ではない)とき
        if not self.instance:

            #これらを組み合わせる
            print(self.validated_data["report_user"])
            print(self.validated_data["report_user"].id)
            print(self.validated_data["reported_user"])
            print(self.validated_data["reported_user"].id)
            print(self.validated_data["reason"])

            # settingsからAPIキーを参照、sendgridのライブラリから本文と件名、メールアドレスを指定して送信する。
            # https://noauto-nolife.com/post/django-sendgrid/
            print("管理者へメール送信")

        super().save(*args, **kwargs)





