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
    </ul>
    <div id="help" v-if="activeTab === 'help'">
      <Infotext></Infotext>
    </div>
    <div id="contributors" v-if="activeTab === 'contributors'">
      <p>{{ $t('infoboxThanks') }}</p>
    </div>
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
