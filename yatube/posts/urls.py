from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from . import views


app_name = 'posts'

handler404 = 'core.views.page_not_found'

urlpatterns = [
    path('posts/<post_id>/edit/', views.post_edit, name='edit'),
    path('create/', views.post_create, name='create'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
