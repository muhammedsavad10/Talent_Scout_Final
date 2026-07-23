import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  lastBatchId: string | null;
  setLastBatchId: (id: string | null) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      lastBatchId: null,
      setLastBatchId: (id) => set({ lastBatchId: id }),
    }),
    {
      name: 'talentscout-storage',
    }
  )
);
export default useAppStore;
