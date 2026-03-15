<template>
  <MainPageContent />
</template>

<script setup>
// Catch-all route for direct access to /info/<tab>, /submit, /organizer/<slug>, /event/<slug>.
// Middleware (querystringHandler.global.ts) runs before this page and sets store state from to.path.
</script>

<style lang="scss">
body {
  position: fixed;
}

::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 7px;
}

::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.5);
  -webkit-box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}

a {
  @apply text-blue-600;
}

a:hover {
  @apply underline;
}
</style>
