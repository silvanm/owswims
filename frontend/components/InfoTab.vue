<template>
  <div>
    <ul class="tabs mt-2">
      <li :class="{ active: activeTab === 'help' }" @click="activeTab = 'help'">
        {{ $t('titleHelp') }}
      </li>
      <li
        :class="{ active: activeTab === 'organizers' }"
        @click="activeTab = 'organizers'"
      >
        {{ $t('titleOrganizers') }}
      </li>
      <li
        :class="{ active: activeTab === 'contributors' }"
        @click="activeTab = 'contributors'"
      >
        {{ $t('titleContributors') }}
      </li>
      <li
        :class="{ active: activeTab === 'imprint' }"
        @click="activeTab = 'imprint'"
      >
        {{ $t('titleImprint') }}
      </li>
    </ul>
    <div v-if="activeTab === 'help'" id="help">
      <Infotext></Infotext>
      <div class="inline-block cursor-pointer">
        <a
          v-if="$store.getters['auth/loggedIn']"
          class="mr-2"
          @click="$store.dispatch('auth/logout')"
          >{{ $t('logout') }}</a
        >
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
      <i18n tag="p" path="infoboxThanks"
        ><a href="https://calendarioaguasabiertas.com/" target="_blank"
          >calendarioaguasabiertas.com</a
        ></i18n
      >
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
export default {
  data() {
    return {
      release: process.env.ciCommitSHA,
    }
  },
  computed: {
    activeTab: {
      get() {
        return this.$store.getters.activeInfoTab || 'help'
      },
      set(tab) {
        this.$store.commit('activeInfoTab', tab)
        this.$urlHistory.push({}, '/info/' + tab)
      },
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
