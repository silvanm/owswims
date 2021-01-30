<template>
  <div>
    <div style="max-width: 600px">
      <h1
        v-if="extended"
        class="text-xl md:text-2xl font-semibold text-primary"
      >
        Welcome to European Open-Water Swims
      </h1>
      <p v-if="extended">
        This is a non-for-profit personal project from open-water swimmers for
        open-water swimmers (and event-organizers). We want to help you find the
        your perfect events in Europe.
      </p>
      <p>
        If you plan your vacations around open-water swim events, then this app
        is for you. Select the desired distance and timerange and all matching
        events will be shown to you. Enable the "Show trip duration" switch to
        let the app calculate you the time to get there by car.
      </p>
      <p>
        Click on the
        <font-awesome-icon icon="search" />
        icon to zoom to the event. Many of the races have their race tracks
        displayed.
      </p>

      <p>
        Additions or corrections can be reported to
        <a href="https://muehlemann.com" target="_blank">me</a> at
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >.
      </p>

      <p v-if="extended">
        <a href="https://muehlemann.com" target="_blank">Silvan Mühlemann</a>
      </p>

      <p>Thanks to Andrey Sheyko for his collaboration.</p>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    extended: {
      type: Boolean,
      default: false,
    },
  },
}
</script>
<style lang="scss">
p {
  @apply my-2;
}
</style>
