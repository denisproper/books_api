from django.urls import include, path 
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='books')
router.register(r'authors', views.AuthorViewSet, basename='authors')
router.register(r'orders', views.OrderViewSet, basename='orders')


urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.SearchView.as_view()),
    
    # path('books/', views.BookAPIListView.as_view()),
    # path('books/<int:pk>/', views.BookDetailAPIView.as_view()),
    # path('authors/', views.AuthorListAPIView.as_view()),
    # path('authors/<int:pk>/', views.AuthorDetailAPIView.as_view()),
    # path('orders/', views.OrderListAPIView.as_view()),
    # path('orders/<int:pk>', views.OrderDetailAPIView.as_view()),
]
