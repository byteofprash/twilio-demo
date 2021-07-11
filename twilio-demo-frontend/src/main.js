import Vue from 'vue'
import App from './App.vue'
import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
import axios from 'axios'

Vue.prototype.$http = axios
Vue.use(Buefy)


Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
