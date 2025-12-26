import os
import json

def gerar_analise_diagnostico(diagnostico_resultado):
    """
    Simula uma análise de IA de alta qualidade baseada nos resultados do diagnóstico.
    Em um cenário real, aqui seria feita uma chamada para a API da OpenAI ou Google Gemini.
    """
    scores = diagnostico_resultado.pontuacao_por_pilar
    respostas = diagnostico_resultado.respostas_detalhadas
    
    # Heurística para gerar insights "inteligentes"
    insights = []
    recomendacoes = []
    
    # 1. Analisar pilar mais fraco
    pilar_fraco = min(scores.items(), key=lambda x: x[1]['score'])
    pilar_forte = max(scores.items(), key=lambda x: x[1]['score'])
    
    if pilar_fraco[1]['score'] < 5:
        insights.append(f"A área de **{pilar_fraco[0]}** apresenta vulnerabilidades críticas que podem estar limitando o crescimento da sua confecção.")
    
    # 2. Gerar recomendações específicas por pilar (Exemplo focado no ERP Dapic)
    if 'Engenharia' in scores and scores['Engenharia']['score'] < 7:
        recomendacoes.append("Implementar o uso de **Fichas Técnicas Digitais** com cálculo automático de consumo de matéria-prima.")
        
    if 'Estoque' in scores and scores['Estoque']['score'] < 6:
        recomendacoes.append("Adotar controle de estoque por **Grade (Cor/Tamanho)** com endereçamento para agilizar a separação de pedidos.")
        
    if 'Comercial' in scores and scores['Comercial']['score'] < 6:
        recomendacoes.append("Integrar os canais de venda (Omnichannel) para evitar quebras de estoque e vendas duplicadas.")

    # 3. Montar o texto final (MarkDown)
    texto = f"### 🤖 Análise Estratégica Baseada em Dados\n\n"
    texto += f"Com base nos dados coletados, identificamos que sua empresa está no nível **{get_nivel_maturidade(scores)}** de maturidade operacional.\n\n"
    
    texto += "#### 📊 Principais Insights\n"
    for insight in insights:
        texto += f"- {insight}\n"
    if not insights:
        texto += "- Sua operação apresenta um equilíbrio saudável entre os pilares analisados.\n"
        
    texto += "\n#### 💡 Recomendações Prioritárias\n"
    for rec in recomendacoes:
        texto += f"- {rec}\n"
        
    texto += "\n#### 🚀 Como o Dapic ERP pode ajudar agora\n"
    texto += f"Para elevar seu score em **{pilar_fraco[0]}**, o Dapic oferece ferramentas específicas de automação que podem reduzir o trabalho manual em até 40% nas primeiras semanas de uso."

    return texto

def get_nivel_maturidade(scores):
    avg = sum(s['score'] for s in scores.values()) / len(scores)
    if avg < 4: return "Iniciante (Reativo)"
    if avg < 7: return "Em Desenvolvimento (Organizado)"
    if avg < 9: return "Avançado (Gerencial)"
    return "Excelência (Orientado a Dados)"
