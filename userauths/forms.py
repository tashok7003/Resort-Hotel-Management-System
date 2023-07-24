from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ImageField, FileInput, TextInput, Select
from captcha.fields import CaptchaField


class CustomCaptchaField(CaptchaField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['class'] = 'form-control'
        attrs['placeholder'] = 'Enter Captcha Keyword'
        return attrs


from userauths.models import Profile, User

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': '', 'id': "", 'placeholder':'Full Name'}), max_length=100, required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': '', 'id': "", 'placeholder':'Username'}), max_length=100, required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': '' , 'id': "", 'placeholder':'Email Address'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "", 'placeholder':'Password'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "", 'placeholder':'Confirm Password'}), required=True)
    captcha=CustomCaptchaField()

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2', 'captcha']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'with-border'
            # visible.field.widget.attrs['placeholder'] = visible.field.label
