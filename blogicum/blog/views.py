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


def get_published(posts: Manager = Post.objects):
    """Return published posts."""
    return posts.select_related(
        'category',
        'author',
        'location',
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def index(request):
    """Main page for blog. Views all blog posts."""
    posts = (
        get_published()
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )
    paginator = Paginator(posts, 10)
    return render(request, 'blog/index.html', {
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


def post(request, post_id):
    """View post details."""
    post_obj = get_object_or_404(Post, pk=post_id)
    if post_obj.author.id != request.user.id:
        post_obj = get_object_or_404(get_published(), pk=post_id)
    return render(request, 'blog/detail.html', {
        'post': post_obj,
        'form': CommentForm(),
        'comments': (
            Comment.objects
            .filter(post=post_obj)
            .order_by('created_at')
        )
    })


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create new post."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

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
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect(instance)
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect(instance)
    return render(request, 'blog/create.html', context)


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


def category(request, category_slug):
    """View published posts in category, if pub date less than now."""
    category_obj = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = (
        get_published(category_obj.posts)
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    paginator = Paginator(posts, 10)
    return render(request, 'blog/category.html', {
        'category': category_obj,
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


def profile(request, username):
    """View user's profile with posts."""
    user = get_object_or_404(User, username=username)
    if request.user.id == user.id:
        posts = (
            user.posts
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
    else:
        posts = (
            get_published(user.posts)
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )
    paginator = Paginator(posts, 10)
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


def edit_profile(request, username):
    """Update user's profile."""
    if not request.user.is_authenticated:
        return redirect('login')
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'blog/user.html', {
        'profile': user,
        'form': form
    })


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Create new comment."""

    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.post_obj.pk}
        )


class CommentUpdateView(UserPassesTestMixin, UpdateView):
    """Update comment."""

    post_id = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = kwargs['post_id']
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.post_id}
        )

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class CommentDeleteView(UserPassesTestMixin, DeleteView):
    """Delete comment."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
