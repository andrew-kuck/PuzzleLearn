from django.urls import path

from . import views

urlpatterns = [
    path('api/generate-nba-question/', views.generate_nba_question, name='generate_nba_question'),
    path('api/gutenberg-text/', views.fetch_gutenberg_text, name='fetch_gutenberg_text'),
    path('api/get-geo-data/', views.get_geo_data, name='get_geo_data'),
    path('', views.index, name='index'),
    path('<path:url_path>', views.page, name='page'),
]