from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models import SalesData, ProjectStatus, TodoItem, RevenueMetrics, VisitorMetrics, Room, Reservation, Notification
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime
from .forms import (
    SalesDataForm, ProjectStatusForm, TodoItemForm,
    RevenueMetricsForm, VisitorMetricsForm, ReservationForm
)

# Landing page (index.html at the root of templates)
def home(request):
    # Get current date and time
    current_datetime = timezone.now()
    
    # First update completed reservations
    Reservation.objects.filter(
        end_time__lte=current_datetime,
        status__in=['pending', 'ongoing']
    ).update(status='completed')
    
    # Then update ongoing reservations
    Reservation.objects.filter(
        start_time__lte=current_datetime,
        end_time__gt=current_datetime,
        status='pending'
    ).update(status='ongoing')
    
    # Get recent reservations with proper status
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    # Format recent reservations for display/JSON
    formatted_reservations = []
    for res in recent_reservations:
        # Determine current status based on time
        if res.end_time <= current_datetime:
            current_status = 'completed'
        elif res.start_time <= current_datetime and res.end_time > current_datetime:
            current_status = 'ongoing'
        else:
            current_status = 'pending'
        
        # Update status if it's different
        if res.status != current_status:
            res.status = current_status
            res.save()
        
        formatted_reservations.append({
            'id': res.id,
            'name': res.name,
            'start_time': res.start_time.strftime('%B %d, %Y at %I:%M %p'),
            'end_time': res.end_time.strftime('%I:%M %p'),
            'num_attendees': res.num_attendees,
            'course': res.get_course_display(),
            'status': current_status,
            'status_display': dict(Reservation.STATUS_CHOICES)[current_status]
        })
    
    # Calculate total reservations and available rooms
    total_reservations = Reservation.objects.count()
    unavailable_room_ids = Reservation.objects.filter(
        start_time__lte=current_datetime,
        end_time__gt=current_datetime,
        status__in=['pending', 'ongoing']
    ).values_list('room_id', flat=True)
    available_rooms = Room.objects.exclude(id__in=unavailable_room_ids).count()
    ongoing_reservations = Reservation.objects.filter(status='ongoing').count()
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Calculate reservations per week with proper day names
    week_ago = current_datetime.date() - timedelta(days=7)
    daily_reservations = (
        Reservation.objects
        .filter(start_time__date__gte=week_ago)
        .values('start_time__date')
        .annotate(count=Count('id'))
        .order_by('start_time__date')
    )

    # Ensure all days of the week are represented
    days_of_week = []
    reservation_counts = {}
    reservation_counts_list = []
    
    for i in range(7):
        date = current_datetime.date() - timedelta(days=6-i)
        day_name = date.strftime('%A')
        days_of_week.append(day_name)
        reservation_counts[day_name] = 0
        
    for entry in daily_reservations:
        day_name = entry['start_time__date'].strftime('%A')
        if day_name in reservation_counts:
            reservation_counts[day_name] = entry['count']
    
    # Create list of counts in the same order as days
    for day in days_of_week:
        reservation_counts_list.append(reservation_counts[day])

    # Calculate course distribution for pie chart
    course_map = {
        'IT': 0,
        'ENTREP': 0,
        'EDUC': 0,
        'ECE': 0,
        'BSAD': 0,
        'BSIS': 0
    }
    
    course_counts = (
        Reservation.objects
        .values('course')
        .annotate(total=Count('id'))
    )
    
    # Update counts from database
    for stat in course_counts:
        course = stat['course']  # This is the actual course code from the choices
        if course in course_map:
            course_map[course] = stat['total']
    
    # Calculate percentages
    total_course_count = sum(course_map.values())
    course_percentages = {}
    for course, count in course_map.items():
        percentage = 0 if total_course_count == 0 else round((count / total_course_count) * 100, 1)
        course_percentages[course] = percentage
    
    # Convert to list in the correct order
    course_stats = list(course_map.values())

    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'sales':
            form = SalesDataForm(request.POST)
        elif form_type == 'project':
            form = ProjectStatusForm(request.POST)
        elif form_type == 'todo':
            form = TodoItemForm(request.POST)
        elif form_type == 'revenue':
            form = RevenueMetricsForm(request.POST)
        elif form_type == 'visitor':
            form = VisitorMetricsForm(request.POST)
        
        if form.is_valid():
            if form_type == 'todo':
                # Assign the current user to the todo item
                todo = form.save(commit=False)
                todo.user = request.user
                todo.save()
            else:
                form.save()
            messages.success(request, 'Data added successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')

    # Initialize empty forms
    forms = {
        'sales_form': SalesDataForm(),
        'project_form': ProjectStatusForm(),
        'todo_form': TodoItemForm(),
        'revenue_form': RevenueMetricsForm(),
        'visitor_form': VisitorMetricsForm(),
    }

    # Get data for display
    recent_sales = SalesData.objects.order_by('-date')[:5]
    total_sales = SalesData.objects.aggregate(total=Sum('amount'))['total'] or 0

    projects = ProjectStatus.objects.all()
    ongoing_projects = projects.filter(status='ongoing').count()
    completed_projects = projects.filter(status='completed').count()

    todos = TodoItem.objects.filter(user=request.user) if request.user.is_authenticated else []

    last_week = timezone.now().date() - timedelta(days=7)
    revenue_data = RevenueMetrics.objects.filter(date__gte=last_week).order_by('date')
    total_revenue = revenue_data.aggregate(total=Sum('total_revenue'))['total'] or 0
    total_expenses = revenue_data.aggregate(total=Sum('expenses'))['total'] or 0
    net_profit = total_revenue - total_expenses

    visitor_data = VisitorMetrics.objects.order_by('-date')[:7]
    total_visitors = visitor_data.aggregate(total=Sum('unique_visitors'))['total'] or 0

    context = {
        **forms,  # Include all forms
        'recent_sales': recent_sales,
        'total_sales': total_sales,
        'projects': projects,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'todos': todos,
        'revenue_data': revenue_data,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'visitor_data': visitor_data,
        'total_visitors': total_visitors,
        'total_reservations': total_reservations,
        'available_rooms': available_rooms,
        'ongoing_reservations': ongoing_reservations,
        'recent_notifications': recent_notifications,
        'recent_reservations': formatted_reservations,
        'days_of_week': days_of_week,
        'reservation_counts_list': reservation_counts_list,
        'course_stats': course_stats,
        'course_percentages': course_percentages,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'total_reservations': total_reservations,
            'available_rooms': available_rooms,
            'ongoing_reservations': ongoing_reservations,
            'recent_reservations': formatted_reservations,
            'notifications': [
                {
                    'message': notif.message,
                    'created_at': notif.created_at.strftime('%B %d, %Y at %I:%M %p')
                }
                for notif in recent_notifications
            ],
            'course_stats': course_stats,
            'course_percentages': course_percentages,
            'reservation_counts_list': reservation_counts_list,
            'days_of_week': days_of_week
        })
    
    return render(request, 'index.html', context)

# UI Features pages
def buttons(request):
    return render(request, 'pages/ui-features/buttons.html')

def dropdowns(request):
    return render(request, 'pages/ui-features/dropdowns.html')

def typography(request):
    return render(request, 'pages/ui-features/typography.html')

# Icons pages
def font_awesome(request):
    return render(request, 'pages/icons/font-awesome.html')

# Forms pages
def basic_elements(request):
    return render(request, 'pages/forms/basic_elements.html')

# Charts pages
def chartjs(request):
    # Get revenue data for charts
    revenue_data = RevenueMetrics.objects.order_by('-date')[:12]
    visitor_data = VisitorMetrics.objects.order_by('-date')[:30]
    
    context = {
        'revenue_data': revenue_data,
        'visitor_data': visitor_data,
    }
    return render(request, 'pages/charts/chartjs.html', context)

# Tables pages
def basic_table(request):
    # Get all sales data for the table
    sales_data = SalesData.objects.all().order_by('-date')
    context = {
        'sales_data': sales_data,
    }
    return render(request, 'pages/tables/basic-table.html', context)

# Sample pages
def blank_page(request):
    return render(request, 'pages/samples/blank-page.html')

def login_page(request):
    return render(request, 'pages/samples/login.html')

def register_page(request):
    return render(request, 'pages/samples/register.html')

def error_404(request):
    return render(request, 'pages/samples/error-404.html')

def error_500(request):
    return render(request, 'pages/samples/error-500.html')

