from django import forms
from .models import SalesData, ProjectStatus, TodoItem, RevenueMetrics, VisitorMetrics, Room, Reservation
from django.utils import timezone
from datetime import datetime, timedelta

class SalesDataForm(forms.ModelForm):
    class Meta:
        model = SalesData
        fields = ['date', 'amount', 'product_category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_category': forms.TextInput(attrs={'class': 'form-control'})
        }

class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = ProjectStatus
        fields = ['name', 'status', 'progress', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ['title', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class RevenueMetricsForm(forms.ModelForm):
    class Meta:
        model = RevenueMetrics
        fields = ['date', 'total_revenue', 'expenses']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_revenue': forms.NumberInput(attrs={'class': 'form-control'}),
            'expenses': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        instance = super().save(False)
        instance.net_profit = instance.total_revenue - instance.expenses
        if commit:
            instance.save()
        return instance

class VisitorMetricsForm(forms.ModelForm):
    class Meta:
        model = VisitorMetrics
        fields = ['date', 'page_views', 'unique_visitors', 'bounce_rate']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'page_views': forms.NumberInput(attrs={'class': 'form-control'}),
            'unique_visitors': forms.NumberInput(attrs={'class': 'form-control'}),
            'bounce_rate': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'})
        }

class ReservationForm(forms.ModelForm):
    # Separate date and time fields
    reservation_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'reservation_date'
        }),
        label='Reservation Date'
    )
    
    reservation_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'id': 'reservation_time'
        }),
        label='Start Time'
    )
    
    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_time', 'name', 'course', 'num_attendees', 'room']
        labels = {
            'name': 'Your Name',
            'course': 'Select Course',
            'num_attendees': 'Number of Attendees',
            'room': 'Select Room',
        }
        help_texts = {
            'num_attendees': 'Minimum of 3 and maximum of 10 attendees allowed.',
            'room': 'Select your preferred room.',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            }),
            'num_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '3',
                'max': '10',
                'placeholder': 'Enter number of attendees'
            }),
            'room': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled'  # Initially disabled until date/time selected
            })
        }

    def clean_num_attendees(self):
        num_attendees = self.cleaned_data.get('num_attendees')
        if num_attendees < 3:
            raise forms.ValidationError("Minimum number of attendees is 3")
        if num_attendees > 10:
            raise forms.ValidationError("Maximum number of attendees is 10")
        return num_attendees

    def clean(self):
        cleaned_data = super().clean()
        reservation_date = cleaned_data.get('reservation_date')
        reservation_time = cleaned_data.get('reservation_time')
        room = cleaned_data.get('room')
        num_attendees = cleaned_data.get('num_attendees')
        
        if reservation_date and reservation_time:
            # Combine date and time into start_time
            start_time = datetime.combine(reservation_date, reservation_time)
            start_time = timezone.make_aware(start_time)
            
            # Auto-compute end_time (1 hour after start_time)
            end_time = start_time + timedelta(hours=1)
            
            # Add to cleaned data
            cleaned_data['start_time'] = start_time
            cleaned_data['end_time'] = end_time
            
            # Check if the reservation is in the past
            if start_time < timezone.now():
                raise forms.ValidationError("Cannot make reservations in the past")
            
            if room:
                # Check for overlapping reservations
                overlapping = Reservation.objects.filter(
                    room=room,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                    status__in=['pending', 'ongoing']
                ).exists()
                
                if overlapping:
                    raise forms.ValidationError("This room is already reserved for this time period")
        
        if room and num_attendees:
            if num_attendees > room.capacity:
                raise forms.ValidationError(
                    f"The number of attendees ({num_attendees}) exceeds the room capacity ({room.capacity})"
                )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(False)
        instance.start_time = self.cleaned_data['start_time']
        instance.end_time = self.cleaned_data['end_time']
        if commit:
            instance.save()
        return instance 