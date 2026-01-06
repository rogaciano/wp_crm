-- =============================================================================
-- Script SQL para inserir tipos de redes sociais na tabela crm_tiporedesocial
-- Execute este script no banco de dados de produção
-- Data: 2026-01-06
-- =============================================================================

-- Limpar dados existentes (opcional - descomente se quiser resetar)
-- DELETE FROM crm_contatoredesocial;
-- DELETE FROM crm_tiporedesocial;

-- Inserir tipos de redes sociais
INSERT INTO crm_tiporedesocial (nome, icone, cor, url_base, placeholder, ordem, ativo) VALUES
('LinkedIn', 'linkedin', '#0A66C2', 'https://linkedin.com/in/', 'usuario', 1, 1),
('Instagram', 'instagram', '#E4405F', 'https://instagram.com/', 'usuario (sem @)', 2, 1),
('Facebook', 'facebook', '#1877F2', 'https://facebook.com/', 'usuario ou URL completa', 3, 1),
('Twitter / X', 'twitter', '#000000', 'https://x.com/', 'usuario (sem @)', 4, 1),
('WhatsApp Business', 'whatsapp', '#25D366', 'https://wa.me/', '5581999999999 (com DDD)', 5, 1),
('YouTube', 'youtube', '#FF0000', 'https://youtube.com/@', 'canal', 6, 1),
('TikTok', 'tiktok', '#000000', 'https://tiktok.com/@', 'usuario', 7, 1),
('Website', 'globe', '#6B7280', '', 'https://exemplo.com', 8, 1)
ON DUPLICATE KEY UPDATE
    icone = VALUES(icone),
    cor = VALUES(cor),
    url_base = VALUES(url_base),
    placeholder = VALUES(placeholder),
    ordem = VALUES(ordem),
    ativo = VALUES(ativo);

-- Verificar dados inseridos
SELECT * FROM crm_tiporedesocial ORDER BY ordem;
