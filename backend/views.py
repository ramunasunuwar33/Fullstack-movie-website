from django.shortcuts import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes,authentication_classes,parser_classes
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from .models import *
from django_filters import rest_framework as filters
from django.conf import settings
from .authentication import CookiesJWTAuthentication
from datetime import datetime
import io
from collections import Counter
import random
import zipfile
from rest_framework.parsers import MultiPartParser
import pandas as pd
from django.core.files.base import ContentFile
#Create your views here.

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            seriliazer = UserSerializer(request.user, many=False)

            res = Response()

            res.data = {'success':True}

            res.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            res.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            res.data.update(tokens)
            return res
        
        except Exception as e:
            print(e)
            return Response({'success':False})
        
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)
            
            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='None',
                path='/'
            )
            return res

        except Exception as e:
            print(e)
            return Response({'refreshed': False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):

    try:

        res = Response()
        res.data = {'success':True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('response_token', path='/', samesite='None')

        return res

    except Exception as e:
        print(e)
        return Response({'success':False})

class MoviesFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    category = filters.ChoiceFilter(choices=Movies.CATEGORY.choices)
    rating = filters.NumberFilter(lookup_expr='gte')
    is_premium = filters.BooleanFilter()
    release_date = filters.DateTimeFromToRangeFilter()
    class Meta:
        model = Movies
        fields = ['title', 'category', 'rating', 'is_premium', 'release_date']


class ListMovies(generics.ListCreateAPIView):
    queryset=Movies.objects.all()
    serializer_class = MovieSerializer
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MoviesFilter

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create a movie.")
        serializer.save()

class UpdateDetailMovie(generics.RetrieveUpdateDestroyAPIView):
    queryset=Movies.objects.all()
    serializer_class=MovieSerializer
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]
    lookup_field='pk'
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        try:
            WatchHistory.objects.update_or_create(
                user=request.user,
                movie=instance,
                defaults={'watched_at': datetime.now()}
            )
        except Exception as e:
            print("Failed to create WatchHistory:", e)
        
        return Response(serializer.data)

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update this movie.")
        
        serializer.save()

class TypeCreateListView(generics.ListCreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    authentication_classes = [CookiesJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create a type.")
        serializer.save()

class TypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    authentication_classes = [CookiesJWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update this type.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this type.")
        instance.delete()


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class= UserSerializer
    permission_classes=[AllowAny]

class SearchMovie(generics.ListAPIView):
    queryset=Movies.objects.all()
    serializer_class = MovieSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields=['title']
    def get_queryset(self):
        qs = Movies.objects.all()
        title = self.request.query_params.get('title')
        if title is not None:
            qs=qs.filter(title__icontains=title)
        return qs
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]
    serializer_class=UserProfileSerializer
    
    def get_queryset(self):
        user = UserProfile.objects.get(user=self.request.user)
        return user
    
    def get_object(self):
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    def perform_update(self,serializer):
        if serializer.is_valid(raise_exception=True):
            userprofile = self.request.user.userprofile
            self.request.user.userprofile.image.delete()
            self.request.user.first_name = userprofile.first_name
            self.request.user.last_name= userprofile.last_name
            self.request.user.email=userprofile.email
            self.request.user.save()
        serializer.save()

class CastCreateListView(generics.ListCreateAPIView):
    queryset = Cast.objects.all()
    serializer_class=CastSerializer
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]

class CastListView(APIView):
    def get(self, request, movie_id):
        cast = Cast.objects.filter(movies__id=movie_id)
        serializer = CastSerializer(cast, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = CastSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CastUpdateView(generics.RetrieveUpdateAPIView):
    queryset=Cast.objects.all()
    serializer_class=CastSerializer
    authenticatoin_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]
    lookup_field='pk'
    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update this cast.")
        serializer.save()

@api_view(['GET'])
@authentication_classes([CookiesJWTAuthentication])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)



class MovieSearchView(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        qs = Movies.objects.all()

        title = self.request.query_params.get('title')
        release_year = self.request.query_params.get('release_year')
        category = self.request.query_params.get('category')
        min_rating = self.request.query_params.get('min_rating')

        if title is not None:
            qs = qs.filter(title__icontains=title)

        if release_year:
            qs = qs.filter(release_date__year=release_year)

        if category:
            if category in dict(Movies.CATEGORY.choices):
                qs = qs.filter(category=category)

        if min_rating:
            try:
                qs = qs.filter(rating__gte=float(min_rating))
            except ValueError:
                pass  # Ignore invalid number
        print(qs)
        return qs

@api_view(['POST'])
@parser_classes([MultiPartParser])
def bulk_upload_movies_zip(request):
    zip_file = request.FILES.get('file')
    if not zip_file.name.endswith('.zip'):
        return Response({'error': 'Only .zip files are allowed'}, status=status.HTTP_400_BAD_REQUEST)

    # Unzip to memory
    with zipfile.ZipFile(zip_file) as zf:
        file_names = zf.namelist()
        print(zf.namelist())
        if 'movies.csv' not in file_names:
            return Response({'error': 'CSV file "movies.csv" not found in ZIP'}, status=400)

        # Read CSV
        csv_bytes = zf.read('movies.csv')
        print(csv_bytes[:20])
        df = pd.read_csv(io.BytesIO(csv_bytes), encoding='utf-8', engine='python')

        created_movies = []

        for _, row in df.iterrows():
            title = row['title']
            description = row['desc']
            category = row['category']
            rating = row['rating']
            release_date=row['release_date']
            is_premium=row['is_premium']
            image_name = row['image']
            video_name = row['video']
            banner_name= row['banner']
            # cast_names = str(row['cast']).split('|')
            # cast_image_names = str(row['cast_image']).split('|')

            image_file = zf.open(image_name)
            video_file = zf.open(video_name)
            banner_file = zf.open(banner_name)

            movie = Movies(
                title=title,
                desc=description,
                category=category,
                rating=rating,
                release_date=release_date,
                is_premium=is_premium
            )
            movie.image.save(image_name, ContentFile(image_file.read()),save=False)
            movie.video.save(video_name, ContentFile(video_file.read()),save=False)
            movie.banner.save(banner_name,ContentFile(banner_file.read()),save=False)
            movie.save()
            

            # for cast_name, cast_image_name in zip(cast_names, cast_image_names):
            #     cast_name = cast_name.strip()
            #     cast_obj, created = Cast.objects.get_or_create(name=cast_name)
            #     cast_obj.movies.add(movie)

            #     if cast_image_name and cast_image_name in file_names:
            #         cast_image_file = zf.open(cast_image_name)
            #         cast_obj.image.save(cast_image_name, ContentFile(cast_image_file.read()), save=False)

            #     cast_obj.save()
                    

            
            created_movies.append(movie.title)

        return Response({'success': f"{len(created_movies)} movies uploaded", 'movies': created_movies}, status=201)

class HistoryRetrieveView(generics.ListAPIView):
    serializer_class=WatchHistorySerializer
    authentication_classes=[CookiesJWTAuthentication]
    permission_classes=[IsAuthenticated]


    def get_queryset(self):
        return WatchHistory.objects.filter(user=self.request.user)

class WatchlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).order_by('-added_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WatchlistDeleteView(generics.DestroyAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        recent_movies = WatchHistory.objects.filter(user=user).order_by('-watched_at')[:10]
        category_counter = Counter()

        for record in recent_movies:
            if record.movie.category:
                category_counter[record.movie.category] += 1

        recommended_movies = []
        seen_movie_ids = set(w.movie.id for w in WatchHistory.objects.filter(user=user))

        for category, count in category_counter.items():
            fetch_count = int(count * 1.5)
            category_movies = Movies.objects.filter(category=category)#.exclude(id__in=seen_movie_ids)
            sampled = random.sample(list(category_movies), min(len(category_movies), fetch_count))
            recommended_movies.extend(sampled)


        random.shuffle(recommended_movies)

        serialized = MovieSerializer(recommended_movies, many=True)
        return Response(serialized.data)