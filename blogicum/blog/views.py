from django.conf import settings
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

SUCCESS_URL = reverse_lazy('blog:index')


def get_published(
        posts: Manager = Post.objects,
        select_related: bool = False,
        published: bool = False,
        order_by: bool = False,
        count_comments: bool = False
):
    """Return published posts."""
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
    if order_by:
        posts = posts.order_by('-pub_date')
    if count_comments:
        posts = posts.annotate(
            comment_count=Count('comments')
        )
    return posts


def get_paginator(request, model_objects):
    paginator = Paginator(model_objects, settings.OBJECTS_PER_PAGE)
    return paginator.get_page(request.GET.get('paginator'))


def index(request):
    """Main page for blog. Views all blog posts."""
    posts = get_published(
        select_related=True,
        published=True,
        order_by=True,
        count_comments=True
    )
    return render(request, 'blog/index.html', {
        'page_obj': get_paginator(request, posts),
    })


def post(request, post_id):
    """View post details."""
    post_ = get_object_or_404(Post, pk=post_id)
    if post_.author.id != request.user.id:
        post_ = get_object_or_404(
            get_published(published=True),
            pk=post_id
        )
    return render(request, 'blog/detail.html', {
        'post': post_,
        'form': CommentForm(),
        'comments': post_.comments.order_by('created_at')
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
            kwargs={'username': self.request.user.username}
        )


def edit_post(request, post_id):
    post_obj = get_object_or_404(Post, pk=post_id)
    if post_obj.author != request.user:
        return redirect(post_obj)
    form = PostForm(request.POST or None, instance=post_obj)
    if form.is_valid():
        form.save()
        return redirect(post_obj)
    return render(request, 'blog/create.html', {
        'form': form
    })


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = SUCCESS_URL

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


def category(request, category_slug):
    """View published posts in category, if pub date less than now."""
    category_ = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_published(
        category_.posts,
        select_related=True,
        published=True,
        order_by=True,
        count_comments=True
    )
    return render(request, 'blog/category.html', {
        'category': category_,
        'page_obj': get_paginator(request, posts)
    })


def profile(request, username):
    """View user's profile with posts."""
    author = get_object_or_404(User, username=username)
    if request.user == author:
        posts = get_published(
            posts=author.posts,
            select_related=True,
            order_by=True,
            count_comments=True
        )
    else:
        posts = get_published(
            posts=author.posts,
            select_related=True,
            published=True,
            order_by=True,
            count_comments=True
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
        post_obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentUserPassesTestMixin(UserPassesTestMixin):
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
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(CommentUserPassesTestMixin, DeleteView):
    """Delete comment."""

    success_url = SUCCESS_URL
