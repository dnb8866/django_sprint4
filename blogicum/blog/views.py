from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.manager import Manager
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView

from blog.forms import ProfileEditForm, PostForm, CommentForm
from blog.models import Post, Category, User, Comment

OBJECTS_PER_PAGE = 10
SUCCESS_URL = reverse_lazy('blog:index')


def get_posts(
        posts: Manager = Post.objects,
        select_related: bool = True,
        published: bool = True,
        count_comments: bool = True
) -> Manager:
    """Return posts."""
    if select_related:
        posts = posts.select_related(
            'category',
            'author',
            'location'
        )
    if published:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    if count_comments:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by(
            *posts.model._meta.ordering
        )
    return posts


def get_paginator(
    request,
    model_objects: Manager,
    per_page: int = OBJECTS_PER_PAGE
) -> Paginator:
    """Return paginator."""
    return (Paginator(model_objects, per_page)
            .get_page(request.GET.get('paginator')))


def index(request):
    """Main page for blog. Views all blog posts."""
    return render(request, 'blog/index.html', {
        'page_obj': get_paginator(request, get_posts()),
    })


def show_post(request, post_id):
    """View post details."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author.id != request.user.id:
        post = get_object_or_404(
            get_posts(
                select_related=False,
                count_comments=False
            ),
            pk=post_id
        )
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all()
    })


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create new post."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = SUCCESS_URL

    def form_valid(self, form):
        """Add current user to post."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


def edit_post(request, post_id):
    """Edit post."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(post)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(post)
    return render(request, 'blog/create.html', {
        'form': form
    })


class PostDeleteView(UserPassesTestMixin, DeleteView):
    """Delete post."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = SUCCESS_URL

    def test_func(self):
        return self.get_object().author == self.request.user


def show_category(request, category_slug):
    """View published posts in category, if pub date less than now."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': get_paginator(
            request,
            get_posts(category.posts)
        )
    })


def show_profile(request, username):
    """View user's profile with posts."""
    author = get_object_or_404(User, username=username)
    posts = get_posts(
        author.posts,
        published=False if request.user == author else True
    )
    return render(request, 'blog/profile.html', {
        'profile': author,
        'page_obj': get_paginator(request, posts)
    })


@login_required
def edit_profile(request):
    """Update user's profile."""
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {
        'form': form
    })


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Create new comment."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', args=[self.kwargs['post_id']]
        )


class CommentUserPassesTestMixin(UserPassesTestMixin):
    """Mixin class for checking author"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.get_object().author == self.request.user


class CommentUpdateView(CommentUserPassesTestMixin, UpdateView):
    """Update comment."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.kwargs['post_id']]
        )


class CommentDeleteView(CommentUserPassesTestMixin, DeleteView):
    """Delete comment."""

    success_url = SUCCESS_URL
