from django.db import migrations


def forwards(apps, schema_editor):
    """
    Move the Water type field to the location
    :param apps:
    :param schema_editor:
    :return:
    """
    Event = apps.get_model('app', 'Event')
    for event in Event.objects.all():
        event.location.water_type = event.water_type
        event.location.save()


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0024_auto_20210104_2019'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
