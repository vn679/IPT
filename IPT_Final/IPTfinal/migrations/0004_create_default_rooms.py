from django.db import migrations

def create_default_rooms(apps, schema_editor):
    Room = apps.get_model('IPTfinal', 'Room')
    default_rooms = [
        {'name': 'Room A', 'capacity': 10},
        {'name': 'Room B', 'capacity': 10},
        {'name': 'Room C', 'capacity': 10},
        {'name': 'Room D', 'capacity': 10},
    ]
    
    for room_data in default_rooms:
        Room.objects.create(**room_data)

def reverse_default_rooms(apps, schema_editor):
    Room = apps.get_model('IPTfinal', 'Room')
    Room.objects.filter(name__in=['Room A', 'Room B', 'Room C', 'Room D']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('IPTfinal', '0003_alter_room_name'),
    ]

    operations = [
        migrations.RunPython(create_default_rooms, reverse_default_rooms),
    ] 