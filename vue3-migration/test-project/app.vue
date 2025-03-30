<template>
  <div>
    <NuxtRouteAnnouncer />
    <div class="navigation">
      <NuxtLink to="/" class="nav-link">Dependency Test</NuxtLink>
      <NuxtLink to="/component-test" class="nav-link">Component Test</NuxtLink>
      <NuxtLink to="/migration-status" class="nav-link">Migration Status</NuxtLink>
      <NuxtLink to="/app" class="nav-link app-link">Integrated App</NuxtLink>
    </div>
    <NuxtPage />
  </div>
</template>

<style scoped>
.navigation {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  background-color: #f5f5f5;
  margin-bottom: 20px;
}

.nav-link {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.nav-link:hover {
  background-color: #45a049;
}

.app-link {
  background-color: #2196F3;
}

.app-link:hover {
  background-color: #0b7dda;
}
</style>
