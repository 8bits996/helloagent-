import React, { useRef, useEffect, useImperativeHandle, forwardRef } from 'react'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState, StateEffect, StateField } from '@codemirror/state'
import { Decoration, keymap } from '@codemirror/view'
import { markdown } from '@codemirror/lang-markdown'
import { oneDark } from '@codemirror/theme-one-dark'

// 高亮效果定义
const highlightEffect = StateEffect.define()
const clearHighlightEffect = StateEffect.define()

const highlightField = StateField.define({
  create() {
    return Decoration.none
  },
  update(decorations, tr) {
    for (let effect of tr.effects) {
      if (effect.is(highlightEffect)) {
        const { from, to } = effect.value
        const deco = Decoration.mark({
          class: 'cm-slot-highlight'
        }).range(from, to)
        return Decoration.set([deco])
      }
      if (effect.is(clearHighlightEffect)) {
        return Decoration.none
      }
    }
    return decorations.map(tr.changes)
  },
  provide: f => EditorView.decorations.from(f)
})

// 高亮样式
const highlightTheme = EditorView.baseTheme({
  '.cm-slot-highlight': {
    backgroundColor: 'rgba(0, 242, 255, 0.15)',
    borderLeft: '3px solid #00f2ff',
    paddingLeft: '8px',
    marginLeft: '-11px',
    display: 'block'
  }
})

const MarkdownPane = forwardRef(function MarkdownPane({ content, onChange, isActive }, ref) {
  const containerRef = useRef(null)
  const viewRef = useRef(null)
  const isExternalUpdate = useRef(false)

  // 暴露方法给父组件
  useImperativeHandle(ref, () => ({
    // 定位并高亮指定槽位
    highlightSlot(slotName) {
      if (!viewRef.current || !slotName) return
      
      const doc = viewRef.current.state.doc.toString()
      // 查找槽位区域
      const slotRegex = new RegExp(`(<!--\\s*@slot:${slotName}\\s*-->)([\\s\\S]*?)(<!--\\s*@\\/slot\\s*-->)`)
      const match = doc.match(slotRegex)
      
      if (match) {
        const startIndex = doc.indexOf(match[0])
        const endIndex = startIndex + match[0].length
        
        // 滚动到该位置
        viewRef.current.dispatch({
          effects: [
            highlightEffect.of({ from: startIndex, to: endIndex }),
            EditorView.scrollIntoView(startIndex, { y: 'center' })
          ],
          selection: { anchor: startIndex + match[1].length + 1 }
        })
        
        // 聚焦编辑器
        viewRef.current.focus()
      }
    },
    // 清除高亮
    clearHighlight() {
      if (viewRef.current) {
        viewRef.current.dispatch({
          effects: clearHighlightEffect.of(null)
        })
      }
    },
    // 获取编辑器实例
    getView() {
      return viewRef.current
    }
  }), [])

  useEffect(() => {
    if (!containerRef.current) return

    const updateListener = EditorView.updateListener.of((update) => {
      if (update.docChanged && !isExternalUpdate.current) {
        const newContent = update.state.doc.toString()
        onChange(newContent)
      }
    })

    const state = EditorState.create({
      doc: content,
      extensions: [
        basicSetup,
        markdown(),
        oneDark,
        highlightField,
        highlightTheme,
        updateListener,
        EditorView.lineWrapping,
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px'
          },
          '.cm-scroller': {
            fontFamily: "'Monaco', 'Menlo', 'Consolas', monospace",
            overflow: 'auto'
          },
          '.cm-content': {
            padding: '16px'
          },
          '.cm-gutters': {
            backgroundColor: '#0c0c12',
            borderRight: '1px solid rgba(255,255,255,0.06)'
          },
          '.cm-activeLineGutter': {
            backgroundColor: 'rgba(0, 242, 255, 0.1)'
          }
        })
      ]
    })

    const view = new EditorView({
      state,
      parent: containerRef.current
    })

    viewRef.current = view

    return () => {
      view.destroy()
    }
  }, [])

  // 外部内容更新时同步到编辑器
  useEffect(() => {
    if (viewRef.current) {
      const currentContent = viewRef.current.state.doc.toString()
      if (currentContent !== content) {
        isExternalUpdate.current = true
        viewRef.current.dispatch({
          changes: {
            from: 0,
            to: currentContent.length,
            insert: content
          }
        })
        isExternalUpdate.current = false
      }
    }
  }, [content])

  return (
    <div 
      ref={containerRef} 
      className={`h-full ${isActive ? 'ring-2 ring-primary/30 ring-inset' : ''}`}
    />
  )
})

export default MarkdownPane
