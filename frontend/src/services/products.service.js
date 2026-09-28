import { ref } from 'vue'
import api from '../api.js'

export const useProductService = () => {
  const searchProducts = async (query, filters = {}) => {
    const params = new URLSearchParams({ query, ...filters })
    const response = await api.get(`/products/search?${params}`)
    return response.data
  }

  const getProduct = async (id) => {
    const response = await api.get(`/products/${id}`)
    return response.data
  }

  const compareProducts = async (ids) => {
    const response = await api.get(`/products/compare?product_ids=${ids.join(',')}`)
    return response.data
  }

  return { searchProducts, getProduct, compareProducts }
}

```