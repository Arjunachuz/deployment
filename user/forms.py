from dataclasses import fields
from django import forms
from accounts.models import Account, UserProfile
from orders.models import Coupon, UsedCoupon


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class'      :'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password', 
        'class'      :'form-control',
    }))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)   
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number' 
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        phone_number = cleaned_data.get('phone_number')  
        password         = cleaned_data.get('password')        
        confirm_password = cleaned_data.get('confirm_password')       
        user = Account.objects.filter(phone_number=phone_number).exists()
        
        phone = str(phone_number)

        # if phone[0] != '+':
        #     raise forms.ValidationError('Phone Number should start with "+91"')

        if len(phone) != 10:  

            raise forms.ValidationError('Phone Number must be 10 digits')  

        elif user:
            raise forms.ValidationError('Phone Number already exist!') 

        else:
            if password != confirm_password:
                raise forms.ValidationError('Password does not match') 

class UserForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')    

    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)  
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'             

class UserProfileForm(forms.ModelForm):

    profile_picture = forms.ImageField(required=False, error_messages={'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile    
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')   

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)  
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'         


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ("coupon_code", "discount", "is_active")


class UsedCouponForm(forms.ModelForm):
    class Meta:
        model = UsedCoupon
        fields = ("user", "coupon")