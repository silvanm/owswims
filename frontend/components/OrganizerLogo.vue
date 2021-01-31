<template>
  <div class="p-6 bg-white shadow-xl relative z-10" style="width: 300px">
    <a :href="url" v-if="url"><img :src="image" /></a>
    <div v-else><img :src="image" /></div>
  </div>
</template>
<script>
export default {
  props: {
    image: {
      type: String,
      required: true,
    },
    url: {
      type: String,
      default: null,
    },
  },
}
</script>
<style scoped>
img {
  width: 100%;
}
</style>
