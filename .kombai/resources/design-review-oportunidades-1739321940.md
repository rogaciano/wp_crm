# Design Review Results: Oportunidades (Opportunities)

**Review Date**: February 12, 2026  
**Route**: `/oportunidades`  
**Focus Areas**: Visual Design, UX/Usability

> **Note**: This review was conducted through static code analysis only. Visual inspection via browser would provide additional insights into layout rendering, interactive behaviors, and actual appearance.

## Summary

The Opportunities page is a well-structured CRM interface with comprehensive functionality for managing sales opportunities. However, there are several visual design inconsistencies and UX improvements that would enhance the overall user experience. Key areas for improvement include color consistency, action button organization, accessibility enhancements, and mobile interaction patterns.

## Issues

| # | Issue | Criticality | Category | Location |
|---|-------|-------------|----------|----------|
| 1 | Inconsistent color scale usage (`gray-*` vs `zinc-*`) creates visual discord | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:3-4,13-14,16-19,34,40,46,58-63,70-98` |
| 2 | Table action buttons overwhelm users with 6-7 icons without clear hierarchy | 🟠 High | UX/Usability | `frontend/src/views/OportunidadesView.vue:100-119` |
| 3 | Action buttons lack loading states causing uncertainty during async operations | 🟠 High | UX/Usability | `frontend/src/views/OportunidadesView.vue:389-400,427-438,441-450` |
| 4 | KPI cards use inline styles instead of design tokens, breaking consistency | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:34-36` |
| 5 | Non-standard font sizes (`text-[10px]`, `text-[9px]`) instead of Tailwind defaults | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:39,45,134,140,146,150` |
| 6 | Table header sticky positioning only on actions column may cause alignment issues | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:78` |
| 7 | Mobile action buttons cramped with excessive uppercase and small spacing | 🟠 High | UX/Usability | `frontend/src/views/OportunidadesView.vue:155-190` |
| 8 | Search debounce of 500ms feels sluggish for modern UX expectations | ⚪ Low | UX/Usability | `frontend/src/views/OportunidadesView.vue:357-361` |
| 9 | Empty state lacks illustration or visual interest, just plain text | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:195-197` |
| 10 | Delete action uses browser confirm() instead of custom modal with context | 🟠 High | UX/Usability | `frontend/src/views/OportunidadesView.vue:441-450` |
| 11 | Action button colors lack semantic meaning, difficult to predict function | 🟠 High | UX/Usability | `frontend/src/views/OportunidadesView.vue:101-118` |
| 12 | Mobile card has overlapping click areas (whole card + individual buttons) | 🟡 Medium | UX/Usability | `frontend/src/views/OportunidadesView.vue:128-144` |
| 13 | No keyboard focus indicators on icon-only action buttons | 🔴 Critical | UX/Usability | `frontend/src/views/OportunidadesView.vue:101-118` |
| 14 | Alert messages use generic browser alert() breaking visual consistency | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:395,408-409,437,449` |
| 15 | Truncated text relies only on title attribute, no tooltip component | ⚪ Low | UX/Usability | `frontend/src/views/OportunidadesView.vue:83-87` |
| 16 | Filter section card has inconsistent spacing with KPI cards below | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:11-30,33-50` |
| 17 | Icon components defined inline rather than imported from icon library | ⚪ Low | Visual Design | `frontend/src/views/OportunidadesView.vue:238-241` |
| 18 | No visual feedback on copy action success beyond browser alert | 🟡 Medium | UX/Usability | `frontend/src/views/OportunidadesView.vue:389-400` |
| 19 | Table row hover state changes background but no transition defined | ⚪ Low | Visual Design | `frontend/src/views/OportunidadesView.vue:82` |
| 20 | Probability display as plain percentage lacks visual weight indicator | 🟡 Medium | UX/Usability | `frontend/src/views/OportunidadesView.vue:98,151` |
| 21 | Mobile "Indicador" field label is uppercase screaming text | ⚪ Low | Visual Design | `frontend/src/views/OportunidadesView.vue:140` |
| 22 | Currency formatting inconsistent between table and mobile views | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:90,147` |
| 23 | Filter dropdowns lack visual disabled state when not admin | 🟡 Medium | UX/Usability | `frontend/src/views/OportunidadesView.vue:24-28` |
| 24 | Stage badge uses dynamic inline styles instead of predefined variants | 🟡 Medium | Visual Design | `frontend/src/views/OportunidadesView.vue:93-95,134-136` |
| 25 | "Nova Oportunidade" button shadow is different from KPI cards | ⚪ Low | Visual Design | `frontend/src/views/OportunidadesView.vue:5` |

