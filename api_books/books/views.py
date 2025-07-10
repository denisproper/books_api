from django.db.models import Q
from django.http import HttpRequest
from rest_framework import generics, viewsets, mixins, views, status
from .paginations import TenItemsPagination
from .models import Author, Book, Order
from .serializers import BookSerializer, AuthorSerializer, OrderSerializer, RegisterSerializer
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser, 
    AllowAny, 
)
from .permissions import IsOwner, IsAdminOrReadOnly, IsOwnerOrAdmin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import BookFilter
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
    

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['genre', 'price', 'rating']

    search_fields = ['title', 'ISBN']
    pagination_class = TenItemsPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class OrderViewSet(
    mixins.ListModelMixin, 
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin, 
    viewsets.GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action in ['list', 'create']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
  

class SearchView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request: HttpRequest):
        query = request.query_params.get('q', '').strip()

        if not query:
            return Response({"books": [], "authors": []})
        
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(ISBN__icontains=query)
        )

        authors = Author.objects.filter(name__icontains=query)

        return Response({
            "books": BookSerializer(books, many=True).data,
            "authors": AuthorSerializer(authors, many=True).data
        })
    
class RegisterView(views.APIView):
    def post(self, request: HttpRequest):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



# class BookAPIListView(generics.ListCreateAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_class = BookFilter
#     search_fields = ['title', 'description']
#     ordering_fields = ['price', 'rating', 'created_at']
#     ordering = ['-created_at']
#     permission_classes = [IsAdminOrReadOnly]



# class BookDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer
#     permission_classes = [IsAdminOrReadOnly]



# class AuthorListAPIView(generics.ListCreateAPIView):
#     queryset = Author.objects.all()
#     serializer_class = AuthorSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['name', 'biography']
#     permission_classes = [IsAdminOrReadOnly]


# class AuthorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Author.objects.all()
#     serializer_class = AuthorSerializer
#     permission_classes = [IsAdminOrReadOnly]



# class OrderListAPIView(generics.ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)
    

# class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsOwnerOrAdmin]


#     def get_queryset(self):
#         return Order.objects.filter(user=self.request.user)