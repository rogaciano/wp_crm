import os
import django
import sys

# Set up Django environment
sys.path.append('e:/projetos/crm_wp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def run():
    with connection.cursor() as cursor:
        # Tables to drop
        cursor.execute("DROP TABLE IF EXISTS crm_funil_usuarios")
        cursor.execute("DROP TABLE IF EXISTS crm_funil")
        
        # Columns to drop if migration failed partially
        to_drop = [
            ('crm_estagiofunil', 'is_padrao'),
            ('crm_estagiofunil', 'funil_id'),
            ('crm_lead', 'estagio_id'),
            ('crm_lead', 'funil_id'),
            ('crm_oportunidade', 'funil_id'),
        ]
        for table, col in to_drop:
            try:
                # Try to drop foreign key if it's a FK
                cursor.execute(f"SELECT constraint_name FROM information_schema.key_column_usage WHERE table_name = '{table}' AND column_name = '{col}' AND table_schema = DATABASE()")
                res = cursor.fetchone()
                if res:
                    fk_name = res[0]
                    cursor.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}")
                    print(f"Dropped FK {fk_name} from {table}")
                
                cursor.execute(f"ALTER TABLE {table} DROP COLUMN {col}")
                print(f"Dropped column {col} from {table}")
            except Exception as e:
                print(f"Error dropping {table}.{col}: {e}")
        
        # Unique constraints/indexes
        try:
            cursor.execute("ALTER TABLE crm_estagiofunil DROP INDEX crm_estagiofunil_funil_id_nome_f6f8742b_uniq")
        except: pass
        try:
            cursor.execute("ALTER TABLE crm_estagiofunil DROP INDEX crm_estagiofunil_nome_key")
        except: pass
        
run()
