from django import forms
from .models import Account

class RegistrationsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm password'
    }))
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name','phone_number', 'email', 'password','confirm_password']
    def __init__(self,*args, **kwargs): 
        super(RegistrationsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] ='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] ='Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] ='Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] ='Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] ='form-control'
    def clean(self):
        cleaned_data = super(RegistrationsForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError(
                "password does not matched"
            )        