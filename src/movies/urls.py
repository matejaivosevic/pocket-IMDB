from django.urls import path

from . import views

urlpatterns = [
    path('movies', views.MovieViewSet.as_view({'get': 'get_movies'}), name='movies'),
    path('movie', views.MovieViewSet.as_view({'get': 'get_movie'}), name='movie'),
    path('genres', views.MovieViewSet.as_view({'get': 'get_genres'}), name='genres'),
    path('create-movie', views.MovieViewSet.as_view({'post': 'create_movie'}), name='create-movie'),
    path('create-genre', views.MovieViewSet.as_view({'post': 'create_genre'}), name='create-genre'),
    path('like', views.MovieViewSet.as_view({'put': 'like_movie'}), name='like')
]
