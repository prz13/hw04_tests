from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'posts'

urlpatterns = [
    path('posts/<post_id>/edit/', views.post_edit, name='edit'),
    path('create/', views.post_create, name='create'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('', views.index, name='index'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
