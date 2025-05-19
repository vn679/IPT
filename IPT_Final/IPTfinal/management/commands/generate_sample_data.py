from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from IPTfinal.models import SalesData, ProjectStatus, TodoItem, RevenueMetrics, VisitorMetrics
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Generates sample data for the dashboard'

    def handle(self, *args, **kwargs):
        # Create a superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser'))

        # Generate sales data
        products = ['Electronics', 'Clothing', 'Books', 'Food', 'Furniture']
        for i in range(30):  # 30 days of sales
            date = timezone.now().date() - timedelta(days=i)
            for _ in range(random.randint(1, 5)):  # 1-5 sales per day
                SalesData.objects.create(
                    date=date,
                    amount=random.uniform(100, 1000),
                    product_category=random.choice(products)
                )

        # Generate project data
        project_names = [
            'Website Redesign', 'Mobile App Development', 'Database Migration',
            'Cloud Integration', 'Security Audit', 'UI/UX Improvement'
        ]
        for name in project_names:
            ProjectStatus.objects.create(
                name=name,
                status=random.choice(['ongoing', 'completed', 'delayed']),
                progress=random.randint(0, 100),
                deadline=timezone.now().date() + timedelta(days=random.randint(1, 90))
            )

        # Generate todo items
        todo_items = [
            'Review project proposal', 'Update documentation', 'Client meeting',
            'Code review', 'Team standup', 'Deploy updates'
        ]
        user = User.objects.first()
        for item in todo_items:
            TodoItem.objects.create(
                user=user,
                title=item,
                completed=random.choice([True, False])
            )

        # Generate revenue metrics
        for i in range(30):  # 30 days of revenue data
            date = timezone.now().date() - timedelta(days=i)
            revenue = random.uniform(5000, 15000)
            expenses = random.uniform(3000, 8000)
            RevenueMetrics.objects.create(
                date=date,
                total_revenue=revenue,
                expenses=expenses,
                net_profit=revenue - expenses
            )

        # Generate visitor metrics
        for i in range(30):  # 30 days of visitor data
            date = timezone.now().date() - timedelta(days=i)
            views = random.randint(1000, 5000)
            visitors = random.randint(500, views)
            VisitorMetrics.objects.create(
                date=date,
                page_views=views,
                unique_visitors=visitors,
                bounce_rate=random.uniform(20, 80)
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated sample data')) 