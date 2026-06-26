import { create } from 'zustand'

const useDashboardStore = create((set) => ({
  instances:       [],
  costs:           {},
  totalCost:       0,
  costTrend:       [],
  recommendations: [],
  totalSavings:    0,
  loading:         false,
  error:           null,

  setInstances:       (instances) => set({ instances }),
  setCosts:           (costs, total, trend = []) => set({ costs, totalCost: total, costTrend: trend }),
  setRecommendations: (recs, savings) => set({ recommendations: recs, totalSavings: savings }),
  setLoading:         (loading) => set({ loading }),
  setError:           (error) => set({ error }),
}))

export default useDashboardStore