<script>
import Radio from "@/components/Radio.vue";
import InputUI from "@/components/InputUI.vue";
import ButtonUi from "@/components/ButtonUi.vue";

export default {
  components: {
    Radio, InputUI, ButtonUi
  },
  data() {
    return {
      selectedOption: null,
      inputStory: '',
      optionValue: '',
      data: [],
      fullAnswer: '',
      data: []
    }
  },

  methods: {
    async getSituation() {
      const params = new URLSearchParams({
        option: this.selectedOption,
        query: this.inputStory,
      })

      const response = await fetch(`/api/tarot?${params.toString()}`,
          {
            method: "GET",
          }
      )

      this.data = await response.json()

      console.log(this.data)
    }
  }
}
</script>

<template>
  <div class="header">
    <div class="logo">
        <div class="sun-logo">
          <img class="sun_lines" src="/img/sun_lines.svg">
          <img class="sun_face" src="/img/face.svg">
        </div>
    </div>

    <p class="text-[#F3C77B] text-4xl text-center mt-8 mb-8">Получи ответы на все вопросы</p>

    <div class="cards">
      <div class="card mt-2">
        <div class="cards flex justify-between">
          <Radio
              v-model="selectedOption"
              value="linear"
              label="Линейный расклад"
              description="Узнать настоящее, прошлое и будущее"
          />
          <Radio
              v-model="selectedOption"
              value="balance"
              label="Расклад Баланс"
              description="Расклад из 4 карт. Что поддерживает вас, что влияет извне, что нарушает равновесие, как восстановить баланс"
          />
          <Radio
              v-model="selectedOption"
              value="advice"
              label="Расклад Баланс"
              description="Расклад из 2 карт. Что, например, сделать и чего стоит избегать"
          />
        </div>
      </div>
    </div>

    <div class="story w-full mt-8">
      <input-u-i v-model="inputStory"></input-u-i>
    </div>
    <div class="btn flex justify-center mt-8">
      <button-ui @click="getSituation">Рассчитать</button-ui>
    </div>

    {{fullAnswer}}

  </div>


</template>

<style scoped>

</style>
