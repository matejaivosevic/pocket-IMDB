from rest_framework import serializers

from src.movies.models import Movie, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'id',
            'name',
        )


class MovieSerializer(serializers.ModelSerializer):

    genre = GenreSerializer(many=False, read_only=True)

    num_of_likes = serializers.SerializerMethodField()

    num_of_dislikes = serializers.SerializerMethodField()

    def get_num_of_likes(self, obj):
        return obj.likes.filter(status=1).count()

    def get_num_of_dislikes(self, obj):
        return obj.likes.filter(status=0).count()

    class Meta:
        model = Movie
        fields = (
            'id',
            'title',
            'description',
            'image_url',
            'visit_count',
            'genre',
            'num_of_likes',
            'num_of_dislikes'
        )

class CreateMovieSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        movie = Movie.objects.create(**validated_data)
        return movie

    class Meta:
        model = Movie
        fields = (
            'title',
            'desription',
            'image_url',
            'visit_count',
            'genre_id'
        )