def get_available_rooms(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        date_str = request.GET.get('date')
        time_str = request.GET.get('time')
        
        if date_str and time_str:
            # Convert strings to datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
            start_time = timezone.make_aware(datetime.combine(date, time))
            end_time = start_time + timedelta(hours=1)
            
            # Get unavailable rooms for this time slot
            unavailable_rooms = Reservation.objects.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['pending', 'ongoing']
            ).values_list('room_id', flat=True)
            
            # Get all rooms with availability status
            all_rooms = Room.objects.all()
            rooms_data = []
            
            for room in all_rooms:
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'capacity': room.capacity,
                    'available': room.id not in unavailable_rooms
                })
            
            return JsonResponse({'rooms': rooms_data})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def make_reservation(request):
    current_datetime = timezone.now()
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.status = 'ongoing' if reservation.start_time <= current_datetime else 'pending'
            reservation.save()
            
            # Create notification with new format
            formatted_start = reservation.start_time.strftime('%B %d, %Y at %I:%M %p')
            Notification.objects.create(
                reservation=reservation,
                message=f"{reservation.name} made a reservation for {reservation.room.name} on {formatted_start}"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            else:
                messages.success(request, 'Your reservation has been submitted successfully!')
                return redirect('make_reservation')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f"{field}: {error}")
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    else:
        form = ReservationForm()
    
    # Update reservation statuses
    current_datetime = timezone.now()
    
    # First update ongoing reservations
    Reservation.objects.filter(
        start_time__lte=current_datetime,
        end_time__gt=current_datetime,
        status='pending'
    ).update(status='ongoing')
    
    # Then update completed reservations
    Reservation.objects.filter(
        end_time__lte=current_datetime,
        status__in=['pending', 'ongoing']
    ).update(status='completed')
    
    # Get recent reservations with proper status
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    # Format recent reservations for JSON response
    formatted_reservations = []
    for res in recent_reservations:
        # Recalculate status for each reservation
        if res.end_time <= current_datetime:
            status = 'completed'
        elif res.start_time <= current_datetime and res.end_time > current_datetime:
            status = 'ongoing'
        else:
            status = 'pending'
            
        # Update status if changed
        if res.status != status:
            res.status = status
            res.save()
            
        formatted_reservations.append({
            'id': res.id,
            'name': res.name,
            'start_time': res.start_time.strftime('%B %d, %Y %H:%M'),
            'end_time': res.end_time.strftime('%H:%M'),
            'num_attendees': res.num_attendees,
            'course': res.get_course_display(),
            'status': status,
            'status_display': dict(Reservation.STATUS_CHOICES)[status]
        })
    
    context = {
        'form': form,
        'title': 'Make a Reservation'
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponse(
            render_to_string('reservation_form.html', context, request=request)
        )
    
    return render(request, 'reservation_form.html', context)

def update_reservation_status(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_datetime = timezone.now()
        
        # First update completed reservations (end time has passed)
        Reservation.objects.filter(
            end_time__lte=current_datetime
        ).update(status='completed')
        
        # Then update ongoing reservations (current time is between start and end)
        Reservation.objects.filter(
            start_time__lte=current_datetime,
            end_time__gt=current_datetime
        ).update(status='ongoing')
        
        # Get total rooms count
        total_rooms = Room.objects.count()
        
        # Get rooms that are currently occupied (ongoing reservations)
        occupied_room_ids = Reservation.objects.filter(
            start_time__lte=current_datetime,
            end_time__gt=current_datetime,
            status='ongoing'
        ).values_list('room_id', flat=True).distinct()
        
        # Calculate available rooms by subtracting occupied rooms from total
        available_rooms = total_rooms - len(occupied_room_ids)
        
        # Get total and ongoing reservations count
        total_reservations = Reservation.objects.count()
        ongoing_reservations = Reservation.objects.filter(status='ongoing').count()
        
        # Get recent reservations with proper status
        recent_reservations = []
        for reservation in Reservation.objects.order_by('-created_at')[:5]:
            # Determine current status based on time
            if reservation.end_time <= current_datetime:
                current_status = 'completed'
            elif reservation.start_time <= current_datetime and reservation.end_time > current_datetime:
                current_status = 'ongoing'
            else:
                current_status = 'pending'
            
            # Update status if it's different
            if reservation.status != current_status:
                reservation.status = current_status
                reservation.save()
            
            recent_reservations.append({
                'id': reservation.id,
                'name': reservation.name,
                'start_time': reservation.start_time.strftime('%B %d, %Y at %I:%M %p'),
                'end_time': reservation.end_time.strftime('%I:%M %p'),
                'num_attendees': reservation.num_attendees,
                'course': reservation.get_course_display(),
                'status': current_status,
                'status_display': dict(Reservation.STATUS_CHOICES)[current_status]
            })
        
        # Get recent notifications
        notifications = []
        for notification in Notification.objects.filter(is_read=False).order_by('-created_at')[:5]:
            notifications.append({
                'message': notification.message,
                'created_at': notification.created_at.strftime('%B %d, %Y at %I:%M %p')
            })
        
        return JsonResponse({
            'total_reservations': total_reservations,
            'available_rooms': available_rooms,
            'ongoing_reservations': ongoing_reservations,
            'recent_reservations': recent_reservations,
            'notifications': notifications
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def rooms(request):
    rooms = Room.objects.all()
    context = {
        'rooms': rooms,
        'title': 'Rooms'
    }
    return render(request, 'rooms.html', context)

def reports(request):
    # Get data for reports
    total_reservations = Reservation.objects.count()
    completed_reservations = Reservation.objects.filter(status='completed').count()
    ongoing_reservations = Reservation.objects.filter(status='ongoing').count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    
    # Get room usage statistics
    room_usage = (
        Reservation.objects
        .values('room__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    # Get course distribution
    course_distribution = (
        Reservation.objects
        .values('course')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    context = {
        'title': 'Reports',
        'total_reservations': total_reservations,
        'completed_reservations': completed_reservations,
        'ongoing_reservations': ongoing_reservations,
        'pending_reservations': pending_reservations,
        'room_usage': room_usage,
        'course_distribution': course_distribution
    }
    return render(request, 'reports.html', context)
