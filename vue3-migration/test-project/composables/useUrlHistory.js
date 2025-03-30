import { useRoute, useRouter } from 'vue-router'
import { ref } from 'vue'

export function useUrlHistory() {
  const router = useRouter()
  const route = useRoute()
  const history = ref([])

  // Add current route to history
  if (route.fullPath) {
    history.value.push(route.fullPath)
  }

  const push = (query, path = null) => {
    const currentQuery = { ...route.query }
    const newQuery = { ...currentQuery, ...query }

    // Remove null or undefined values
    Object.keys(newQuery).forEach((key) => {
      if (newQuery[key] === null || newQuery[key] === undefined) {
        delete newQuery[key]
      }
    })

    const newPath = path || route.path

    router.push({
      path: newPath,
      query: newQuery,
    })

    history.value.push(router.currentRoute.value.fullPath)
  }

  const back = () => {
    if (history.value.length > 1) {
      history.value.pop() // Remove current
      const previousPath = history.value[history.value.length - 1]
      router.push(previousPath)
    } else {
      router.push('/')
    }
  }

  const clear = () => {
    history.value = []
  }

  return {
    history,
    push,
    back,
    clear,
  }
}
