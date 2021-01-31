<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div
      id="welcomebox"
      class="p-6 bg-white shadow-xl relative"
      style="z-index: 5"
    >
      <Infotext :extended="true" @hide="$emit('hide')"></Infotext>
      <div class="absolute right-0 top-0 p-6" style="z-index: 10">
        <CloseButton ref="closebutton" @collapse="$emit('hide')"></CloseButton>
      </div>
    </div>
    <div
      class="absolute h-screen w-screen bg-black opacity-25"
      style="z-index: 1; top: 0"
    ></div>
  </div>
</template>
<script>
export default {}
</script>
<style lang="scss" scoped>
div#welcomebox {
  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
