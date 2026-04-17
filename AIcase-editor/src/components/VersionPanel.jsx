import React, { useState, useEffect } from 'react'

function VersionPanel({ fileName, currentHtml, currentMd, onRestore, onClose }) {
  const [versions, setVersions] = useState([])
  const [editingName, setEditingName] = useState(null)
  const [newName, setNewName] = useState('')
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: '', onConfirm: null })

  // 加载版本列表
  useEffect(() => {
    loadVersions()
  }, [fileName])

  const loadVersions = () => {
    const stored = JSON.parse(localStorage.getItem(`versions_${fileName}`) || '[]')
    // 添加"当前版本"
    const allVersions = [
      {
        id: 'current',
        name: '当前版本（未保存）',
        timestamp: Date.now(),
        htmlContent: currentHtml,
        mdContent: currentMd,
        isCurrent: true
      },
      ...stored.map((v, i) => ({ ...v, id: `v${i}` })).reverse()
    ]
    setVersions(allVersions)
  }

  // 格式化时间
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
    
    return date.toLocaleString('zh-CN', {
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 恢复版本
  const handleRestore = (version) => {
    if (version.isCurrent) {
      setConfirmDialog({
        show: true,
        message: '当前已是此版本',
        onConfirm: () => setConfirmDialog({ show: false, message: '', onConfirm: null }),
        isAlert: true
      })
      return
    }
    
    setConfirmDialog({
      show: true,
      message: `确定要恢复到版本 "${version.name}" 吗？\n当前未保存的更改将丢失。`,
      onConfirm: () => {
        onRestore({
          htmlContent: version.htmlContent,
          mdContent: version.mdContent
        })
        setConfirmDialog({ show: false, message: '', onConfirm: null })
        onClose()
      }
    })
  }

  // 删除版本
  const handleDelete = (version) => {
    if (version.isCurrent) return
    
    setConfirmDialog({
      show: true,
      message: `确定要删除版本 "${version.name}" 吗？`,
      onConfirm: () => {
        const stored = JSON.parse(localStorage.getItem(`versions_${fileName}`) || '[]')
        const index = versions.filter(v => !v.isCurrent).findIndex(v => v.id === version.id)
        const actualIndex = stored.length - 1 - index
        stored.splice(actualIndex, 1)
        localStorage.setItem(`versions_${fileName}`, JSON.stringify(stored))
        loadVersions()
        setConfirmDialog({ show: false, message: '', onConfirm: null })
      }
    })
  }

  // 重命名版本
  const handleRename = (version) => {
    if (version.isCurrent) return
    setEditingName(version.id)
    setNewName(version.name)
  }

  const handleSaveRename = (version) => {
    if (!newName.trim()) {
      setEditingName(null)
      return
    }
    
    const stored = JSON.parse(localStorage.getItem(`versions_${fileName}`) || '[]')
    const index = versions.filter(v => !v.isCurrent).findIndex(v => v.id === version.id)
    const actualIndex = stored.length - 1 - index
    if (actualIndex >= 0 && actualIndex < stored.length) {
      stored[actualIndex].name = newName.trim()
      localStorage.setItem(`versions_${fileName}`, JSON.stringify(stored))
      loadVersions()
    }
    setEditingName(null)
  }

  // 版本列表视图
  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className="bg-editor-bg rounded-lg w-[800px] max-h-[80vh] flex flex-col overflow-hidden">
        {/* 头部 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-editor-border">
          <div className="flex items-center gap-2">
            <span className="material-icons text-primary">history</span>
            <span className="text-white font-medium">版本历史</span>
            <span className="text-gray-500 text-sm">({versions.length} 个版本)</span>
          </div>
          <button onClick={onClose} className="toolbar-btn">
            <span className="material-icons text-sm">close</span>
          </button>
        </div>

        {/* 版本列表 */}
        <div className="flex-1 overflow-y-auto">
          {versions.map((version) => (
            <div
              key={version.id}
              className="px-4 py-3 border-b border-editor-border hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center justify-between">
                {/* 左侧：版本信息 */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    {version.isCurrent ? (
                      <span className="text-primary text-sm font-medium">{version.name}</span>
                    ) : editingName === version.id ? (
                      <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        onBlur={() => handleSaveRename(version)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename(version)
                          if (e.key === 'Escape') setEditingName(null)
                        }}
                        className="bg-transparent border border-primary px-2 py-0.5 rounded text-white text-sm outline-none"
                        autoFocus
                      />
                    ) : (
                      <span className="text-white">{version.name}</span>
                    )}
                    {version.isCurrent && (
                      <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">当前</span>
                    )}
                  </div>
                  <div className="text-gray-500 text-xs mt-1">
                    {formatTime(version.timestamp)}
                  </div>
                </div>

                {/* 右侧：操作按钮 */}
                <div className="flex items-center gap-1">
                  {!version.isCurrent && (
                    <>
                      <button
                        onClick={() => handleRestore(version)}
                        className="toolbar-btn text-xs"
                        title="恢复此版本"
                      >
                        <span className="material-icons text-sm">restore</span>
                      </button>
                      <button
                        onClick={() => handleRename(version)}
                        className="toolbar-btn text-xs"
                        title="重命名"
                      >
                        <span className="material-icons text-sm">edit</span>
                      </button>
                      <button
                        onClick={() => handleDelete(version)}
                        className="toolbar-btn text-xs text-red-400 hover:bg-red-500/20"
                        title="删除"
                      >
                        <span className="material-icons text-sm">delete</span>
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}

          {versions.length === 1 && (
            <div className="px-4 py-8 text-center text-gray-500">
              <span className="material-icons text-4xl mb-2 block opacity-50">folder_open</span>
              <p>暂无保存的版本</p>
              <p className="text-sm mt-1">点击工具栏"保存"按钮创建版本</p>
            </div>
          )}
        </div>

        {/* 底部提示 */}
        <div className="px-4 py-2 border-t border-editor-border text-center text-gray-500 text-sm">
          点击恢复按钮恢复到指定版本 • 双击版本名称可重命名
        </div>
      </div>

      {/* 自定义确认对话框 */}
      {confirmDialog.show && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[9999]">
          <div className="bg-[#1a1a24] rounded-xl p-6 w-80 border border-gray-700 shadow-2xl">
            <p className="text-gray-200 mb-4 whitespace-pre-line">{confirmDialog.message}</p>
            <div className="flex justify-end gap-2">
              {!confirmDialog.isAlert && (
                <button
                  onClick={() => setConfirmDialog({ show: false, message: '', onConfirm: null })}
                  className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
                >
                  取消
                </button>
              )}
              <button
                onClick={() => confirmDialog.onConfirm?.()}
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

export default VersionPanel
