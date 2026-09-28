<template>
  <div class="search-bar">
    <input 
      v-model="query" 
      placeholder="Buscar materiales..." 
      @keyup.enter="onSearch"
    />
    <button @click="onSearch">Buscar</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const emit = defineEmits(['search'])
const query = ref('')
const onSearch = () => emit('search', query.value)
</script>

```