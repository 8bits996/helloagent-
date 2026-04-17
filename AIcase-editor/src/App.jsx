import React, { useState, useCallback } from 'react'
import Editor from './components/Editor'
import FloatButton from './components/FloatButton'
import FileSelector from './components/FileSelector'

function App() {
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [currentFile, setCurrentFile] = useState(null)
  const [showFileSelector, setShowFileSelector] = useState(false)

  const handleOpenEditor = useCallback(() => {
    setShowFileSelector(true)
  }, [])

  const handleFileSelect = useCallback((file) => {
    setCurrentFile(file)
    setShowFileSelector(false)
    setIsEditorOpen(true)
  }, [])

  const handleCloseEditor = useCallback(() => {
    setIsEditorOpen(false)
    setCurrentFile(null)
  }, [])

  return (
    <div className="h-screen w-screen overflow-hidden bg-[#0a0a0f]">
      {isEditorOpen && currentFile ? (
        <Editor 
          file={currentFile} 
          onClose={handleCloseEditor}
        />
      ) : (
        <div className="h-full flex items-center justify-center relative">
          {/* 背景装饰 */}
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[150px]"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-secondary/5 rounded-full blur-[150px]"></div>
          </div>
          
          {/* 网格背景 */}
          <div 
            className="absolute inset-0 opacity-[0.02]"
            style={{
              backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                               linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
              backgroundSize: '60px 60px'
            }}
          ></div>

          {/* 主内容 */}
          <div className="text-center relative z-10 animate-slide-up">
            {/* Logo/图标 */}
            <div className="mb-8 flex justify-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 border border-white/10 flex items-center justify-center glow">
                <span className="material-icons text-4xl gradient-text" style={{ WebkitTextFillColor: 'transparent', background: 'linear-gradient(135deg, #00f2ff, #7000ff)', WebkitBackgroundClip: 'text' }}>
                  edit_document
                </span>
              </div>
            </div>
            
            <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">
              案例编辑器
            </h1>
            <p className="text-gray-500 mb-10 text-lg">
              可视化编辑 · 一键导出
            </p>
            
            {/* 功能标签 */}
            <div className="flex flex-wrap justify-center gap-3 mb-12 max-w-md mx-auto">
              {[
                { icon: 'edit', label: '文字编辑' },
                { icon: 'image', label: '图片替换' },
                { icon: 'sync', label: 'MD同步' },
                { icon: 'download', label: '导出图片' },
                { icon: 'history', label: '版本管理' },
              ].map((item) => (
                <div 
                  key={item.label}
                  className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.06] text-gray-400 text-sm"
                >
                  <span className="material-icons text-sm text-primary/60">{item.icon}</span>
                  {item.label}
                </div>
              ))}
            </div>

            {/* 开始按钮 */}
            <button
              onClick={handleOpenEditor}
              className="group px-8 py-4 rounded-2xl bg-gradient-to-r from-primary/20 to-secondary/20 border border-primary/30 text-white font-medium text-lg transition-all duration-300 hover:from-primary/30 hover:to-secondary/30 hover:border-primary/50 hover:shadow-[0_0_40px_rgba(0,242,255,0.2)] hover:-translate-y-1"
            >
              <span className="flex items-center gap-3">
                <span className="material-icons">add_circle</span>
                开始编辑
                <span className="material-icons text-sm opacity-50 group-hover:translate-x-1 transition-transform">arrow_forward</span>
              </span>
            </button>

            {/* HTML 规范提示 */}
            <div className="mt-12 max-w-lg mx-auto">
              <div className="glass-card rounded-xl p-4 text-left bg-white/[0.02] border border-white/[0.06]">
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-icons text-primary/80 text-sm">info</span>
                  <span className="text-gray-300 text-sm font-medium">HTML 输入规范</span>
                </div>
                <ul className="text-gray-500 text-xs space-y-1.5">
                  <li className="flex items-start gap-2">
                    <span className="text-primary/60">•</span>
                    <span>可编辑元素需添加 <code className="px-1 py-0.5 bg-white/5 rounded text-primary/80">data-slot="名称"</code> 属性</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary/60">•</span>
                    <span>类型标记 <code className="px-1 py-0.5 bg-white/5 rounded text-primary/80">data-type="text|richtext|image"</code></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary/60">•</span>
                    <span>模板标识 <code className="px-1 py-0.5 bg-white/5 rounded text-primary/80">&lt;body data-template="long|16x9"&gt;</code></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-gray-600">→</span>
                    <span className="text-gray-600">详见 docs/指南/Skill.md 阶段五</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* 快捷键提示 */}
            <div className="mt-8 text-gray-600 text-xs">
              <span className="inline-flex items-center gap-2">
                <kbd className="px-2 py-1 rounded bg-white/5 border border-white/10 font-mono">⌘</kbd>
                <span>+</span>
                <kbd className="px-2 py-1 rounded bg-white/5 border border-white/10 font-mono">Z</kbd>
                <span className="mx-2">撤销</span>
                <kbd className="px-2 py-1 rounded bg-white/5 border border-white/10 font-mono">⌘</kbd>
                <span>+</span>
                <kbd className="px-2 py-1 rounded bg-white/5 border border-white/10 font-mono">S</kbd>
                <span className="mx-2">保存</span>
              </span>
            </div>
          </div>
        </div>
      )}

      {showFileSelector && (
        <FileSelector 
          onSelect={handleFileSelect}
          onClose={() => setShowFileSelector(false)}
        />
      )}

      {!isEditorOpen && (
        <FloatButton onClick={handleOpenEditor} />
      )}
    </div>
  )
}

export default App
