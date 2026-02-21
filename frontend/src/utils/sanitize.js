import DOMPurify from 'dompurify'

/**
 * Sanitiza HTML antes de renderizar via v-html.
 * Permite tags seguras para markdown convertido (headers, listas, negrito, etc.)
 */
export function sanitizeHtml(html) {
  if (!html) return ''
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['h2', 'h3', 'h4', 'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'span', 'a'],
    ALLOWED_ATTR: ['class', 'href', 'target', 'rel'],
  })
}

/**
 * Sanitiza SVG gerado pelo backend (organograma).
 * SVG requer tags específicas — usa configuração mais permissiva mas ainda segura.
 */
export function sanitizeSvg(svg) {
  if (!svg) return ''
  return DOMPurify.sanitize(svg, { USE_PROFILES: { svg: true, svgFilters: true } })
}
