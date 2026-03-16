from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0052_add_agenda_treinamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='canal',
            name='encaminhar_whatsapp_responsavel',
            field=models.BooleanField(
                default=False,
                help_text='Se ativo, encaminha mensagens WhatsApp recebidas nas oportunidades deste canal para o responsável',
            ),
        ),
    ]
