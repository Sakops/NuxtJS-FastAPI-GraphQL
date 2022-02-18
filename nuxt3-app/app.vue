<template>
  <div class="bg-blue">
    <h1>My Posts</h1>

    <div class="block" v-for="post in posts" :key="post.id">

      <div class="block-frame">
        <div class="block-info">
          <img src="./assets/post.png" alt="">

          <p>{{ post.id }}</p>
          <p>{{ post.post }}</p>
          <p>{{ post.content }}</p>
        </div>
        
      </div>
      
    </div>
  </div>
</template>

<script>
import axios from "axios"
export default {
  data() {
    return {
        posts:[]
    }
  }, 
  async mounted(){
    const query = `
    query MyQuery {
      getPosts {
        content
        id
        post
      }
    }`;
    const data = await axios.post("http://127.0.0.1:8000/graphql", {
      query: query
    })
    this.posts = data.data.data.getPosts;
  }
}
</script>