from django.db import migrations

def create_default_table_types(apps, schema_editor):
    TableType = apps.get_model('api', 'TableTypeModel')
    default_tables = [
        (1, 2, 100, 400),
        (5, 10, 500, 2000),
        (10, 20, 1000, 4000),
        (50, 100, 5000, 20000),
        (250, 500, 25000, 100000),
        (500, 1000, 50000, 200000),
    ]
    
    for small_blind, big_blind, min_buy, max_buy in default_tables:
        TableType.objects.get_or_create(
            small_blind=small_blind,
            big_blind=big_blind,
            min_buy_in=min_buy,
            max_buy_in=max_buy
        )

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_table_types),
    ]