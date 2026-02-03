"""
Script para gerar relatório HTML hierárquico do Diagnóstico de Maturidade
Execute: python export_diagnostico.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from crm.models import DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta
from datetime import datetime

def generate_html_report():
    """Gera relatório HTML hierárquico dos pilares, perguntas e respostas"""
    
    pilares = DiagnosticoPilar.objects.all().prefetch_related('perguntas__respostas').order_by('ordem')
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diagnóstico de Maturidade - Estrutura</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 40px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            color: white;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1rem;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        .pilar {{
            background: white;
            border-radius: 16px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            overflow: hidden;
        }}
        .pilar-header {{
            padding: 24px 30px;
            color: white;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .pilar-icon {{
            width: 50px;
            height: 50px;
            background: rgba(255,255,255,0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }}
        .pilar-info h2 {{
            font-size: 1.5rem;
            margin-bottom: 4px;
        }}
        .pilar-info p {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        .perguntas {{
            padding: 20px 30px 30px;
        }}
        .pergunta {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-left: 4px solid #ddd;
        }}
        .pergunta:last-child {{
            margin-bottom: 0;
        }}
        .pergunta-header {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 12px;
        }}
        .pergunta-numero {{
            background: #e9ecef;
            color: #495057;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            font-weight: bold;
            flex-shrink: 0;
        }}
        .pergunta-texto {{
            font-size: 1rem;
            font-weight: 500;
            color: #333;
            line-height: 1.5;
        }}
        .pergunta-ajuda {{
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 8px;
            font-style: italic;
        }}
        .respostas {{
            margin-top: 15px;
            padding-left: 40px;
        }}
        .resposta {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            background: white;
            border-radius: 8px;
            margin-bottom: 8px;
            border: 1px solid #e9ecef;
        }}
        .resposta:last-child {{
            margin-bottom: 0;
        }}
        .pontuacao {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            min-width: 50px;
            text-align: center;
        }}
        .pontuacao-alta {{
            background: #d4edda;
            color: #155724;
        }}
        .pontuacao-media {{
            background: #fff3cd;
            color: #856404;
        }}
        .pontuacao-baixa {{
            background: #f8d7da;
            color: #721c24;
        }}
        .resposta-texto {{
            flex: 1;
            font-size: 0.95rem;
            color: #495057;
        }}
        .resposta-feedback {{
            font-size: 0.8rem;
            color: #6c757d;
            margin-left: auto;
            max-width: 300px;
            text-align: right;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #6c757d;
            font-size: 0.9rem;
        }}
        .no-data {{
            text-align: center;
            padding: 60px;
            color: #6c757d;
        }}
        .no-data-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
        }}
        @media print {{
            body {{
                background: white;
                padding: 20px;
            }}
            .pilar {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Diagnóstico de Maturidade</h1>
            <p>Estrutura Hierárquica de Pilares, Perguntas e Respostas</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{pilares.count()}</div>
                    <div class="stat-label">Pilares</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{DiagnosticoPergunta.objects.count()}</div>
                    <div class="stat-label">Perguntas</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{DiagnosticoResposta.objects.count()}</div>
                    <div class="stat-label">Respostas</div>
                </div>
            </div>
        </div>
"""
    
    if not pilares.exists():
        html += """
        <div class="no-data">
            <div class="no-data-icon">📭</div>
            <h2>Nenhum pilar cadastrado</h2>
            <p>Acesse o Django Admin para criar pilares, perguntas e respostas.</p>
        </div>
"""
    else:
        icons = ['🎯', '💰', '📈', '🛠️', '👥', '🚀', '📊', '💡', '🔧', '📋']
        
        for i, pilar in enumerate(pilares):
            icon = icons[i % len(icons)]
            perguntas = pilar.perguntas.all().order_by('ordem')
            
            html += f"""
        <div class="pilar">
            <div class="pilar-header" style="background: {pilar.cor};">
                <div class="pilar-icon">{icon}</div>
                <div class="pilar-info">
                    <h2>{pilar.nome}</h2>
                    <p>{pilar.descricao or f'{perguntas.count()} perguntas'}</p>
                </div>
            </div>
            <div class="perguntas">
"""
            
            if not perguntas.exists():
                html += """
                <div class="pergunta" style="text-align: center; color: #6c757d;">
                    <em>Nenhuma pergunta cadastrada neste pilar</em>
                </div>
"""
            else:
                for j, pergunta in enumerate(perguntas, 1):
                    respostas = pergunta.respostas.all().order_by('-pontuacao')
                    
                    html += f"""
                <div class="pergunta" style="border-left-color: {pilar.cor};">
                    <div class="pergunta-header">
                        <div class="pergunta-numero">{j}</div>
                        <div class="pergunta-texto">{pergunta.texto}</div>
                    </div>
"""
                    if pergunta.ajuda:
                        html += f"""
                    <div class="pergunta-ajuda">💡 {pergunta.ajuda}</div>
"""
                    
                    if respostas.exists():
                        html += """
                    <div class="respostas">
"""
                        for resposta in respostas:
                            # Determina a classe de pontuação
                            if resposta.pontuacao >= 7:
                                pont_class = "pontuacao-alta"
                            elif resposta.pontuacao >= 4:
                                pont_class = "pontuacao-media"
                            else:
                                pont_class = "pontuacao-baixa"
                            
                            feedback_html = f'<span class="resposta-feedback">{resposta.feedback}</span>' if resposta.feedback else ''
                            
                            html += f"""
                        <div class="resposta">
                            <span class="pontuacao {pont_class}">{resposta.pontuacao} pts</span>
                            <span class="resposta-texto">{resposta.texto}</span>
                            {feedback_html}
                        </div>
"""
                        html += """
                    </div>
"""
                    
                    html += """
                </div>
"""
            
            html += """
            </div>
        </div>
"""
    
    html += f"""
        <div class="footer">
            Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | CRM WP - Diagnóstico de Maturidade
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    print("📊 Gerando relatório do Diagnóstico de Maturidade...")
    
    html_content = generate_html_report()
    
    # Salva o arquivo
    output_path = os.path.join(os.path.dirname(__file__), 'diagnostico_estrutura.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Relatório gerado com sucesso!")
    print(f"📄 Arquivo: {output_path}")
    print(f"\n💡 Abra o arquivo no navegador para visualizar.")
    
    # Tenta abrir no navegador
    import webbrowser
    try:
        webbrowser.open(f'file://{output_path}')
        print("🌐 Abrindo no navegador...")
    except:
        pass


if __name__ == '__main__':
    main()
