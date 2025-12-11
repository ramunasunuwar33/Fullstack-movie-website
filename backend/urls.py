from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('movies/',views.ListMovies.as_view(),name="list_create_movies"),
    path('movies/<int:pk>/',views.UpdateDetailMovie.as_view(),name="update_detail_movie"),
    path('movies/search/',views.SearchMovie.as_view(),name="search_movie"),
    path('register/',views.CreateUserView.as_view(),name="register"),
    path('token/',views.CustomTokenObtainPairView.as_view(),name="token"),
    path('token/refresh/',views.CustomTokenRefreshView.as_view(),name="refresh"),
    path('logout/',views.logout,name="logout"),
    path('authenticated/',views.is_logged_in,name='is_authenticated'),
    path('user_profile/',views.UserProfileView.as_view(),name="user_profile"),
    path('type/',views.TypeCreateListView.as_view(),name="create_type"),
    path('update_type/<int:pk>/',views.TypeDetailView.as_view(),name="update_type"),
    path('movies/<int:movie_id>/cast/',views.CastListView.as_view(),name="create_cast"),
    path('cast/',views.CastCreateListView.as_view(),name='list_cast'),
    path('update_cast/<int:pk>/',views.CastUpdateView.as_view(),name="update_cast"),
    path('history/',views.HistoryRetrieveView.as_view(),name="history"),
    path('watchlist/', views.WatchlistListCreateView.as_view(), name='watchlist'),
    path('watchlist/<int:pk>/', views.WatchlistDeleteView.as_view(), name='watchlist-delete'),

    path('movies/bulk-upload/',views.bulk_upload_movies_zip,name='bulk_upload'),
    path('recommendations/', views.RecommendationView.as_view(), name='recommendations'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
