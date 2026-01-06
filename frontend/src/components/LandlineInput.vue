<template>
  <input
    :value="displayValue"
    @input="handleInput"
    @blur="handleBlur"
    type="text"
    :class="inputClass"
    :placeholder="placeholder"
    :required="required"
    :disabled="disabled"
    maxlength="15"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '(81) 3333-4444' },
  inputClass: { type: String, default: 'input' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

// Formata o número para exibição: (81) 3333-4444 ou (81) 9 3333-4444
const formatForDisplay = (value) => {
  if (!value) return ''

  // Remove tudo que não é dígito
  let digits = value.replace(/\D/g, '')

  // Remove DDI 55 se existir
  if (digits.startsWith('55') && digits.length >= 12) {
    digits = digits.slice(2)
  }

  // Limita a 11 dígitos (pode ter 10 para fixo ou 11 com 9)
  digits = digits.slice(0, 11)

  // Aplica máscara progressiva
  if (digits.length === 0) return ''
  if (digits.length <= 2) return `(${digits}`

  // Detecta se tem 9 no início (após DDD)
  const ddd = digits.slice(0, 2)
  const resto = digits.slice(2)

  if (resto.startsWith('9') && digits.length >= 11) {
    // Formato celular: (81) 9 3333-4444
    const nove = resto.slice(0, 1)
    const parte1 = resto.slice(1, 5)
    const parte2 = resto.slice(5, 9)

    if (resto.length <= 1) return `(${ddd}) ${nove}`
    if (resto.length <= 5) return `(${ddd}) ${nove} ${parte1}`
    return `(${ddd}) ${nove} ${parte1}-${parte2}`
  } else {
    // Formato fixo: (81) 3333-4444
    const parte1 = resto.slice(0, 4)
    const parte2 = resto.slice(4, 8)

    if (resto.length <= 4) return `(${ddd}) ${parte1}`
    return `(${ddd}) ${parte1}-${parte2}`
  }
}

// Remove formatação para salvar
const stripFormatting = (value) => {
  return value.replace(/\D/g, '')
}

const displayValue = computed(() => {
  return formatForDisplay(props.modelValue)
})

const handleInput = (event) => {
  const rawValue = event.target.value
  let digits = stripFormatting(rawValue)

  // Remove DDI 55 se o usuário digitou
  if (digits.startsWith('55') && digits.length > 11) {
    digits = digits.slice(2)
  }

  // Limita a 11 dígitos
  digits = digits.slice(0, 11)

  // Emite o valor sem formatação (backend vai normalizar)
  emit('update:modelValue', digits)

  // Força a exibição formatada
  event.target.value = formatForDisplay(digits)
}

const handleBlur = () => {
  // Quando sai do campo, emite o valor final
  let digits = stripFormatting(props.modelValue)

  // Se tiver menos de 10 dígitos, não é válido
  if (digits.length > 0 && digits.length < 10) {
    // Opcional: pode mostrar erro aqui
  }

  emit('update:modelValue', digits)
}
</script>
