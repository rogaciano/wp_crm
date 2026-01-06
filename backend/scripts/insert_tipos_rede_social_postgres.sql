-- =============================================================================
-- Script SQL para inserir tipos de redes sociais na tabela crm_tiporedesocial
-- VERSÃO PARA POSTGRESQL (Produção)
-- Data: 2026-01-06
-- =============================================================================

-- Inserir tipos de redes sociais usando INSERT com ON CONFLICT (upsert)
INSERT INTO crm_tiporedesocial (nome, icone, cor, url_base, placeholder, ordem, ativo) VALUES
('LinkedIn', 'linkedin', '#0A66C2', 'https://linkedin.com/in/', 'usuario', 1, TRUE),
('Instagram', 'instagram', '#E4405F', 'https://instagram.com/', 'usuario (sem @)', 2, TRUE),
('Facebook', 'facebook', '#1877F2', 'https://facebook.com/', 'usuario ou URL completa', 3, TRUE),
('Twitter / X', 'twitter', '#000000', 'https://x.com/', 'usuario (sem @)', 4, TRUE),
('WhatsApp Business', 'whatsapp', '#25D366', 'https://wa.me/', '5581999999999 (com DDD)', 5, TRUE),
('YouTube', 'youtube', '#FF0000', 'https://youtube.com/@', 'canal', 6, TRUE),
('TikTok', 'tiktok', '#000000', 'https://tiktok.com/@', 'usuario', 7, TRUE),
('Website', 'globe', '#6B7280', '', 'https://exemplo.com', 8, TRUE)
ON CONFLICT (nome) DO UPDATE SET
    icone = EXCLUDED.icone,
    cor = EXCLUDED.cor,
    url_base = EXCLUDED.url_base,
    placeholder = EXCLUDED.placeholder,
    ordem = EXCLUDED.ordem,
    ativo = EXCLUDED.ativo;

-- Verificar dados inseridos
SELECT * FROM crm_tiporedesocial ORDER BY ordem;
