from django.urls import path, include

from blog import views

app_name = 'blog'

urlpatterns = [
    path('profile/',
         include(
             [
                 path('edit/', views.edit_profile, name='edit_profile'),
                 path('<slug:username>/', views.show_profile, name='profile')
             ]
         )
         ),
    path('posts/',
         include(
             [
                 path(
                     '<int:post_id>/edit/',
                     views.edit_post,
                     name='edit_post'
                 ),
                 path(
                     '<int:post_id>/delete/',
                     views.PostDeleteView.as_view(),
                     name='delete_post'
                 ),
                 path(
                     '<int:post_id>/edit_comment/<int:comment_id>/',
                     views.CommentUpdateView.as_view(),
                     name='edit_comment'
                 ),
                 path(
                     '<int:post_id>/delete_comment/<int:comment_id>/',
                     views.CommentDeleteView.as_view(),
                     name='delete_comment'
                 ),
                 path(
                     '<int:post_id>/comment/',
                     views.CommentCreateView.as_view(),
                     name='add_comment'
                 ),
                 path(
                     '<int:post_id>/',
                     views.show_post,
                     name='post_detail'
                 ),
                 path(
                     'create/',
                     views.PostCreateView.as_view(),
                     name='create_post'
                 ),
             ]
         )),
    path(
        'category/<slug:category_slug>/',
        views.show_category,
        name='category_posts'
    ),
    path('', views.IndexListView.as_view(), name='index'),
]
