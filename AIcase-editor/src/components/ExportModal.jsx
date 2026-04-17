import React, { useState, useCallback, useRef, useEffect } from 'react'
import * as htmlToImage from 'html-to-image'

// 预设宽度选项
const WIDTH_PRESETS = {
  '16:9': [
    { label: '1920px (1080p)', value: 1920 },
    { label: '1280px (720p)', value: 1280 },
    { label: '960px', value: 960 },
  ],
  'long': [
    { label: '1080px (手机)', value: 1080 },
    { label: '750px (微信)', value: 750 },
    { label: '1200px (公众号)', value: 1200 },
  ]
}

// 清晰度选项
const SCALE_OPTIONS = [
  { label: '1x', value: 1 },
  { label: '2x', value: 2 },
  { label: '3x', value: 3 },
]

function ExportModal({ htmlContent, fileName, onClose }) {
  const [exportType, setExportType] = useState('image') // 'image' | 'html'
  const [templateType, setTemplateType] = useState('16:9')
  const [width, setWidth] = useState(1920)
  const [customWidth, setCustomWidth] = useState('')
  const [scale, setScale] = useState(1)
  const [isExporting, setIsExporting] = useState(false)
  const [previewHeight, setPreviewHeight] = useState(0)
  const [exportProgress, setExportProgress] = useState('')
  const previewIframeRef = useRef(null)

  // 计算高度（16:9模式）
  const getFixedHeight = useCallback(() => {
    return Math.round(width * 9 / 16)
  }, [width])

  // 更新预览
  useEffect(() => {
    if (previewIframeRef.current) {
      const iframe = previewIframeRef.current
      // 使用 srcdoc 而非 blob URL，确保样式正确渲染
      iframe.srcdoc = htmlContent

      // 监听 iframe 加载完成
      const handleLoad = () => {
        if (templateType === 'long') {
          try {
            const doc = iframe.contentDocument || iframe.contentWindow.document
            const height = doc.body.scrollHeight || doc.documentElement.scrollHeight
            setPreviewHeight(height)
          } catch (e) {
            setPreviewHeight(800)
          }
        } else {
          setPreviewHeight(getFixedHeight())
        }
      }
      
      iframe.onload = handleLoad
    }
  }, [htmlContent, templateType, width, getFixedHeight])

  // 导出 HTML 文件
  const handleExportHtml = useCallback(() => {
    setIsExporting(true)
    setExportProgress('准备导出...')
    
    try {
      // 清理编辑器注入的脚本和属性
      let cleanHtml = htmlContent
      cleanHtml = cleanHtml.replace(/<script>\s*\(function\(\)\s*\{[\s\S]*?enableEditMode[\s\S]*?\}\)\(\);\s*<\/script>/g, '')
      cleanHtml = cleanHtml.replace(/<base[^>]*>/g, '')
      cleanHtml = cleanHtml.replace(/\s*contenteditable="true"/g, '')
      cleanHtml = cleanHtml.replace(/\s*data-editable="true"/g, '')
      cleanHtml = cleanHtml.replace(/\s*data-image-slot="true"/g, '')
      cleanHtml = cleanHtml.replace(/\s*data-draggable="true"/g, '')
      cleanHtml = cleanHtml.replace(/\s*draggable="true"/g, '')
      cleanHtml = cleanHtml.replace(/\s*class="element-selected"/g, '')
      
      // 创建 Blob 并下载
      const blob = new Blob([cleanHtml], { type: 'text/html;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const exportFileName = fileName.endsWith('.html') ? fileName : `${fileName}.html`
      link.download = exportFileName
      link.href = url
      link.click()
      
      URL.revokeObjectURL(url)
      setExportProgress('')
      onClose()
      showToast(`导出成功: ${exportFileName}`)
    } catch (error) {
      console.error('Export HTML error:', error)
      setExportProgress('')
      alert('导出失败: ' + error.message)
    } finally {
      setIsExporting(false)
    }
  }, [htmlContent, fileName, onClose])

  // 使用 html-to-image 导出图片（所见即所得）
  const handleExport = useCallback(async () => {
    setIsExporting(true)
    setExportProgress('准备导出...')

    try {
      // 创建离屏渲染容器
      const container = document.createElement('div')
      container.style.cssText = `
        position: fixed;
        left: -99999px;
        top: 0;
        width: ${width}px;
        overflow: visible;
        background: #020617;
        z-index: -9999;
      `
      document.body.appendChild(container)

      // 创建 iframe
      const iframe = document.createElement('iframe')
      iframe.style.cssText = `
        width: ${width}px;
        border: none;
        background: #020617;
      `
      container.appendChild(iframe)

      setExportProgress('渲染内容...')

      // 写入内容
      await new Promise((resolve, reject) => {
        iframe.onload = resolve
        iframe.onerror = reject
        
        const doc = iframe.contentDocument || iframe.contentWindow.document
        doc.open()
        doc.write(htmlContent)
        doc.close()
      })

      // 等待资源加载（字体、图片等）
      setExportProgress('等待资源加载...')
      await new Promise(resolve => setTimeout(resolve, 2500))

      // 获取实际高度
      const doc = iframe.contentDocument || iframe.contentWindow.document
      
      // 对于长图模式，精确获取内容高度
      let finalHeight
      if (templateType === '16:9') {
        finalHeight = getFixedHeight()
      } else {
        // 长图模式：获取实际内容高度
        const body = doc.body
        const html = doc.documentElement
        finalHeight = Math.max(
          body.scrollHeight,
          body.offsetHeight,
          html.clientHeight,
          html.scrollHeight,
          html.offsetHeight
        )
        // 确保高度合理
        finalHeight = Math.max(finalHeight, 800)
      }

      // 调整容器和 iframe 高度
      container.style.height = `${finalHeight}px`
      iframe.style.height = `${finalHeight}px`

      // 等待重排完成
      await new Promise(resolve => setTimeout(resolve, 500))

      setExportProgress('处理嵌套内容...')

      // 隐藏固定定位的按钮（主题切换按钮）
      const fixedButtons = doc.querySelectorAll('button.fixed')
      fixedButtons.forEach(btn => btn.style.display = 'none')

      // 处理 Logo iframe - 将其内容内联替换，避免重影
      const logoIframes = doc.querySelectorAll('iframe[src*="tencentadslogo"]')
      for (const logoIframe of logoIframes) {
        try {
          const logoDoc = logoIframe.contentDocument || logoIframe.contentWindow?.document
          if (logoDoc && logoDoc.body) {
            // 创建替代元素
            const logoReplacement = doc.createElement('div')
            logoReplacement.style.cssText = logoIframe.style.cssText
            logoReplacement.style.width = logoIframe.style.width || '140px'
            logoReplacement.style.height = logoIframe.style.height || '36px'
            logoReplacement.style.display = 'flex'
            logoReplacement.style.alignItems = 'center'
            logoReplacement.style.justifyContent = 'center'
            
            // 复制 logo 内容
            const logoContent = logoDoc.body.innerHTML
            logoReplacement.innerHTML = logoContent
            
            // 复制样式
            const logoStyles = logoDoc.querySelectorAll('style')
            logoStyles.forEach(style => {
              const newStyle = doc.createElement('style')
              newStyle.textContent = style.textContent
              doc.head.appendChild(newStyle)
            })
            
            // 替换 iframe
            logoIframe.parentNode.replaceChild(logoReplacement, logoIframe)
          }
        } catch (e) {
          // 如果无法访问 iframe 内容，直接隐藏避免重影
          logoIframe.style.display = 'none'
          console.warn('Could not inline logo iframe:', e)
        }
      }

      setExportProgress('加载字体...')

      // 预加载 Material Icons 字体并转为 base64 内嵌
      const fontUrl = 'https://fonts.gstatic.com/s/materialicons/v140/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2'
      try {
        const fontResponse = await fetch(fontUrl)
        const fontBlob = await fontResponse.blob()
        const fontBase64 = await new Promise((resolve) => {
          const reader = new FileReader()
          reader.onloadend = () => resolve(reader.result)
          reader.readAsDataURL(fontBlob)
        })
        
        // 注入内嵌字体样式到 iframe
        const fontStyle = doc.createElement('style')
        fontStyle.textContent = `
          @font-face {
            font-family: 'Material Icons';
            font-style: normal;
            font-weight: 400;
            src: url(${fontBase64}) format('woff2');
          }
          .material-icons {
            font-family: 'Material Icons' !important;
            font-weight: normal;
            font-style: normal;
            font-size: 24px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            -webkit-font-smoothing: antialiased;
          }
        `
        doc.head.appendChild(fontStyle)
      } catch (fontError) {
        console.warn('Failed to embed Material Icons font:', fontError)
      }

      // 加载 Inter 字体（用于 tracking-widest 等样式）
      try {
        const interFontUrl = 'https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff2'
        const interResponse = await fetch(interFontUrl)
        const interBlob = await interResponse.blob()
        const interBase64 = await new Promise((resolve) => {
          const reader = new FileReader()
          reader.onloadend = () => resolve(reader.result)
          reader.readAsDataURL(interBlob)
        })
        
        const interStyle = doc.createElement('style')
        interStyle.textContent = `
          @font-face {
            font-family: 'Inter';
            font-style: normal;
            font-weight: 400 800;
            src: url(${interBase64}) format('woff2');
          }
        `
        doc.head.appendChild(interStyle)
      } catch (fontError) {
        console.warn('Failed to embed Inter font:', fontError)
      }

      // 修复 tracking-widest 布局不一致问题：强制计算并内联 letter-spacing
      const trackingElements = doc.querySelectorAll('.tracking-widest')
      trackingElements.forEach(el => {
        // Tailwind tracking-widest = 0.1em，强制固定为像素值
        const computedStyle = iframe.contentWindow.getComputedStyle(el)
        const fontSize = parseFloat(computedStyle.fontSize)
        const letterSpacing = fontSize * 0.1 // tracking-widest = 0.1em
        el.style.letterSpacing = `${letterSpacing}px`
        // 确保文本不换行，保持单行布局
        el.style.whiteSpace = 'nowrap'
      })

      // 等待字体渲染
      await new Promise(resolve => setTimeout(resolve, 1000))

      setExportProgress('生成图片...')

      // 使用 html-to-image 生成图片（支持 blur、backdrop-filter 等 CSS 特效）
      const dataUrl = await htmlToImage.toJpeg(doc.documentElement, {
        width: width,
        height: finalHeight,
        pixelRatio: scale,
        backgroundColor: '#020617',
        style: {
          margin: '0',
          padding: '0',
          overflow: 'visible'
        },
        // 允许字体嵌入
        skipFonts: false,
        // 允许跨域图片
        cacheBust: true,
        // 过滤掉 iframe 元素避免重影
        filter: (node) => {
          // 排除所有 iframe
          if (node.tagName === 'IFRAME') {
            return false
          }
          return true
        },
      })

      setExportProgress('下载文件...')

      // 下载图片
      const link = document.createElement('a')
      const exportFileName = `${fileName.replace('.html', '')}_${width}x${finalHeight}_${scale}x.jpg`
      link.download = exportFileName
      link.href = dataUrl
      link.click()

      // 清理
      document.body.removeChild(container)

      setExportProgress('')
      onClose()
      
      // 显示成功提示
      showToast(`导出成功: ${exportFileName}`)
    } catch (error) {
      console.error('Export error:', error)
      setExportProgress('')
      alert('导出失败: ' + error.message)
    } finally {
      setIsExporting(false)
    }
  }, [htmlContent, fileName, width, scale, templateType, getFixedHeight, onClose])

  // 处理自定义宽度
  const handleCustomWidth = useCallback((value) => {
    setCustomWidth(value)
    const num = parseInt(value, 10)
    if (num > 0 && num <= 4096) {
      setWidth(num)
    }
  }, [])

  // 简单的 toast 提示
  const showToast = (message) => {
    const toast = document.createElement('div')
    toast.className = 'fixed bottom-8 left-1/2 -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-[9999] animate-fade-in'
    toast.textContent = message
    document.body.appendChild(toast)
    setTimeout(() => {
      toast.style.opacity = '0'
      toast.style.transition = 'opacity 0.3s'
      setTimeout(() => document.body.removeChild(toast), 300)
    }, 2000)
  }

  // 计算预览缩放比例
  const previewScale = Math.min(1, 320 / width)
  const previewDisplayHeight = templateType === '16:9' 
    ? getFixedHeight() * previewScale 
    : Math.min(400, previewHeight * previewScale)

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div className="bg-editor-sidebar rounded-xl shadow-2xl w-[680px] max-h-[90vh] overflow-hidden flex flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-editor-border">
          <div className="flex items-center gap-3">
            <span className="material-icons text-primary">{exportType === 'image' ? 'image' : 'code'}</span>
            <h2 className="text-white font-semibold text-lg">导出文件</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-1"
          >
            <span className="material-icons">close</span>
          </button>
        </div>

        {/* 导出类型切换 */}
        <div className="px-5 pt-4">
          <div className="grid grid-cols-2 gap-2">
            <button
              className={`py-3 px-4 rounded-lg border transition-all flex items-center justify-center gap-2 ${
                exportType === 'image'
                  ? 'bg-primary/20 border-primary text-primary'
                  : 'border-editor-border text-gray-400 hover:border-gray-500'
              }`}
              onClick={() => setExportType('image')}
            >
              <span className="material-icons">image</span>
              <span className="font-medium">图片 (JPG)</span>
            </button>
            <button
              className={`py-3 px-4 rounded-lg border transition-all flex items-center justify-center gap-2 ${
                exportType === 'html'
                  ? 'bg-primary/20 border-primary text-primary'
                  : 'border-editor-border text-gray-400 hover:border-gray-500'
              }`}
              onClick={() => setExportType('html')}
            >
              <span className="material-icons">code</span>
              <span className="font-medium">网页 (HTML)</span>
            </button>
          </div>
        </div>

        {/* 内容 */}
        <div className="flex-1 overflow-y-auto">
          {exportType === 'image' ? (
            /* 图片导出设置 */
            <div className="flex">
            {/* 左侧：预览 */}
            <div className="w-[340px] p-5 border-r border-editor-border">
              <label className="block text-sm text-gray-400 mb-3">预览</label>
              <div 
                className="bg-editor-bg rounded-lg overflow-hidden border border-editor-border"
                style={{ 
                  width: '100%',
                  height: previewDisplayHeight + 40,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <div
                  style={{
                    width: width * previewScale,
                    height: templateType === '16:9' ? getFixedHeight() * previewScale : previewHeight * previewScale,
                    overflow: 'hidden',
                    borderRadius: '4px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
                  }}
                >
                  <iframe
                    ref={previewIframeRef}
                    style={{
                      width: width,
                      height: templateType === '16:9' ? getFixedHeight() : previewHeight || 800,
                      border: 'none',
                      transform: `scale(${previewScale})`,
                      transformOrigin: 'top left',
                      pointerEvents: 'none'
                    }}
                    title="Export Preview"
                    sandbox="allow-same-origin allow-scripts"
                  />
                </div>
              </div>
              
              {/* 尺寸信息 */}
              <div className="mt-3 text-center">
                <span className="text-gray-500 text-xs">输出尺寸: </span>
                <span className="text-primary font-mono text-sm">
                  {width} × {templateType === '16:9' ? getFixedHeight() : (previewHeight || '自适应')} px
                </span>
                <span className="text-gray-600 text-xs ml-2">@ {scale}x</span>
              </div>
              <div className="mt-1 text-center">
                <span className="text-gray-600 text-xs">
                  实际像素: {width * scale} × {(templateType === '16:9' ? getFixedHeight() : previewHeight) * scale || '?'} px
                </span>
              </div>
            </div>

            {/* 右侧：设置 */}
            <div className="flex-1 p-5 space-y-5">
              {/* 模板类型 */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">模板类型</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    className={`py-3 px-4 rounded-lg border transition-all flex flex-col items-center gap-1 ${
                      templateType === '16:9'
                        ? 'bg-primary/20 border-primary text-primary'
                        : 'border-editor-border text-gray-400 hover:border-gray-500'
                    }`}
                    onClick={() => {
                      setTemplateType('16:9')
                      setWidth(WIDTH_PRESETS['16:9'][0].value)
                      setCustomWidth('')
                    }}
                  >
                    <span className="material-icons text-2xl">crop_16_9</span>
                    <span className="text-sm font-medium">横版 16:9</span>
                    <span className="text-xs opacity-60">PPT/演示</span>
                  </button>
                  <button
                    className={`py-3 px-4 rounded-lg border transition-all flex flex-col items-center gap-1 ${
                      templateType === 'long'
                        ? 'bg-primary/20 border-primary text-primary'
                        : 'border-editor-border text-gray-400 hover:border-gray-500'
                    }`}
                    onClick={() => {
                      setTemplateType('long')
                      setWidth(WIDTH_PRESETS['long'][0].value)
                      setCustomWidth('')
                    }}
                  >
                    <span className="material-icons text-2xl">crop_portrait</span>
                    <span className="text-sm font-medium">长图</span>
                    <span className="text-xs opacity-60">微信/H5</span>
                  </button>
                </div>
              </div>

              {/* 宽度选择 */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">宽度</label>
                <div className="space-y-2">
                  <div className="grid grid-cols-3 gap-2">
                    {WIDTH_PRESETS[templateType].map(preset => (
                      <button
                        key={preset.value}
                        className={`py-2 px-3 rounded-lg border text-sm transition-colors ${
                          width === preset.value && !customWidth
                            ? 'bg-primary/20 border-primary text-primary'
                            : 'border-editor-border text-gray-400 hover:border-gray-500'
                        }`}
                        onClick={() => {
                          setWidth(preset.value)
                          setCustomWidth('')
                        }}
                      >
                        {preset.value}px
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      placeholder="自定义宽度"
                      value={customWidth}
                      onChange={(e) => handleCustomWidth(e.target.value)}
                      min="320"
                      max="4096"
                      className="flex-1 py-2 px-3 rounded-lg border border-editor-border bg-transparent text-white placeholder-gray-500 focus:border-primary focus:outline-none text-sm"
                    />
                    <span className="text-gray-500 text-sm">px</span>
                  </div>
                </div>
              </div>

              {/* 清晰度 */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">清晰度</label>
                <div className="flex gap-2">
                  {SCALE_OPTIONS.map(option => (
                    <button
                      key={option.value}
                      className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                        scale === option.value
                          ? 'bg-primary/20 border-primary text-primary'
                          : 'border-editor-border text-gray-400 hover:border-gray-500'
                      }`}
                      onClick={() => setScale(option.value)}
                    >
                      <div className="text-sm font-medium">{option.label}</div>
                      <div className="text-xs opacity-60">
                        {option.value === 1 ? '标准' : option.value === 2 ? '高清' : '超清'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 格式说明 */}
              <div className="bg-editor-bg rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <span className="material-icons text-sm text-gray-500 mt-0.5">info</span>
                  <div className="text-xs text-gray-500 space-y-1">
                    <p>• 导出格式：JPG（质量95%）</p>
                    <p>• 2x/3x 适合高分屏或打印</p>
                    <p>• 建议长图使用 1080px 宽度</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          ) : (
            /* HTML 导出设置 */
            <div className="p-5">
              <div className="bg-editor-bg rounded-lg p-6 text-center">
                <span className="material-icons text-5xl text-primary mb-4">code</span>
                <h3 className="text-white font-semibold text-lg mb-2">导出 HTML 文件</h3>
                <p className="text-gray-400 text-sm mb-4">
                  将当前编辑内容导出为独立的 HTML 文件，可直接在浏览器中打开查看
                </p>
                <div className="bg-slate-800/50 rounded-lg p-4 text-left">
                  <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                    <span className="material-icons text-sm text-green-400">check_circle</span>
                    包含所有样式和脚本
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                    <span className="material-icons text-sm text-green-400">check_circle</span>
                    可离线查看
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                    <span className="material-icons text-sm text-green-400">check_circle</span>
                    可二次编辑
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <span className="material-icons text-sm text-green-400">check_circle</span>
                    适合分享和存档
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 底部 */}
        <div className="px-5 py-4 border-t border-editor-border flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {exportProgress && (
              <span className="flex items-center gap-2">
                <span className="material-icons text-sm animate-spin">refresh</span>
                {exportProgress}
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              className="toolbar-btn"
              onClick={onClose}
              disabled={isExporting}
            >
              取消
            </button>
            <button
              className="toolbar-btn primary px-6"
              onClick={exportType === 'image' ? handleExport : handleExportHtml}
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <span className="material-icons text-sm animate-spin">refresh</span>
                  导出中
                </>
              ) : (
                <>
                  <span className="material-icons text-sm">download</span>
                  {exportType === 'image' ? '导出 JPG' : '导出 HTML'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExportModal
