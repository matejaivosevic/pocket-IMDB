from django.urls import path

from . import views

urlpatterns = [
    path('movies', views.MovieViewSet.as_view({'get': 'get_movies'}), name='movies'),
    path('movies-by-title', views.MovieViewSet.as_view({'get': 'get_movies_by_title'}), name='movies-by-title'),
    path('popular', views.MovieViewSet.as_view({'get': 'get_popular'}), name='popular'),
    path('watch', views.MovieViewSet.as_view({'put': 'watch_list_action'}), name='watch'),
    path('watch-list', views.MovieViewSet.as_view({'get': 'get_watch_list'}), name='watch-list'),
    path('movies-by-genre', views.MovieViewSet.as_view({'get': 'get_movies_by_genre'}), name='movies-by-genre'),
    path('movie-comments', views.MovieViewSet.as_view({'get': 'get_movie_comments'}), name='movie-comments'),
    path('visit-movie', views.MovieViewSet.as_view({'patch': 'visit_movie'}), name='visit-movie'),
    path('movie', views.MovieViewSet.as_view({'get': 'get_movie'}), name='movie'),
    path('genres', views.MovieViewSet.as_view({'get': 'get_genres'}), name='genres'),
    path('create-movie', views.MovieViewSet.as_view({'post': 'create_movie'}), name='create-movie'),
    path('create-genre', views.MovieViewSet.as_view({'post': 'create_genre'}), name='create-genre'),
    path('create-comment', views.MovieViewSet.as_view({'post': 'create_comment'}), name='create-comment'),
    path('like', views.MovieViewSet.as_view({'put': 'like_movie'}), name='like')
]
