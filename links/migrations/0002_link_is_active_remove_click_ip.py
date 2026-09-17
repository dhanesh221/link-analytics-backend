from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [("links", "0001_initial")]
    operations = [
        migrations.AddField(model_name="link", name="is_active", field=models.BooleanField(default=True)),
        migrations.AlterField(model_name="link", name="created_at", field=models.DateTimeField(auto_now_add=True, db_index=True)),
        migrations.AlterField(model_name="click", name="clicked_at", field=models.DateTimeField(auto_now_add=True, db_index=True)),
        migrations.RemoveField(model_name="click", name="ip_address"),
    ]
