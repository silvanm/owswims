import { ref, onMounted } from 'vue'

export function useDeviceDetector() {
  const isMobile = ref(false)
  const isTablet = ref(false)
  const isDesktop = ref(true)

  onMounted(() => {
    const checkDevice = () => {
      const width = window.innerWidth
      isMobile.value = width < 768
      isTablet.value = width >= 768 && width < 1024
      isDesktop.value = width >= 1024
    }

    // Initial check
    checkDevice()

    // Listen for resize events
    window.addEventListener('resize', checkDevice)

    // Clean up event listener
    return () => {
      window.removeEventListener('resize', checkDevice)
    }
  })

  return {
    isMobile,
    isTablet,
    isDesktop,
  }
}
