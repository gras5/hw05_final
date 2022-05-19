from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def get_page_object(posts, page_number):
    paginator = Paginator(posts, settings.POSTS_DISPLAYED)
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.select_related('author', 'group')

    page_number = request.GET.get('page')
    page_obj = get_page_object(posts, page_number)

    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')

    page_number = request.GET.get('page')
    page_obj = get_page_object(posts, page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')

    page_number = request.GET.get('page')
    page_obj = get_page_object(posts, page_number)

    is_follow = (
        request.user.is_authenticated
        and request.user.follower.filter(author__username=username).exists()
    )

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': is_follow,
        'posts_number': page_obj.paginator.count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'group', 'author').prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.select_related('author')
                )
        ),
        pk=post_id
    )

    author_posts_number = post.author.posts.count()

    context = {
        'form': CommentForm(),
        'post': post,
        'author_posts_number': author_posts_number,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)

    context = {
        'title_text': 'Новый пост',
        'button_text': 'Добавить',
        'form': form,
    }

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.prefetch_related(
            'author'
        ),
        pk=post_id
    )

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    context = {
        'title_text': 'Редактировать пост',
        'button_text': 'Сохранить',
        'edited_post_id': post.pk,
        'form': form,
    }

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@ login_required
def follow_index(request):
    posts = Post.objects.select_related().filter(
        author__following__user=request.user)

    page_number = request.GET.get('page')
    page_obj = get_page_object(posts, page_number)

    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@ login_required
def profile_follow(request, username):

    is_follow = request.user.follower.filter(
        author__username=username).exists()

    author_user = User.objects.get(username=username)

    if not is_follow and request.user != author_user:
        follow = Follow.objects.create(
            user=request.user,
            author=User.objects.get(username=username)
        )
        follow.save()

    return redirect('posts:profile', username=username)


@ login_required
def profile_unfollow(request, username):

    follow = Follow.objects.filter(
        user=request.user,
        author__username=username
    )

    follow.delete()

    return redirect('posts:profile', username=username)
