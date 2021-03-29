<template>
  <div>
    <ul class="tabs mt-2">
      <li :class="{ active: activeTab === 'help' }" @click="activeTab = 'help'">
        {{ $t('titleHelp') }}
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
    <div v-if="activeTab === 'contributors'" id="contributors">
      <p>{{ $t('infoboxThanks') }}</p>
    </div>
    <div v-if="activeTab === 'imprint'" id="imprint">
      <p>
        Silvan Mühlemann<br />
        c/o Mühlemann&Popp Online Media AG<br />
        Limmatquai 122<br />
        8001 Zürich<br />
        +41 78 714 14 78<br />
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >
      </p>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      activeTab: 'help',
    }
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
