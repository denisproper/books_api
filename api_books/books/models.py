from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class Genre(models.TextChoices):
    FANTASY = 'fantasy', 'Фантастика'
    DETECTIVE = 'detective', 'Детектив'
    ROMANCE = 'romance', 'Романтика'
    DRAMA = 'drama', 'Драма'
    MYSTERY = 'mystery', 'Мистика'
    OTHER = 'other', 'Другое'

class Status(models.TextChoices):
    CREATED = 'created', 'Создан'
    PAID = 'paid', 'Оплачен'
    SENT = 'sent', 'Отправлен'
    DELIVERED = 'delivered', 'Доставлен'


class Author(models.Model):
    name = models.CharField(max_length=50)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    books = models.ManyToManyField(to='Book', related_name='authors')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    genre = models.CharField(
        max_length=20, 
        choices=Genre.choices, 
        default=Genre.OTHER
    )
    year = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=2, decimal_places=1, 
                                 validators=[MinValueValidator(0), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ISBN = models.CharField(max_length=13,
                            validators=[RegexValidator(r'^\d{13}$')],
                            unique=True)

    def __str__(self):
        return self.title



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='orders')
    status = models.CharField(
        max_length=10,
        choices=Status.choices, 
        default=Status.CREATED
    )
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    books = models.ManyToManyField('Book',
                                   through='OrderItem',
                                   related_name='orders')
    def __str__(self):
        return f'{self.user}'

class OrderItem(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE, 
                             related_name='order_items')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
