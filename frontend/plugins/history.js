export default ({ app }, inject) => {
  inject('device', {
    isMobile() {
      // using breakpoints from https://tailwindcss.com/docs/breakpoints
      return window.innerWidth < 1024
    },
    isSmall() {
      return window.innerWidth < 640
    },
  })
}
