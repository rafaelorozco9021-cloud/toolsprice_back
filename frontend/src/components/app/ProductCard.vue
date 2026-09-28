<template>
  <div class="product-card">
    <img :src="product.imagen_url" :alt="product.nombre" />
    <h3>{{ product.nombre }}</h3>
    <p class="price">${{ product.precio }} {{ product.moneda }}</p>
    <p class="store">{{ product.tienda }}</p>
    <button @click="$emit('add', product)">Agregar al presupuesto</button>
  </div>
</template>

<script setup>
defineProps({ product: Object })
defineEmits(['add'])
</script>

```