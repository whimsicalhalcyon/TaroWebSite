<script>
export default {
  props: {
    modelValue : {
      type: String,
      default: ()=> '',
    }
  }
}
</script>

<template>
  <input type="text" class="w-full border-[#F3C77B] border-1 p-4 text-[#F3C77B] focus:shadow-[0_0_18px_rgba(243,199,123,0.45)] border-0" placeholder="Напишите свою историю" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)">
</template>

<style scoped>

</style>