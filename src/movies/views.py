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
from src.movies.serializers import MovieSerializer, CreateMovieSerializer
from src.movies.models import Movie, Genre, Likes
from django.core import serializers
from rest_framework import status
from django.conf import settings
from itertools import chain
from django.db import connection
from django.db.models import Prefetch
from django.core.paginator import Paginator


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

    @action(detail=False, methods=['post'], url_path='create-genre', url_name='create-genre')
    def create_genre(self, instance):
        try:
            genre = self.request.data
            name = genre['name']
            Genre.objects.create(name=name)
            return Response(list(Genre.objects.filter().values()), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Create genre error ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movies', url_name='movies')
    def get_movies(self, instance):
        try:
            queryset = Movie.objects.all()
            serializer = MovieSerializer(queryset, many=True)
            length = len(list(serializer.data))
            paginator = Paginator(serializer.data, 10)
            page_number = self.request.GET.get("page")
            page_obj = paginator.page(page_number)
            return Response({"data": list(page_obj), "length": length}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Get movies  error  ' + e}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='movie', url_name='movie')
    def get_movie(self, instance):
        try:
            queryset = Movie.objects.filter(id=self.request.GET.get("id"))
            serializer = MovieSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
            data = self.request.data
            movie_id = data['movie_id']
            user_id = data['user_id']
            status = data['status']
            try:
                likeExists = Likes.objects.get(movie_id=movie_id, user_id=user_id)
                if likeExists:
                    likeExists.delete()
                queryset = Movie.objects.all()
                serializer = MovieSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception:
                pass
            Likes.objects.create(movie_id=movie_id, user_id=user_id, status=1)
            queryset = Movie.objects.all()
            serializer = MovieSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Like movie error ' + e}, status=status.HTTP_400_BAD_REQUEST)
