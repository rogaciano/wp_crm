# Generated migration to populate initial social network types

from django.db import migrations


def criar_tipos_redes_sociais(apps, schema_editor):
    TipoRedeSocial = apps.get_model('crm', 'TipoRedeSocial')
    
    tipos = [
        {
            'nome': 'LinkedIn',
            'icone': 'linkedin',
            'cor': '#0A66C2',
            'url_base': 'https://linkedin.com/in/',
            'placeholder': 'usuario',
            'ordem': 1,
            'ativo': True
        },
        {
            'nome': 'Instagram',
            'icone': 'instagram',
            'cor': '#E4405F',
            'url_base': 'https://instagram.com/',
            'placeholder': 'usuario (sem @)',
            'ordem': 2,
            'ativo': True
        },
        {
            'nome': 'Facebook',
            'icone': 'facebook',
            'cor': '#1877F2',
            'url_base': 'https://facebook.com/',
            'placeholder': 'usuario ou URL completa',
            'ordem': 3,
            'ativo': True
        },
        {
            'nome': 'Twitter / X',
            'icone': 'twitter',
            'cor': '#000000',
            'url_base': 'https://x.com/',
            'placeholder': 'usuario (sem @)',
            'ordem': 4,
            'ativo': True
        },
        {
            'nome': 'WhatsApp Business',
            'icone': 'whatsapp',
            'cor': '#25D366',
            'url_base': 'https://wa.me/',
            'placeholder': '5581999999999 (com DDD)',
            'ordem': 5,
            'ativo': True
        },
        {
            'nome': 'YouTube',
            'icone': 'youtube',
            'cor': '#FF0000',
            'url_base': 'https://youtube.com/@',
            'placeholder': 'canal',
            'ordem': 6,
            'ativo': True
        },
        {
            'nome': 'TikTok',
            'icone': 'tiktok',
            'cor': '#000000',
            'url_base': 'https://tiktok.com/@',
            'placeholder': 'usuario',
            'ordem': 7,
            'ativo': True
        },
        {
            'nome': 'Website',
            'icone': 'globe',
            'cor': '#6B7280',
            'url_base': '',
            'placeholder': 'https://exemplo.com',
            'ordem': 8,
            'ativo': True
        },
    ]
    
    for tipo in tipos:
        TipoRedeSocial.objects.get_or_create(nome=tipo['nome'], defaults=tipo)


def reverter(apps, schema_editor):
    TipoRedeSocial = apps.get_model('crm', 'TipoRedeSocial')
    TipoRedeSocial.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0022_redes_sociais_normalizadas'),
    ]

    operations = [
        migrations.RunPython(criar_tipos_redes_sociais, reverter),
    ]
