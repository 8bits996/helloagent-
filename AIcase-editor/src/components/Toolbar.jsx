import React from 'react'

function Toolbar({ 
  onSave, 
  onExport, 
  onVersions, 
  onReset, 
  onClose,
  onUndo,
  onRedo,
  canUndo,
  canRedo 
}) {
  return (
    <div className="toolbar">
      {/* 左侧：返回 + 撤销/重做 */}
      <div className="flex items-center gap-1">
        <button 
          className="toolbar-btn !p-2 !rounded-xl" 
          onClick={onClose} 
          title="关闭编辑器"
        >
          <span className="material-icons text-lg">arrow_back</span>
        </button>
        
        <div className="w-px h-6 bg-white/5 mx-3"></div>
        
        <div className="flex items-center bg-white/[0.02] rounded-xl p-1">
          <button 
            className="toolbar-btn !border-0 !bg-transparent !px-3" 
            onClick={onUndo} 
            disabled={!canUndo}
            title="撤销 (⌘Z)"
          >
            <span className="material-icons text-lg">undo</span>
          </button>
          
          <div className="w-px h-4 bg-white/10"></div>
          
          <button 
            className="toolbar-btn !border-0 !bg-transparent !px-3" 
            onClick={onRedo} 
            disabled={!canRedo}
            title="重做 (⌘⇧Z)"
          >
            <span className="material-icons text-lg">redo</span>
          </button>
        </div>
      </div>

      {/* 中间：Logo + 标题 */}
      <div className="flex-1 flex items-center justify-center gap-3">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20 border border-white/10 flex items-center justify-center">
          <span className="material-icons text-sm text-primary">edit_document</span>
        </div>
        <span className="text-white/60 text-sm font-medium tracking-wide">案例编辑器</span>
      </div>

      {/* 右侧：主要操作 */}
      <div className="flex items-center gap-2">
        <button 
          className="toolbar-btn" 
          onClick={onVersions} 
          title="版本历史"
        >
          <span className="material-icons text-lg">history</span>
          <span className="hidden sm:inline">版本</span>
        </button>
        
        <button 
          className="toolbar-btn" 
          onClick={onReset} 
          title="重置到初始状态"
        >
          <span className="material-icons text-lg">refresh</span>
          <span className="hidden sm:inline">重置</span>
        </button>
        
        <button 
          className="toolbar-btn" 
          onClick={onExport} 
          title="导出为图片或HTML"
        >
          <span className="material-icons text-lg">download</span>
          <span className="hidden sm:inline">导出</span>
        </button>
        
        <button 
          className="toolbar-btn primary" 
          onClick={onSave} 
          title="保存版本 (⌘S)"
        >
          <span className="material-icons text-lg">save</span>
          <span>保存</span>
        </button>
      </div>
    </div>
  )
}

export default Toolbar
