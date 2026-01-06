-- =============================================================================
-- Script SQL para adicionar campo emoji à tabela crm_tipocontato
-- VERSÃO PARA POSTGRESQL (Produção)
-- Data: 2026-01-06
-- =============================================================================

-- Adicionar coluna emoji
ALTER TABLE crm_tipocontato ADD COLUMN IF NOT EXISTS emoji VARCHAR(10) NULL;

-- Adicionar coluna foto na tabela de contatos
ALTER TABLE crm_contato ADD COLUMN IF NOT EXISTS foto VARCHAR(100) NULL;

-- Verificar alterações
SELECT id, nome, emoji FROM crm_tipocontato ORDER BY nome;
