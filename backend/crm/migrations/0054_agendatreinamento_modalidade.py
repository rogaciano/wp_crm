from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0053_canal_encaminhar_whatsapp_responsavel'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendatreinamento',
            name='modalidade',
            field=models.CharField(
                choices=[('ONLINE', 'Online'), ('PRESENCIAL', 'Presencial')],
                default='ONLINE',
                help_text='Online ou Presencial',
                max_length=15,
            ),
        ),
    ]
