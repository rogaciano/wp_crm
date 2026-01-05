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
    maxlength="16"
  />
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '(81) 9 9999-9999' },
  inputClass: { type: String, default: 'input' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

// Formata o número para exibição: (81) 9 9999-9999
const formatForDisplay = (value) => {
  if (!value) return ''
  
  // Remove tudo que não é dígito
  let digits = value.replace(/\D/g, '')
  
  // Remove DDI 55 se existir
  if (digits.startsWith('55') && digits.length >= 12) {
    digits = digits.slice(2)
  }
  
  // Limita a 11 dígitos (DDD + 9 + 8)
  digits = digits.slice(0, 11)
  
  // Aplica máscara progressiva
  if (digits.length === 0) return ''
  if (digits.length <= 2) return `(${digits}`
  if (digits.length <= 3) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`
  if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2, 3)} ${digits.slice(3)}`
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 3)} ${digits.slice(3, 7)}-${digits.slice(7, 11)}`
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
  
  // Garante que tem 11 dígitos se tiver DDD
  if (digits.length >= 10 && digits.length < 11) {
    // Adiciona o 9 se faltando
    const ddd = digits.slice(0, 2)
    const resto = digits.slice(2)
    if (!resto.startsWith('9')) {
      digits = ddd + '9' + resto
    }
  }
  
  emit('update:modelValue', digits)
}
</script>
