from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path(
        'profile/<slug:username>/edit/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.profile,
        name='profile'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.edit_post,
        name='edit_post'
    ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:pk>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:pk>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path(
        'posts/<int:pk>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/',
        views.post,
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'category/<slug:category_slug>/', views.category, name='category_posts'
    ),
    path(
        '',
        views.index,
        name='index'
    ),
]
