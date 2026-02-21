from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration de merge para unir os dois branches paralelos de migrations:
    - Branch A: ...0041_origem_model (depende de 0040_contamarca)
    - Branch B: ...0040_alter_funil_tipo (depende de 0039_add_funil_estagio_to_canal)
    """

    dependencies = [
        ('crm', '0040_alter_funil_tipo'),
        ('crm', '0041_origem_model'),
    ]

    operations = []
