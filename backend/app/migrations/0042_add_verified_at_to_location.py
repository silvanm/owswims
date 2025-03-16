from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0041_event_previous_year_event"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="verified_at",
            field=models.DateTimeField(
                blank=True,
                help_text="set if the location has been verified by the admin",
                null=True,
            ),
        ),
    ]
