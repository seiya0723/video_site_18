from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator

import uuid


class VideoCategory(models.Model):

    class Meta:
        db_table = "video_category"

    # TIPS:数値型の主キーではPostgreSQLなど一部のDBでエラーを起こす。それだけでなく予測がされやすく衝突しやすいので、UUID型の主キーに仕立てる。
    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    name   = models.CharField(verbose_name="カテゴリー名", max_length=10)

    def __str__(self):
        return self.name


class Video(models.Model):

    class Meta:

        db_table = "video"

    id       = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    category = models.ForeignKey(VideoCategory, verbose_name="カテゴリ", on_delete=models.PROTECT,related_name='video')
    dt       = models.DateTimeField(verbose_name="投稿日", default=timezone.now)

    title        = models.CharField(verbose_name="タイトル", max_length=50)
    description  = models.CharField(verbose_name="動画説明文", max_length=500)
    movie        = models.FileField(verbose_name="動画", upload_to="tube/movie", blank=True)
    thumbnail    = models.ImageField(verbose_name="サムネイル", upload_to="tube/thumbnail/", null=True)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    edited       = models.BooleanField(default=False)

    views        = models.IntegerField(verbose_name="再生回数", default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title


class VideoComment(models.Model):

    class Meta:
        db_table = "video_comment"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    content = models.CharField(verbose_name="コメント文", max_length=500)
    target  = models.ForeignKey(Video, verbose_name="コメント先の動画", on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    def __str__(self):
        return self.content


#コメントに対するリプライのモデル
class VideoCommentReply(models.Model):

    class Meta:
        db_table = "video_comment_reply"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    content = models.CharField(verbose_name="リプライ", max_length=500)
    target  = models.ForeignKey(VideoComment, verbose_name="リプライ対象のコメント", on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    def __str__(self):
        return self.content



#コメントに対するリプライのモデル
class VideoCommentReplyToReply(models.Model):

    class Meta:
        db_table = "video_comment_reply_to_reply"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False )
    content = models.CharField(verbose_name="動画コメントのリプライに対するリプライ", max_length=500)
    target  = models.ForeignKey(VideoCommentReply, verbose_name="リプライ対象のコメント", on_delete=models.CASCADE)
    dt      = models.DateTimeField(verbose_name="投稿日", default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class History(models.Model):

    class Meta:
        db_table     = "history"

    id     = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt     = models.DateTimeField(verbose_name="視聴日時", default=timezone.now)
    target = models.ForeignKey(Video, verbose_name="視聴した動画", on_delete=models.CASCADE)
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="視聴したユーザー", on_delete=models.CASCADE)
    views  = models.IntegerField(verbose_name="視聴回数", default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.target.title


class MyList(models.Model):

    class Meta:
        db_table    = "mylist"

    id       = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt       = models.DateTimeField(verbose_name="登録日時", default=timezone.now)
    target   = models.ForeignKey(Video, verbose_name="マイリスト動画", on_delete=models.CASCADE)
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="登録したユーザー", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.title


class NotifyCategory(models.Model):
    class Meta:
        db_table = "notify_category"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="通知カテゴリ名", max_length=10)

    def __str__(self):
        return self.name


class Notify(models.Model):
    class Meta:
        db_table = "notify"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(NotifyCategory, verbose_name="通知カテゴリ", on_delete=models.CASCADE, null=True)
    dt = models.DateTimeField(verbose_name="通知作成日時", default=timezone.now)
    title = models.CharField(verbose_name="通知タイトル", max_length=200)
    content = models.CharField(verbose_name="通知内容", max_length=2000)
    target = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="通知対象のユーザー", through="NotifyTarget",
                                    through_fields=("notify", "user"))

    def __str__(self):
        return self.title


class NotifyTarget(models.Model):
    # 下記で、組み合わせのユニークが実現できる。
    # https://stackoverflow.com/questions/2201598/how-to-define-two-fields-unique-as-couple

    class Meta:
        db_table = "notify_target"
        unique_together = ("user", "notify")

    # TODO:notifyはunique=Trueとして、全く同じ内容の通知が二度以上送られないようにするべきでは？
    # ↑通知は同じでもユーザーごとに異なるため、notifyだけuniqueにすると全員に対して通知できない。userとnotifyの組み合わせがユニークにする必要がある。

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dt = models.DateTimeField(verbose_name="通知日時", default=timezone.now)
    notify = models.ForeignKey(Notify, verbose_name="通知", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="通知対象", on_delete=models.CASCADE)
    read = models.BooleanField(verbose_name="既読", default=False)

    # Q:管理画面から通知が追加された時、対象者にメールを送信するには。
    # A:saveメソッドをオーバーライドする。ビューが埋まっている管理画面の他に、通常のビューでも処理の手間を省ける。
    # 参照元: https://docs.djangoproject.com/en/3.2/topics/db/models/#overriding-predefined-model-methods

    # ↑現状では単なる既読化、未読化の処理でもsaveメソッドを使っているので、下記のコードに別途条件分岐が必要。←未読既読のフォームクラスはモデルを継承していないので大丈夫では？
    """
    def save(self, *args, **kwargs):
        do_something()
        super().save(*args, **kwargs)  # Call the "real" save() method.
        do_something_else()
    """

    # deleteメソッドもオーバーライド可能


class GoodVideo(models.Model):

    class Meta:
        db_table    = "good_video"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt      = models.DateTimeField(verbose_name="評価日時", default=timezone.now)
    target  = models.ForeignKey(Video, verbose_name="対象動画", on_delete=models.CASCADE, related_name="favorite")
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="高評価したユーザー", on_delete=models.CASCADE)

    def __str__(self):
        return self.target.title


class ReportCategory(models.Model):
    class Meta:
        db_table = "report_category"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name="通報カテゴリ名", max_length=10)

    def __str__(self):
        return self.name

class Report(models.Model):

    class Meta:
        db_table    = "report"

    id             = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt             = models.DateTimeField(verbose_name="通報日時", default=timezone.now)
    report_user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="通報したユーザー", on_delete=models.CASCADE,related_name="report_user")
    reported_user  = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="通報されたユーザー", on_delete=models.CASCADE,related_name="reported_user")
    reason         = models.CharField(verbose_name="通報理由", max_length=200)
    category       = models.ForeignKey(ReportCategory, verbose_name="通報カテゴリ", on_delete=models.CASCADE, null=True)
    target         = models.CharField(verbose_name="通報対象", max_length=500)

    #TODO：通報されたコメントや動画を同定するには？
    def __str__(self):
        return self.reason

class UserPolicy(models.Model):

    class Meta:
        db_table    = "userpolicy"

    id      = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt      = models.DateTimeField(verbose_name="利用規約同意日時", default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="ユーザー", on_delete=models.CASCADE)
    accept  = models.BooleanField(verbose_name="同意", default=False)


# Twitterのモデル(推測)
"""
    id          = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dt          = models.DateTimeField(verbose_name="評価日時", default=timezone.now)
    target      = models.UUIDField(verbose_name="リプライ先",null=True,blank=True)
    content     = models.CharField(verbose_name="通知内容", max_length=200)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="高評価したユーザー", on_delete=models.CASCADE, related_name="favorite_from_user")

"""
