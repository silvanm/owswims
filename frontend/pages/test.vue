<template>
  <div>
    <date-picker v-model="dateRange" range></date-picker>
    <button @click="setDate">set date</button>
  </div>
</template>
<script>
import DatePicker from 'vue2-datepicker'
import 'vue2-datepicker/index.css'

export default {
  components: { DatePicker },
  data() {
    return {
      dateRange: [new Date(2019, 0, 1), new Date(2020, 0, 1)],
    }
  },
  methods: {
    setDate() {
      this.dateRange[0] = new Date(2015, 0, 1)
      this.dateRange[1] = new Date(2018, 0, 1)
    },
  },
}
</script>