## Criticality Legend
- 🔴 **Critical**: Breaks functionality or violates accessibility standards
- 🟠 **High**: Significantly impacts user experience or design quality
- 🟡 **Medium**: Noticeable issue that should be addressed
- ⚪ **Low**: Nice-to-have improvement

## Detailed Recommendations

### High Priority Fixes

1. **Keyboard Accessibility (#13)**: Add visible focus rings to all icon buttons. Example:
   ```vue
   <button class="p-1.5 text-emerald-500 hover:bg-emerald-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2">
   ```

2. **Action Button Hierarchy (#2)**: Group actions into a dropdown menu for less critical operations. Keep only 2-3 primary actions visible (Edit, WhatsApp, More...).

3. **Loading States (#3)**: Implement loading indicators for async operations:
   ```vue
   <button @click="deleteOportunidade(oportunidade.id)" :disabled="deleting[oportunidade.id]">
     <span v-if="!deleting[oportunidade.id]"><!-- Icon --></span>
     <span v-else class="animate-spin"><!-- Loading icon --></span>
   </button>
   ```

4. **Confirmation Modal (#10)**: Replace browser `confirm()` with custom modal showing opportunity details and delete consequences.

5. **Mobile Interaction (#12)**: Separate click handlers - make card clickable only via explicit "tap to view" area, not entire surface.

### Medium Priority Improvements

6. **Color Consistency (#1)**: Standardize on `zinc-*` scale (already used in main layout). Replace all `gray-*` with `zinc-*`.

7. **Design Tokens (#4, #24)**: Extract KPI card styles and stage badge styles into reusable components with proper color variants.

8. **Font Sizes (#5)**: Replace arbitrary values with standard Tailwind sizes:
   - `text-[10px]` → `text-xs`
   - `text-[9px]` → `text-xs` with `leading-tight`

9. **Empty State (#9)**: Add an illustration and helpful CTA:
   ```vue
   <div class="text-center py-12">
     <svg class="w-16 h-16 mx-auto mb-4 text-gray-300"><!-- Icon --></svg>
     <h3 class="text-lg font-semibold text-gray-900 mb-2">Nenhuma oportunidade ainda</h3>
     <p class="text-gray-500 mb-4">Comece criando sua primeira oportunidade de venda</p>
     <button @click="openCreateModal" class="btn btn-primary">+ Nova Oportunidade</button>
   </div>
   ```

10. **Toast Notifications (#14, #18)**: Implement toast notification system instead of browser alerts for better UX.

### Low Priority Polish

11. **Search Debounce (#8)**: Reduce to 300ms for snappier feel while maintaining API protection.

12. **Transition Effects (#19)**: Add smooth transitions to hover states:
    ```vue
    class="hover:bg-gray-50 transition-colors duration-150"
    ```

13. **Icon Library (#17)**: Import icons from a proper icon library (Heroicons, Lucide) instead of inline SVG templates.

## Next Steps

**Immediate Actions:**
1. Fix critical accessibility issue (#13) - add focus states to all buttons
2. Implement loading states (#3) for async operations
3. Address action button overload (#2) with dropdown/menu pattern

**Short Term (1-2 sprints):**
1. Standardize color system (#1) across the page
2. Replace browser alerts (#10, #14, #18) with custom modals and toasts
3. Improve mobile interaction patterns (#7, #12)

**Long Term:**
1. Build reusable component library for KPI cards, badges, and action menus
2. Implement comprehensive design token system
3. Add keyboard shortcuts and power-user features
