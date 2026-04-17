import { useState, useCallback, useRef } from 'react'

const MAX_HISTORY = 50

export function useHistory(initialState) {
  const [history, setHistory] = useState([initialState])
  const [currentIndex, setCurrentIndex] = useState(0)
  const initialStateRef = useRef(initialState)

  // 当前状态
  const currentState = history[currentIndex]

  // 添加新状态
  const pushState = useCallback((newState) => {
    setHistory(prev => {
      // 截断当前位置之后的历史
      const newHistory = prev.slice(0, currentIndex + 1)
      newHistory.push(newState)
      
      // 限制历史记录数量
      if (newHistory.length > MAX_HISTORY) {
        newHistory.shift()
        return newHistory
      }
      
      return newHistory
    })
    setCurrentIndex(prev => Math.min(prev + 1, MAX_HISTORY - 1))
  }, [currentIndex])

  // 撤销
  const undo = useCallback(() => {
    setCurrentIndex(prev => Math.max(0, prev - 1))
  }, [])

  // 重做
  const redo = useCallback(() => {
    setCurrentIndex(prev => Math.min(history.length - 1, prev + 1))
  }, [history.length])

  // 是否可撤销/重做
  const canUndo = currentIndex > 0
  const canRedo = currentIndex < history.length - 1

  // 重置到初始状态
  const reset = useCallback(() => {
    setHistory([initialStateRef.current])
    setCurrentIndex(0)
  }, [])

  // 跳转到指定版本
  const goTo = useCallback((index) => {
    if (index >= 0 && index < history.length) {
      setCurrentIndex(index)
    }
  }, [history.length])

  return {
    currentState,
    history,
    currentIndex,
    pushState,
    undo,
    redo,
    canUndo,
    canRedo,
    reset,
    goTo
  }
}
