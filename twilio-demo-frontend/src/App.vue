<template>
  <div id="app" class="container">
    <img alt="Vue logo" src="./assets/owl_logo.png"/>
    <div>
      <b-button @click="hireTaxi">Hire taxi!</b-button>
    </div>
    <div class="columns is-centered">
      <div class="column box is-6">
      <b-collapse v-if="sessionCreated" class="card" animation="slide" aria-id="contentIdForA11y3">
        <template #trigger="props">
          <div
            class="card-header"
            role="button"
            aria-controls="contentIdForA11y3">
            <p class="card-header-title">
             Tim - M-AB 1234 - Mercedes B-Klasse
            </p>
            <a class="card-header-icon">
              <b-icon
                  :icon="props.open ? 'menu-down' : 'menu-up'">
              </b-icon>
            </a>
          </div>
        </template>

          <div class="card-content">
            <div class="content">
              Contact the driver through one of the following modes
            </div>
          </div>
          <footer class="card-footer">
            <b-button type="is-danger is-light" class="card-footer-item" @click="endSession()">End session</b-button>
            <b-button icon-left="trash" class="card-footer-item"><a href="tel:+14158436071" target="_blank">Call driver </a> </b-button>
            <b-button class="card-footer-item"><a href="https://wa.me/14155238886?text=join worker-something" target="_blank">Whatsapp updates</a></b-button>
            <b-button class="card-footer-item"> SMS </b-button>
          </footer>
        </b-collapse>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'App',
  components: {
  },
  data(){
    return{
      sessionCreated: false,
      sessionSid: "",
    }
  },
  methods:{
    hireTaxi(){
      console.log("Hiring taxi")
      this.$http.post("http://localhost:5000/taxi")
        .then(resp => {
          console.log("Response is: ", resp)   
          this.sessionSid = resp.data.session
        })
        .catch(err => {
          console.log("Error is: ", err)
        })
      this.sessionCreated = true;
    },
    endSession(){
      if(this.sessionSid){
        console.log("Session is :", this.sessionSid)
        this.$http.delete("http://localhost:5000/taxi", {data: {"sessionSid": this.sessionSid}})
          .then(resp =>{
            console.log(resp.data)
          })
          .catch(err => {
            console.log(err)
          })
      }
    },
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
