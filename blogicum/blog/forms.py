from django import forms

from blog.models import User, Post, Comment


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PostForm(forms.ModelForm):

    class Meta:
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        model = Post
        fields = ['title', 'text', 'location', 'category', 'pub_date', 'image']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
