from django import forms
from .models import Notify,NotifyTarget,UserPolicy,ReportCategory,Report

class NotifyAdminForm(forms.ModelForm):

    class Meta:
        model   = Notify
        fields  = [ "category","dt","title","content", ]


    content     = forms.CharField(  widget  = forms.Textarea( attrs={ "maxlength":str(Notify.content.field.max_length), } ),
                                    label   = Notify.content.field.verbose_name
                                    )


class NotifyTargetAdminForm(forms.ModelForm):

    class Meta:
        model   = NotifyTarget
        fields  = [ "notify","user" ]

class UserPolicyForm(forms.ModelForm):

    class Meta:
        model   = UserPolicy
        fields  = [ "accept"]
        labels  = { "accept":"利用規約に同意する。"}

class ReportCategoryForm(forms.Form):
    category  = forms.ModelChoiceField(ReportCategory.objects, label="通報理由",empty_label="選択してください")


class ReportForm(forms.ModelForm):

    class Meta:
        model   = Report
        fields = ["category","reason"]
