import { Loader } from 'google-maps'

export default ({ app }, inject) => {
  // Inject $hello(msg) in Vue, context and store.
  let google = null

  inject('google', async (msg) => {
    const loader = new Loader(process.env.googleMapsKey, { version: 'beta' })
    if (google) {
      return google
    } else {
      console.log(`Loading google!`)
      google = await loader.load()
    }
  })
}
