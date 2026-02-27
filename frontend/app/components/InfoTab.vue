<template>
  <div>
    <ul class="tabs mt-2">
      <li :class="{ active: activeTab === 'help' }" @click="setTab('help')">
        {{ $t('titleHelp') }}
      </li>
      <li
        :class="{ active: activeTab === 'organizers' }"
        @click="setTab('organizers')"
      >
        {{ $t('titleOrganizers') }}
      </li>
      <li
        :class="{ active: activeTab === 'contributors' }"
        @click="setTab('contributors')"
      >
        {{ $t('titleContributors') }}
      </li>
      <li
        :class="{ active: activeTab === 'imprint' }"
        @click="setTab('imprint')"
      >
        {{ $t('titleImprint') }}
      </li>
    </ul>
    <div v-if="activeTab === 'help'" id="help">
      <Infotext />
      <div class="inline-block cursor-pointer">
        <a
          v-if="authStore.loggedIn"
          class="mr-2"
          @click="authStore.logout()"
        >{{ $t('logout') }}</a>
        <span v-else>
          <a @click="$emit('showLogin')">{{ $t('login') }}</a>
        </span>
      </div>
    </div>
    <div v-if="activeTab === 'organizers'" id="organizers">
      <h3 class="font-bold text-lg mb-2">{{ $t('organizerPortalTitle') }}</h3>
      <p class="mb-3">{{ $t('organizerPortalDescription') }}</p>
      <ul class="list-disc ml-4 mb-4 text-sm">
        <li>{{ $t('organizerFeature1') }}</li>
        <li>{{ $t('organizerFeature2') }}</li>
        <li>{{ $t('organizerFeature3') }}</li>
        <li>{{ $t('organizerFeature4') }}</li>
      </ul>
      <a
        href="/organizer-admin/"
        target="_blank"
        class="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        {{ $t('organizerPortalButton') }}
      </a>
    </div>
    <div v-if="activeTab === 'contributors'" id="contributors">
      <p>
        {{ $t('infoboxThanks') }}
        <a href="https://calendarioaguasabiertas.com/" target="_blank"
          >calendarioaguasabiertas.com</a
        >
      </p>
    </div>
    <div v-if="activeTab === 'imprint'" id="imprint">
      <p>
        Silvan Mühlemann<br />
        c/o mühlemann+popp AG<br />
        Limmatquai 122<br />
        8001 Zürich<br />
        +41 78 714 14 78<br />
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >
      </p>
      <div class="text-gray-300 text-sm">{{ release }}</div>
    </div>
  </div>
</template>

<script>
import { useMainStore } from '~/stores/main'
import { useAuthStore } from '~/stores/auth'

export default {
  emits: ['showLogin'],
  setup() {
    const store = useMainStore()
    const authStore = useAuthStore()
    return { store, authStore }
  },
  data() {
    return {
      release: import.meta.env.VITE_CI_COMMIT_SHA || '',
    }
  },
  computed: {
    activeTab() {
      return this.store.activeInfoTab || 'help'
    },
  },
  methods: {
    setTab(tab) {
      this.store.activeInfoTab = tab
      useUrlHistory().push({}, '/info/' + tab)
    },
  },
}
</script>

<style lang="scss" scoped>
ul.tabs {
  li {
    @apply inline-block mr-2 border-b-2 pb-1 cursor-pointer;
  }

  li.active {
    @apply border-b-2 border-blue-600;
  }
}
</style>
