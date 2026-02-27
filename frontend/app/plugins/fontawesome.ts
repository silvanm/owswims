import { library, config } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faQuestionCircle,
  faGripLines,
  faTimes,
  faPlus,
  faSearch,
  faLocationArrow,
  faInfoCircle,
  faImage,
  faEdit,
  faExternalLinkSquareAlt,
  faExpandArrowsAlt,
  faEnvelope,
  faArrowLeft,
} from '@fortawesome/free-solid-svg-icons'
import { faCalendar } from '@fortawesome/free-regular-svg-icons'
import { faFacebook } from '@fortawesome/free-brands-svg-icons'

// Prevent FontAwesome from adding its CSS since we import it in nuxt.config.ts
config.autoAddCss = false

library.add(
  faQuestionCircle,
  faGripLines,
  faTimes,
  faPlus,
  faSearch,
  faLocationArrow,
  faInfoCircle,
  faImage,
  faEdit,
  faExternalLinkSquareAlt,
  faExpandArrowsAlt,
  faEnvelope,
  faArrowLeft,
  faCalendar,
  faFacebook
)

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('FontAwesomeIcon', FontAwesomeIcon)
})
