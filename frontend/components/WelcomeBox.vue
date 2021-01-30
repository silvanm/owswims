<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div class="p-4 bg-white shadow-xl">
      <div class="float-right">
        <CloseButton ref="closebutton" @collapse="$emit('hide')"></CloseButton>
      </div>
      <Infotext :extended="true"></Infotext>
    </div>
  </div>
</template>
<script>
export default {}
</script>
<style lang="scss" scoped>
div {
  @apply p-4;

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
