import { ref } from 'vue'
import api from '../api.js'

export const useBudgetService = () => {
  const createBudget = async (budget) => {
    const response = await api.post('/budgets/', budget)
    return response.data
  }

  const getBudgets = async () => {
    const response = await api.get('/budgets/')
    return response.data
  }

  const getBudget = async (id) => {
    const response = await api.get(`/budgets/${id}`)
    return response.data
  }

  const exportPDF = async (id) => {
    const response = await api.post(`/budgets/${id}/export/pdf`, {
      responseType: 'blob'
    })
    return response.data
  }

  return { createBudget, getBudgets, getBudget, exportPDF }
}

```