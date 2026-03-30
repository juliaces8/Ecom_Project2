from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Product, Review, Store
from django.core.exceptions import ValidationError

# 1. Registration Form (User + Role)


class UserRegisterForm(UserCreationForm):
    """
    Handles user registration and profile creation.
    Includes a unique email check to prevent duplicate accounts.
    """
    email = forms.EmailField(required=True, help_text="Required for invoices.")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        """Validates that the email address is unique in the system."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "A user with this email address already exists.")
        return email

    def save(self, commit=True):
        """Saves the User and automatically creates the associated Profile."""
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(user=user,
                                   role=self.cleaned_data.get('role'))
        return user

# 2. Product Form (For Vendors)


class ProductForm(forms.ModelForm):
    """Form for Vendors to list or update products."""
    class Meta:
        model = Product
        fields = ['store', 'name', 'description', 'price', 'stock']

# 3. Review Form (Matched to 'content' field in Model)


class ReviewForm(forms.ModelForm):
    """Form for Buyers to submit product ratings and feedback."""
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)],
                                   attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts on this product...'
            }),
        }

# 4. Store Form (For Vendors to Create/Update Stores)


class StoreForm(forms.ModelForm):
    """Form for creating/editing a Vendor store.
    Description is now mandatory."""
    class Meta:
        model = Store
        fields = ['name', 'description', 'logo']
