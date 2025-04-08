# accounts/forms.py
#from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AuthenticationForm
#from .models import Custom_User

#class CustomUserCreationForm(UserCreationForm):
 #   class Meta:
  #      model = Custom_User
   #     fields = ['username', 'email', 'phone_number', 'address']
        # Include other fields as necessary

#class CustomUserChangeForm(UserChangeForm):
    #class Meta:
    #    model = Custom_User
   #     fields = ['username', 'email', 'phone_number', 'address']
        # Include other fields as necessary

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

 