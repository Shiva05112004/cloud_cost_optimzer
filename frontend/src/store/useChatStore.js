import { create } from 'zustand'

const useChatStore = create((set, get) => ({
  // messages keyed by instance_id so each recommendation card has its own thread
  threads: {},          // { [instance_id]: [{role, text}, ...] }
  loadingId: null,      // instance_id currently waiting for a response
  openId: null,         // instance_id whose chat box is expanded

  toggleChat: (instanceId) =>
    set((state) => ({
      openId: state.openId === instanceId ? null : instanceId,
    })),

  sendMessage: (instanceId, text) =>
    set((state) => ({
      threads: {
        ...state.threads,
        [instanceId]: [
          ...(state.threads[instanceId] || []),
          { role: 'user', text },
        ],
      },
      loadingId: instanceId,
    })),

  receiveAnswer: (instanceId, text) =>
    set((state) => ({
      threads: {
        ...state.threads,
        [instanceId]: [
          ...(state.threads[instanceId] || []),
          { role: 'assistant', text },
        ],
      },
      loadingId: null,
    })),

  receiveError: (instanceId) =>
    set((state) => ({
      threads: {
        ...state.threads,
        [instanceId]: [
          ...(state.threads[instanceId] || []),
          { role: 'assistant', text: 'Sorry, I could not process that. Please try again.' },
        ],
      },
      loadingId: null,
    })),

  getThread: (instanceId) => get().threads[instanceId] || [],
}))

export default useChatStore
