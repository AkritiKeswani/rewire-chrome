# Generated by Django 3.2.9 on 2022-05-01 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('RewireApp', '0003_alter_blocklist_website'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('money', models.PositiveIntegerField(default=0)),
                ('accountable_dude', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accountable_dude', to='RewireApp.participant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flow_user', to='RewireApp.participant')),
            ],
            options={
                'unique_together': {('user', 'accountable_dude')},
            },
        ),
    ]
