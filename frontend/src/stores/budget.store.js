import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useBudgetStore = defineStore('budget', () => {
  const items = ref([])
  const budgetType = ref('construccion')

  const subtotal = computed(() => items.value.reduce((sum, item) => sum + (Number(item.precio) || 0) * (Number(item.quantity) || 1), 0))
  const tax = computed(() => Math.round(subtotal.value * 0.16))
  const total = computed(() => subtotal.value + tax.value)
  const count = computed(() => items.value.reduce((s, i) => s + (Number(i.quantity) || 0), 0))
  const itemsCount = computed(() => items.value.length)

  function addItem(product, quantity = 1) {
    const qty = Math.max(1, parseInt(quantity) || 1)
    const existing = items.value.find(i => i.url_producto === product.url_producto)
    if (existing) {
      existing.quantity += qty
    } else {
      items.value.push({ ...product, quantity: qty })
    }
  }

  function removeItem(index) {
    items.value.splice(index, 1)
  }

  function incQty(index) {
    if (items.value[index]) items.value[index].quantity++
  }

  function decQty(index) {
    if (items.value[index]) {
      if (items.value[index].quantity > 1) items.value[index].quantity--
      else removeItem(index)
    }
  }

  function clear() {
    items.value = []
  }

  function setBudgetType(t) {
    budgetType.value = t
  }

  return { items, budgetType, subtotal, tax, total, count, itemsCount, addItem, removeItem, incQty, decQty, clear, setBudgetType }
})