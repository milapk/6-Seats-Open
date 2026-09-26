from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_playermodel_street_bet'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamemodel',
            name='last_raise_size',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
