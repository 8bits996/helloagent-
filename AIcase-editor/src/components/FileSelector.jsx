import React, { useState, useCallback, useEffect } from 'react'

// 模板列表
const TEMPLATES = [
  { name: '横版16x9模板.html', label: '横版 16:9 演示模板', icon: 'crop_16_9', desc: 'PPT/演示场景' },
  { name: '长图模板.html', label: '长图模板', icon: 'crop_portrait', desc: '公众号/H5' }
]

function FileSelector({ onSelect, onClose }) {
  const [dragOver, setDragOver] = useState(false)
  const [loadingTemplate, setLoadingTemplate] = useState(null)
  const [cases, setCases] = useState([])
  const [loadingCases, setLoadingCases] = useState(true)
  const [activeTab, setActiveTab] = useState('cases') // 'cases' | 'templates' | 'upload'

  // 加载输出目录的案例列表
  useEffect(() => {
    const loadCases = async () => {
      setLoadingCases(true)
      try {
        // 尝试加载案例索引文件（位于public根目录）
        const response = await fetch('/cases-index.json')
        if (response.ok) {
          const data = await response.json()
          setCases(data.files || [])
        } else {
          // 如果没有索引文件，尝试加载已知的案例
          setCases([])
        }
      } catch (err) {
        console.log('No case index found')
        setCases([])
      } finally {
        setLoadingCases(false)
      }
    }
    loadCases()
  }, [])

  // 加载案例文件
  const loadCase = useCallback(async (caseName) => {
    setLoadingTemplate(caseName)
    try {
      // 先检查是否有保存的版本（优先使用最新版本）
      const versions = JSON.parse(localStorage.getItem(`versions_${caseName}`) || '[]')
      if (versions.length > 0) {
        // 使用最新保存的版本
        const latestVersion = versions[versions.length - 1]
        onSelect({
          name: caseName,
          htmlContent: latestVersion.htmlContent,
          mdContent: latestVersion.mdContent || '',
          basePath: '/public/'
        })
        return
      }
      
      // 无保存版本，加载原始文件
      const response = await fetch(`/${encodeURIComponent(caseName)}`)
      if (!response.ok) throw new Error('加载失败')
      const htmlContent = await response.text()
      
      onSelect({
        name: caseName,
        htmlContent,
        mdContent: '',
        basePath: '/public/'
      })
    } catch (err) {
      alert('加载案例失败: ' + err.message)
    } finally {
      setLoadingTemplate(null)
    }
  }, [onSelect])

  // 加载模板文件
  const loadTemplate = useCallback(async (templateName) => {
    setLoadingTemplate(templateName)
    try {
      // 模板现在位于 public/templates/ 目录下
      const response = await fetch(`/templates/${encodeURIComponent(templateName)}`)
      if (!response.ok) throw new Error('加载失败')
      const htmlContent = await response.text()
      
      onSelect({
        name: templateName,
        htmlContent,
        mdContent: '',
        basePath: '/templates/'
      })
    } catch (err) {
      alert('加载模板失败: ' + err.message)
    } finally {
      setLoadingTemplate(null)
    }
  }, [onSelect])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.name.endsWith('.html')) {
        const reader = new FileReader()
        reader.onload = (event) => {
          onSelect({
            name: file.name,
            htmlContent: event.target.result,
            mdContent: '',
            path: file.name
          })
        }
        reader.readAsText(file)
      } else {
        alert('请选择 HTML 文件')
      }
    }
  }, [onSelect])

  const handleFileInput = useCallback((e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        onSelect({
          name: file.name,
          htmlContent: event.target.result,
          mdContent: '',
          path: file.name
        })
      }
      reader.readAsText(file)
    }
  }, [onSelect])

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="glass-card w-[600px] max-h-[80vh] overflow-hidden animate-slide-up flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
              <span className="material-icons text-sm text-primary">folder_open</span>
            </div>
            <h2 className="text-white font-semibold">选择文件</h2>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-500 hover:text-white hover:bg-white/5 transition-colors"
          >
            <span className="material-icons text-xl">close</span>
          </button>
        </div>

        {/* 标签页 */}
        <div className="flex border-b border-white/5 px-6 shrink-0">
          <button
            onClick={() => setActiveTab('cases')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'cases' 
                ? 'border-primary text-primary' 
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            <span className="flex items-center gap-2">
              <span className="material-icons text-sm">description</span>
              已生成案例
            </span>
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'templates' 
                ? 'border-primary text-primary' 
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            <span className="flex items-center gap-2">
              <span className="material-icons text-sm">dashboard</span>
              空白模板
            </span>
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'upload' 
                ? 'border-primary text-primary' 
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            <span className="flex items-center gap-2">
              <span className="material-icons text-sm">upload_file</span>
              上传文件
            </span>
          </button>
        </div>

        {/* 内容区域 */}
        <div className="p-6 overflow-y-auto flex-1">
          {/* 已生成案例 */}
          {activeTab === 'cases' && (
            <div>
              {loadingCases ? (
                <div className="text-center py-12">
                  <span className="material-icons text-3xl text-primary animate-spin">refresh</span>
                  <p className="text-gray-500 mt-3">加载中...</p>
                </div>
              ) : cases.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/5 flex items-center justify-center">
                    <span className="material-icons text-3xl text-gray-600">folder_off</span>
                  </div>
                  <p className="text-gray-500 mb-2">暂无已生成的案例</p>
                  <p className="text-gray-600 text-sm">请拖拽 HTML 文件或选择空白模板开始</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {cases.map((caseItem) => (
                    <button
                      key={caseItem.name || caseItem}
                      onClick={() => loadCase(caseItem.name || caseItem)}
                      disabled={loadingTemplate === (caseItem.name || caseItem)}
                      className="w-full p-4 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-4 text-left transition-all hover:bg-white/[0.05] hover:border-white/10 group disabled:opacity-50"
                    >
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-white/5 flex items-center justify-center shrink-0">
                        <span className="material-icons text-xl text-green-400/80">article</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-white font-medium mb-0.5 truncate">{caseItem.name || caseItem}</div>
                        <div className="text-gray-600 text-sm">{caseItem.desc || '输出目录'}</div>
                      </div>
                      {loadingTemplate === (caseItem.name || caseItem) ? (
                        <span className="material-icons text-xl text-primary animate-spin">refresh</span>
                      ) : (
                        <span className="material-icons text-xl text-gray-600 group-hover:text-primary group-hover:translate-x-1 transition-all">arrow_forward</span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 空白模板 */}
          {activeTab === 'templates' && (
            <div className="space-y-2">
              {TEMPLATES.map((tpl) => (
                <button
                  key={tpl.name}
                  onClick={() => loadTemplate(tpl.name)}
                  disabled={loadingTemplate === tpl.name}
                  className="w-full p-4 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-4 text-left transition-all hover:bg-white/[0.05] hover:border-white/10 group disabled:opacity-50"
                >
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/10 to-secondary/10 border border-white/5 flex items-center justify-center shrink-0">
                    <span className="material-icons text-xl text-primary/80">{tpl.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-white font-medium mb-0.5">{tpl.label}</div>
                    <div className="text-gray-600 text-sm">{tpl.desc}</div>
                  </div>
                  {loadingTemplate === tpl.name ? (
                    <span className="material-icons text-xl text-primary animate-spin">refresh</span>
                  ) : (
                    <span className="material-icons text-xl text-gray-600 group-hover:text-primary group-hover:translate-x-1 transition-all">arrow_forward</span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* 上传文件 */}
          {activeTab === 'upload' && (
            <div
              className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
                dragOver 
                  ? 'border-primary bg-primary/5' 
                  : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/5 flex items-center justify-center">
                <span className="material-icons text-3xl text-gray-500">upload_file</span>
              </div>
              <p className="text-white mb-2">拖拽 HTML 文件到这里</p>
              <p className="text-gray-600 text-sm mb-5">或点击下方按钮选择文件</p>
              <label className="inline-block">
                <input 
                  type="file" 
                  accept=".html"
                  className="hidden"
                  onChange={handleFileInput}
                />
                <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm font-medium cursor-pointer hover:bg-white/10 hover:border-white/20 transition-all">
                  <span className="material-icons text-sm">folder_open</span>
                  选择文件
                </span>
              </label>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FileSelector
