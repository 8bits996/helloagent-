import React, { useState, useCallback, useRef, useEffect } from 'react'
import Toolbar from './Toolbar'
import MarkdownPane from './MarkdownPane'
import HtmlPane from './HtmlPane'
import ExportModal from './ExportModal'
import VersionPanel from './VersionPanel'
import { useHistory } from '../hooks/useHistory'
import { useSync } from '../hooks/useSync'

function Editor({ file, onClose }) {
  // 分屏宽度比例
  const [splitRatio, setSplitRatio] = useState(0.35)
  const containerRef = useRef(null)
  const isDragging = useRef(false)
  
  // Markdown 编辑器 ref
  const mdPaneRef = useRef(null)

  // 当前焦点面板
  const [activePane, setActivePane] = useState('html') // 'md' | 'html'

  // 初始内容
  const initialHtml = file?.htmlContent || ''
  const initialMd = file?.mdContent || ''

  // 使用历史记录 hook
  const {
    currentState,
    pushState,
    undo,
    redo,
    canUndo,
    canRedo,
    reset
  } = useHistory({
    htmlContent: initialHtml,
    mdContent: initialMd
  })

  // 使用同步 hook（添加防护）
  const {
    htmlContent,
    mdContent,
    updateHtml,
    updateMd,
    syncFromHtml,
    syncFromMd,
    setContents
  } = useSync(
    currentState?.htmlContent || initialHtml, 
    currentState?.mdContent || initialMd, 
    activePane
  )

  // 使用 ref 保存最新的内容，确保保存时能获取到最新值
  const htmlContentRef = useRef(htmlContent)
  const mdContentRef = useRef(mdContent)
  
  useEffect(() => {
    htmlContentRef.current = htmlContent
  }, [htmlContent])
  
  useEffect(() => {
    mdContentRef.current = mdContent
  }, [mdContent])

  // 模态框状态
  const [showExportModal, setShowExportModal] = useState(false)
  const [showVersions, setShowVersions] = useState(false)
  
  // 自定义对话框状态（替代 prompt/alert/confirm）
  const [dialog, setDialog] = useState({ type: null, message: '', callback: null })
  const [dialogInput, setDialogInput] = useState('')

  // 处理分屏拖拽
  const handleMouseDown = useCallback((e) => {
    isDragging.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!isDragging.current || !containerRef.current) return
    
    const rect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const ratio = Math.max(0.15, Math.min(0.7, x / rect.width))
    setSplitRatio(ratio)
  }, [])

  const handleMouseUp = useCallback(() => {
    isDragging.current = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  // 防抖定时器
  const saveHistoryTimeout = useRef(null)

  // 处理 HTML 内容更新（记录历史）
  const handleHtmlChange = useCallback((newHtml) => {
    updateHtml(newHtml)
    
    // 防抖保存历史
    if (saveHistoryTimeout.current) {
      clearTimeout(saveHistoryTimeout.current)
    }
    saveHistoryTimeout.current = setTimeout(() => {
      pushState({ htmlContent: newHtml, mdContent })
    }, 300)
  }, [updateHtml, pushState, mdContent])

  // 处理 MD 内容更新（记录历史）
  const handleMdChange = useCallback((newMd) => {
    updateMd(newMd)
    
    // 防抖保存历史（不在这里同步，updateMd 内部已处理）
    if (saveHistoryTimeout.current) {
      clearTimeout(saveHistoryTimeout.current)
    }
    saveHistoryTimeout.current = setTimeout(() => {
      pushState({ htmlContent, mdContent: newMd })
    }, 300)
  }, [updateMd, pushState, htmlContent])

  // 保存版本
  const handleSave = useCallback(() => {
    setDialogInput('')
    setDialog({
      type: 'prompt',
      message: '版本名称（留空使用时间戳）：',
      callback: (versionName) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
        const name = versionName || timestamp
        
        // 使用 ref 获取最新的内容
        const currentHtml = htmlContentRef.current
        const currentMd = mdContentRef.current
        
        console.log('Saving version:', name, 'HTML length:', currentHtml?.length, 'MD length:', currentMd?.length)
        
        // 存储到 localStorage（后续可改为文件系统）
        const fileName = file?.name || 'untitled'
        const versions = JSON.parse(localStorage.getItem(`versions_${fileName}`) || '[]')
        versions.push({
          name,
          timestamp: Date.now(),
          htmlContent: currentHtml,
          mdContent: currentMd
        })
        localStorage.setItem(`versions_${fileName}`, JSON.stringify(versions))
        
        console.log('Version saved successfully')
        
        // 延迟显示成功提示，避免状态冲突
        setTimeout(() => {
          setDialog({ type: 'alert', message: `版本 "${name}" 已保存`, callback: null })
        }, 100)
      }
    })
  }, [file?.name])

  // 重置
  const handleReset = useCallback(() => {
    setDialog({
      type: 'confirm',
      message: '确定要重置到初始版本吗？所有未保存的更改将丢失。',
      callback: (confirmed) => {
        if (confirmed) reset()
      }
    })
  }, [reset])

  // 从版本恢复
  const handleRestoreVersion = useCallback((versionData) => {
    // 使用 setContents 直接设置内容，避免触发同步导致内容被覆盖
    setContents(versionData.htmlContent, versionData.mdContent)
    pushState({
      htmlContent: versionData.htmlContent,
      mdContent: versionData.mdContent
    })
  }, [setContents, pushState])

  // 定位到 MD 中的槽位
  const handleLocateSlot = useCallback((slotName) => {
    if (mdPaneRef.current && slotName) {
      mdPaneRef.current.highlightSlot(slotName)
      setActivePane('md')
    }
  }, [])

  // 清除 MD 高亮
  const handleClearMdHighlight = useCallback(() => {
    if (mdPaneRef.current) {
      mdPaneRef.current.clearHighlight()
    }
  }, [])

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'z' && !e.shiftKey) {
          e.preventDefault()
          undo()
        } else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
          e.preventDefault()
          redo()
        } else if (e.key === 's') {
          e.preventDefault()
          handleSave()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [undo, redo, handleSave])

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0f]">
      {/* 工具栏 */}
      <Toolbar
        onSave={handleSave}
        onExport={() => setShowExportModal(true)}
        onVersions={() => setShowVersions(true)}
        onReset={handleReset}
        onClose={onClose}
        onUndo={undo}
        onRedo={redo}
        canUndo={canUndo}
        canRedo={canRedo}
      />

      {/* 主编辑区 */}
      <div 
        ref={containerRef}
        className="flex-1 flex overflow-hidden"
      >
        {/* Markdown 编辑区 */}
        <div 
          style={{ width: `${splitRatio * 100}%` }}
          className="flex flex-col min-w-0"
          onClick={() => setActivePane('md')}
        >
          <div className={`panel-header flex items-center justify-between transition-colors ${activePane === 'md' ? 'bg-primary/5 border-b-primary/20' : ''}`}>
            <div className="flex items-center gap-2">
              <span className="material-icons text-sm text-gray-600">code</span>
              <span>Markdown</span>
            </div>
            {activePane === 'md' && (
              <span className="flex items-center gap-1.5 text-primary text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                编辑中
              </span>
            )}
          </div>
          <div className="flex-1 overflow-hidden bg-[#0c0c12]">
            <MarkdownPane
              ref={mdPaneRef}
              content={mdContent}
              onChange={handleMdChange}
              isActive={activePane === 'md'}
            />
          </div>
        </div>

        {/* 分隔条 */}
        <div 
          className="resizer"
          onMouseDown={handleMouseDown}
        />

        {/* HTML 预览/编辑区 */}
        <div 
          style={{ width: `${(1 - splitRatio) * 100}%` }}
          className="flex flex-col min-w-0"
          onClick={() => setActivePane('html')}
        >
          <div className={`panel-header flex items-center justify-between transition-colors ${activePane === 'html' ? 'bg-primary/5 border-b-primary/20' : ''}`}>
            <div className="flex items-center gap-2">
              <span className="material-icons text-sm text-gray-600">preview</span>
              <span>HTML Preview</span>
            </div>
            {activePane === 'html' && (
              <span className="flex items-center gap-1.5 text-primary text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                编辑中
              </span>
            )}
          </div>
          <div className="flex-1 overflow-hidden">
            <HtmlPane
              content={htmlContent}
              onChange={handleHtmlChange}
              isActive={activePane === 'html'}
              basePath={file?.basePath}
              onLocateSlot={handleLocateSlot}
              onClearMdHighlight={handleClearMdHighlight}
            />
          </div>
        </div>
      </div>

      {/* 导出模态框 */}
      {showExportModal && (
        <ExportModal
          htmlContent={htmlContent}
          fileName={file?.name || 'export'}
          onClose={() => setShowExportModal(false)}
        />
      )}

      {/* 版本管理面板 */}
      {showVersions && (
        <VersionPanel
          fileName={file?.name || 'untitled'}
          currentHtml={htmlContent}
          currentMd={mdContent}
          onRestore={handleRestoreVersion}
          onClose={() => setShowVersions(false)}
        />
      )}

      {/* 自定义对话框（替代 prompt/alert/confirm） */}
      {dialog.type && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[9999]">
          <div className="bg-[#1a1a24] rounded-xl p-6 w-80 border border-gray-700 shadow-2xl">
            <p className="text-gray-200 mb-4">{dialog.message}</p>
            {dialog.type === 'prompt' && (
              <input
                type="text"
                value={dialogInput}
                onChange={(e) => setDialogInput(e.target.value)}
                className="w-full px-3 py-2 bg-[#0c0c12] border border-gray-600 rounded-lg text-gray-200 mb-4 focus:outline-none focus:border-primary"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    dialog.callback?.(dialogInput)
                    setDialog({ type: null, message: '', callback: null })
                  }
                }}
              />
            )}
            <div className="flex justify-end gap-2">
              {(dialog.type === 'confirm' || dialog.type === 'prompt') && (
                <button
                  onClick={() => {
                    // 取消时不调用 callback，直接关闭
                    setDialog({ type: null, message: '', callback: null })
                  }}
                  className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
                >
                  取消
                </button>
              )}
              <button
                onClick={() => {
                  try {
                    if (dialog.type === 'prompt' && dialog.callback) {
                      dialog.callback(dialogInput)
                    } else if (dialog.type === 'confirm' && dialog.callback) {
                      dialog.callback(true)
                    }
                  } catch (err) {
                    console.error('Dialog callback error:', err)
                  }
                  // 所有类型都要关闭对话框
                  setDialog({ type: null, message: '', callback: null })
                }}
                className="px-4 py-2 bg-primary text-black rounded-lg font-medium hover:bg-primary/90 transition-colors"
              >
                确定
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Editor
