from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Book, Author, Order, OrderItem


class BookShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title']


class AuthorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), many=True, write_only=True
    )
    authors = AuthorShortSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['title', 'description', 'price', 'genre', 
                  'year', 'quantity', 'rating', 'ISBN', 'authors', 'author_ids']
        

    def validate_year(self, value):
        current_year = datetime.now().year
        if value < 1800 or value > current_year:
            raise serializers.ValidationError(f"Year must be between 1800 and {current_year}")
        return value
    
    def validate_ISBN(self, value: str):
        if not value.replace('-', '').isdigit() or len(value.replace('-', '')) not in [10, 13]:
            raise serializers.ValidationError("Invalid ISBN format")
        return value 
    
    def validate(self, data):
        if not self.instance and not self.initial_data.get('author_ids'):
            raise serializers.ValidationError({"authors": "At least one author must be provided."})
        return data
    

    def create(self, validated_data):
        authors = validated_data.pop('author_ids')
        book = Book.objects.create(**validated_data)
        book.authors.set(authors)
        book.save()
        return book


    def update(self, instance, validated_data):
        authors = validated_data.pop('author_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if authors is not None:
            instance.authors.set(authors)
        return instance


class AuthorSerializer(serializers.ModelSerializer):
    books = BookShortSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['name', 'biography', 'birth_date', 'books']

    def validate_birth_date(self, value):
        current_year = datetime.now().year
        if value.year > current_year:
            raise serializers.ValidationError('f"Year must be less than {current_year}"')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)
    book = BookShortSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=7, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['book_id', 'book', 'quantity', 'price'] 

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate(self, data):
        book = data.get('book_id')
        quantity = data.get('quantity')
        if book and book.quantity < quantity:
            raise serializers.ValidationError("Not enough books in stock.")
        return data
 

    def create(self, validated_data):
        book = validated_data['book_id']
        validated_data['book'] = book
        validated_data['price'] = book.price
        return super().create(validated_data)
    


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price',
                 'created_at', 'address', 'items']

    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value
    

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(total_price=0, **validated_data)

        total = 0
        for item_data in items_data:
            book = item_data['book_id']
            quantity = item_data['quantity']
            price = book.price
            total += price * quantity
            OrderItem.objects.create(order=order, book=book, quantity=quantity, price=price)

            book.quantity -= quantity
            book.save()

        order.total_price = total
        order.save()
        return order
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(
             username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )