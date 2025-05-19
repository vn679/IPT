from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SalesData(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.date} - {self.product_category}: ${self.amount}"

class ProjectStatus(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
    ]
    
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.IntegerField(default=0)  # Percentage complete
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.status}"

class TodoItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class RevenueMetrics(models.Model):
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    expenses = models.DecimalField(max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.date} - Revenue: ${self.total_revenue}"

class VisitorMetrics(models.Model):
    date = models.DateField()
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2)  # Stored as percentage
    
    def __str__(self):
        return f"{self.date} - Views: {self.page_views}, Visitors: {self.unique_visitors}"

class Room(models.Model):
    ROOM_CHOICES = [
        ('Room A', 'Room A'),
        ('Room B', 'Room B'),
        ('Room C', 'Room C'),
        ('Room D', 'Room D'),
    ]
    
    name = models.CharField(max_length=100, choices=ROOM_CHOICES)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Reservation(models.Model):
    COURSE_CHOICES = [
        ('IT', 'Information Technology'),
        ('ENTREP', 'Entrepreneurship'),
        ('EDUC', 'Education'),
        ('ECE', 'Electronics Engineering'),
        ('BSAD', 'Business Administration'),
        ('BSIS', 'Information Systems')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    num_attendees = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.room.name} - {self.start_time}"

class Notification(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return self.message 