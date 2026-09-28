<template>
  <div class="budget-panel">
    <h3>Presupuesto ({{ items.length }} ítems)</h3>
    <ul>
      <li v-for="(item, idx) in items" :key="idx">
        {{ item.nombre }} x{{ item.quantity }} = ${{ item.quantity * item.precio }}
        <button @click="$emit('remove', idx)">x</button>
      </li>
    </ul>
    <p>Subtotal: ${{ subtotal }}</p>
    <p>IVA: ${{ tax }}</p>
    <p><strong>Total: ${{ total }}</strong></p>
    <button @click="$emit('generate')">Generar PDF</button>
  </div>
</template>

<script setup>
defineProps({ items: Array, subtotal: Number, tax: Number, total: Number })
defineEmits(['remove', 'generate'])
</script>

```