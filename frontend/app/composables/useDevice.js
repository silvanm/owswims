/**
 * Composable replacing the old this.$device plugin.
 * Provides simple responsive breakpoint checks.
 */
export function useDevice() {
  function isMobile() {
    if (typeof window === 'undefined') return false
    return window.innerWidth < 768
  }

  function isSmall() {
    if (typeof window === 'undefined') return false
    return window.innerWidth < 640
  }

  return {
    isMobile,
    isSmall,
  }
}
