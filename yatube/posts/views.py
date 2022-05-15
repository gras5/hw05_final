from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    posts = Post.objects.select_related('author', 'group')

    paginator = Paginator(posts, settings.POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')

    paginator = Paginator(posts, settings.POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    posts_number = posts.count()

    paginator = Paginator(posts, settings.POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_follow = (
        request.user.follower.filter(
            author__username=username
        ).exists()
        if request.user.is_authenticated
        else False
    )

    context = {
        'author': author,
        'posts_number': posts_number,
        'page_obj': page_obj,
        'following': is_follow,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        pk=post_id
    )
    post_comments = post.comments.select_related('author')
    author_posts_number = post.author.posts.count()

    context = {
        'form': CommentForm(request.POST or None),
        'post': post,
        'author_posts_number': author_posts_number,
        'comments': post_comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    context = {
        'title_text': 'Новый пост',
        'card_header_text': 'Новый пост',
        'button_text': 'Добавить',
    }

    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)

    context['form'] = form
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    context = {
        'title_text': 'Редактировать пост',
        'card_header_text': 'Редактировать пост',
        'button_text': 'Сохранить',
        'edited_post_id': post.pk,
    }

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)

    context['form'] = form
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        pk=post_id
    )

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related().filter(
        author__following__user=request.user)

    paginator = Paginator(posts, settings.POSTS_DISPLAYED)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):

    is_follow = request.user.follower.filter(
        author__username=username).exists()

    if not is_follow and request.user.username != username:
        follow = Follow.objects.create(
            user=request.user,
            author=User.objects.get(username=username)
        )
        follow.save()

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    is_follow = request.user.follower.filter(
        author__username=username).exists()

    if is_follow:
        follow = Follow.objects.get(
            user=request.user,
            author__username=username
        )

        follow.delete()

    return redirect('posts:profile', username=username)
