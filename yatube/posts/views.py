from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import PostForm
from .models import Post, Group


User = get_user_model()


POST_LIST_LIMIT = 10


def index(request):
    title = 'Последние обновления на сайте'
    post_list = Post.objects.select_related('group', 'author')
    paginator = Paginator(post_list, POST_LIST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = 'Записи сообщества'
    post_list = group.posts.select_related()
    paginator = Paginator(post_list, POST_LIST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_number': page_number,
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    title = 'Профаил пользователя {username}'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    paginator = Paginator(post_list, POST_LIST_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'author': author,
        'title': title,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    title = 'Пост {post.text}'
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'title': title,
        'posts_count': posts_count,
        'requser': request.user,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = 'Добавить запись'
    form = PostForm(request.POST or None)
    context = {'title': title}
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    title = 'Редактировать запись'
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, 
                    files=request.FILES or None, 
                    instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'title': title,
    }
    return render(request,
                template,
                context)

@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id) 
