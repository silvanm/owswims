// plugins/fontawesome.js
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faGripLines,
  faExternalLinkSquareAlt,
  faImage,
  faSearch,
  faEdit,
  faQuestionCircle,
} from '@fortawesome/free-solid-svg-icons'

// Add the icons to the library
library.add(
  faGripLines,
  faExternalLinkSquareAlt,
  faImage,
  faSearch,
  faEdit,
  faQuestionCircle
)

export default defineNuxtPlugin((nuxtApp) => {
  // Register the component globally
  nuxtApp.vueApp.component('font-awesome-icon', FontAwesomeIcon)
})
