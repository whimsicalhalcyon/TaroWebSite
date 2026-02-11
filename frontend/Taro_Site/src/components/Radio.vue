<script>
export default {
  props: {
    modelValue: {
      type: String,
      required: true
    },
    value: {
      type: String,
      default: false
    },
    label: {
      type: String,
      required: true
    },
    description : {
      type: String,
    }
  },
  emits: ['update:modelValue']
}
</script>

<template>
  <label
      class="w-xs bg-[#5B1F78] p-6 cursor-pointer border-2 transition-all duration-200 flex items-start"
      :class="modelValue === value? 'border-[#F3C77B] shadow-[0_0_28px_rgba(243,199,123,0.7)]' : 'border-transparent hover:shadow-[0_0_18px_rgba(243,199,123,0.45)]'"
  >
    <input
        type="radio"
        class="hidden"
        :name="name"
        :value="value"
        :checked="modelValue === value"
        @change="$emit('update:modelValue', value)"
    />


    <span class="flex flex-col">
      <span class="text-[#F3C77B] text-3xl">{{label}}</span>
      <span class="text-white text-2xl">{{description}}</span>
    </span>
  </label>
</template>

<style scoped>

</style>