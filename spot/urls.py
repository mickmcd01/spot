from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:term>/top_tracks/', views.top_tracks, name='top_tracks'),
    path('<str:term>/top_artists/', views.top_artists, name='top_artists'),
    path('recent_tracks/', views.recent_tracks, name='recent_tracks'),
    path('<str:id>/artist_detail/', views.artist_detail, name='artist_detail')

]