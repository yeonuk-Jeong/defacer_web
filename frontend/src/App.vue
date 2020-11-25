<template>
  <div>
    <v-card>
      <v-app-bar color="deep-purple accent-4" dark fixed>
        <v-toolbar-title>Defacer demo webpage</v-toolbar-title>
      </v-app-bar>
    </v-card>
    <section class="MainPage">
      <MainPage />
    </section>
  </div>
</template>

<script>
import MainPage from './views/MainPage'

export default {
  name: 'app',
  components: {
    MainPage
  }
}
</script>
<style scoped>
#app {
  text-align: left;
  height: 100vh;
}

.MainPage {
  background-color: #212121;
  color: whitesmoke;
  opacity: 0.97;
  height: 1500px;
}
</style>
