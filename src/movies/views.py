from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import json
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.generics import RetrieveAPIView
from src.movies.serializers import MovieSerializer, CreateMovieSerializer, CommentSerializer, WatchListSerializer
from src.movies.models import Movie, Genre, Likes, Comment, WatchList
from django.core import serializers
from rest_framework import status
from django.conf import settings
from itertools import chain
from django.db import connection
from django.db.models import Prefetch
from django.core.paginator import Paginator
from src.users.serializers import UserSerializer
import datetime
import operator


class MovieViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                  mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates, Updates and Retrieves - User Accounts
    """
    serializers = {
        'default': MovieSerializer,
        'create': CreateMovieSerializer
    }
    permissions = {
        'default': (IsAuthenticated,),
        'create': (IsAuthenticated,)
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['default'])

    def get_permissions(self):
        self.permission_classes = self.permissions.get(self.action, self.permissions['default'])
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='create-movie', url_name='create-movie')
    def create_movie(self, instance):
        try:
            movie = self.request.data
            title = movie['title']
            description = movie['description']
            image_url = movie['image_url']
            genre_id = movie['genre_id']
            Movie.objects.create(title=title, description=description, image_url=image_url, visit_count=0, genre_id=genre_id)
            return Response(list(Movie.objects.filter().values()), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create movie error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create-comment', url_name='create-comment')
    def create_comment(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            comment = self.request.data
            content = comment['content']
            movie_id = comment['movie_id']
            timestamp = datetime.datetime.now()
            Comment.objects.create(content=content, movie_id=movie_id, timestamp=timestamp, user_id=user_id)
            comments = Comment.objects.filter(movie_id=movie_id, user_id=user_id, timestamp=timestamp, content=content)
            comSerializer = CommentSerializer(comments, many=True)
            return Response(comSerializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create movie error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='visit-movie', url_name='visit-movie')
    def visit_movie(self, instance):
        try:
            movie_id = self.request.GET.get("id")
            movie = Movie.objects.get(id=movie_id)
            movie.visit_count = movie.visit_count + 1
            movie.save()
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            queryset = Movie.objects.filter(id=movie_id)
            comments = Comment.objects.filter(movie_id=self.request.GET.get("id"))
            comSerializer = CommentSerializer(comments, many=True)
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            comSerializer.data.sort(reverse=True, key=lambda e: e['timestamp'])
            return Response({"data": serializer.data, "comments": comSerializer.data[::-1][:10]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create movie error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create-genre', url_name='create-genre')
    def create_genre(self, instance):
        try:
            genre = self.request.data
            name = genre['name']
            Genre.objects.create(name=name)
            return Response(list(Genre.objects.filter().values()), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create genre error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='watch', url_name='watch')
    def watch_list_action(self, instance):
        try:
            data = self.request.data
            movie_id = data['movie_id']
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]

            try:
                dataExists = WatchList.objects.filter(movie_id=movie_id, user_id=user_id)
                if dataExists:
                    dataExists.delete()
                    return Response({"data": False, "id": movie_id}, status=status.HTTP_200_OK)
            except Exception:
                pass

            WatchList.objects.create(movie_id=movie_id, user_id=user_id)
            return Response({"data": True, "id": movie_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create genre error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='watch-list', url_name='watch-list')
    def get_watch_list(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            watch_list = WatchList.objects.filter(user_id=user_id)
            serializer = WatchListSerializer(watch_list, context={'user_id': user_id}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='related', url_name='related')
    def get_related(self, instance):
        try:
            genre_id = self.request.GET.get('id')
            related = Movie.objects.filter(genre_id=genre_id).values()[:10]
            return Response(related, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movies', url_name='movies')
    def get_movies(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            genres = Genre.objects.filter().values()
            queryset = Movie.objects.all()
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            length = len(list(serializer.data))
            paginator = Paginator(serializer.data, 10)
            page_number = self.request.GET.get("page")
            page_obj = paginator.page(page_number)
            popular = serializer.data
            popular.sort(reverse=True, key=lambda e: e['num_of_likes'])
            return Response({"data": list(page_obj), "length": length, "genres": genres, "popular": popular[:10]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='popular', url_name='popular')
    def get_popular(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            queryset = Movie.objects.all()
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            lista = serializer.data
            lista.sort(reverse=True, key=lambda e: e['num_of_likes'])
            return Response(lista[:10], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movies-by-title', url_name='movies-by-title')
    def get_movies_by_title(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            genres = Genre.objects.filter().values()
            queryset = Movie.objects.filter(title__icontains=self.request.GET.get("title"))
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            length = len(list(serializer.data))
            paginator = Paginator(serializer.data, 10)
            page_number = self.request.GET.get("page")
            page_obj = paginator.page(page_number)
            popular = serializer.data
            popular.sort(reverse=True, key=lambda e: e['num_of_likes'])
            return Response({"data": list(page_obj), "length": length, "genres": genres, "popular": popular[:10]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movies-by-genre', url_name='movies-by-genre')
    def get_movies_by_genre(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            queryset = Movie.objects.filter(genre_id=self.request.GET.get("id"))
            genres = Genre.objects.filter().values()
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            length = len(list(serializer.data))
            paginator = Paginator(serializer.data, 10)
            page_number = self.request.GET.get("page")
            page_obj = paginator.page(page_number)
            popular = serializer.data
            popular.sort(reverse=True, key=lambda e: e['num_of_likes'])
            return Response({"data": list(page_obj), "length": length, "genres": genres, "popular": popular[:10]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movie', url_name='movie')
    def get_movie(self, instance):
        try:
            movie_id = self.request.GET.get("id")
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            comments = Comment.objects.filter(movie_id)
            comSerializer = CommentSerializer(comments, many=True)
            queryset = Movie.objects.filter(id=self.request.GET.get("id"))
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            comSerializer.data.sort(reverse=True, key=lambda e: e['timestamp'])
            return Response({"data": serializer.data, "comments": comSerializer.data[::-1][:10]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movie error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movie-comments', url_name='movie-comments')
    def get_movie_comments(self, instance):
        try:
            comments = Comment.objects.filter(movie_id=self.request.GET.get("id"))
            comSerializer = CommentSerializer(comments, many=True)
            comSerializer.data.sort(reverse=True, key=lambda e: e['timestamp'])
            return Response(comSerializer.data[::-1], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movie error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='genres', url_name='genres')
    def get_genres(self, instance):
        try:
            queryset = Genre.objects.filter().values()
            genre_list = list(queryset)
            return Response(genre_list, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get genres  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='like', url_name='like')
    def like_movie(self, instance):
        try:
            user_id = UserSerializer(self.request.user, context={'request': self.request}).data["id"]
            data = self.request.data
            movie_id = data['movie_id']
            stat = data['status']
            try:
                likeExists = Likes.objects.get(movie_id=movie_id, user_id=user_id, status=stat)
                if likeExists:
                    likeExists.delete()
                queryset = Movie.objects.filter(id=movie_id)
                serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception:
                pass
            Likes.objects.create(movie_id=movie_id, user_id=user_id, status=stat)
            queryset = Movie.objects.filter(id=movie_id)
            serializer = MovieSerializer(queryset, context={'user_id': user_id}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Like movie error ' + e}, status=status.HTTP_400_BAD_REQUEST)
