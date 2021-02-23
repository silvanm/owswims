<template>
  <div>
    <Nuxt />
  </div>
</template>
<script>
export default {
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
</script>
<style></style>
