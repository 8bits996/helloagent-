import React, { useRef, useEffect, useState, useCallback, useMemo } from 'react'
import PropertyPanel from './PropertyPanel'

function HtmlPane({ content, onChange, isActive, basePath, onLocateSlot, onClearMdHighlight }) {
  const iframeRef = useRef(null)
  const [selectedElement, setSelectedElement] = useState(null)
  
  // 缩放和设备预览状态
  const [zoom, setZoom] = useState(100)
  const [deviceMode, setDeviceMode] = useState('desktop') // 'desktop' | 'mobile'
  
  // 编辑模式开关 - 默认关闭
  const [editMode, setEditMode] = useState(false)
  
  // 追踪内容变化来源，避免 iframe 内部修改后重新加载
  const lastContentRef = useRef(content)
  const isInternalChange = useRef(false)

  // 注入编辑功能的脚本（仅支持文字编辑和图片替换）
  const getEnhancedHtml = useCallback((html, baseUrl, isEditMode) => {
    // 注入 <base> 标签以解析相对路径
    const baseTag = baseUrl ? `<base href="${baseUrl}">` : ''
    
    const editScript = `
<script>
(function() {
  let selectedElement = null;
  let editModeEnabled = ${isEditMode};
  
  // 切换编辑模式
  window.setEditMode = function(enabled) {
    editModeEnabled = enabled;
    if (enabled) {
      document.body.classList.add('edit-mode');
    } else {
      document.body.classList.remove('edit-mode');
      deselectElement();
    }
  };
  
  // 预览模式下点击定位（查找有 data-slot 的元素）
  function handlePreviewClick(e) {
    if (editModeEnabled) return;
    
    // 查找点击元素或其父级中带有 data-slot 的元素
    let target = e.target;
    let slotElement = target.closest('[data-slot]');
    
    if (slotElement) {
      e.preventDefault();
      e.stopPropagation();
      
      const slotName = slotElement.getAttribute('data-slot');
      const slotType = slotElement.getAttribute('data-type') || 'text';
      
      // 添加临时高亮效果
      slotElement.classList.add('preview-highlight');
      setTimeout(() => {
        slotElement.classList.remove('preview-highlight');
      }, 1000);
      
      // 通知父窗口定位到 MD
      window.parent.postMessage({
        type: 'previewLocate',
        slotName: slotName,
        slotType: slotType
      }, '*');
    }
  }
  
  // 初始化元素（只做一次）
  window.initElements = function() {
    // 为预览模式添加全局点击监听
    document.addEventListener('click', handlePreviewClick, true);
    
    // 先处理图片容器，设置标记
    const imageContainers = document.querySelectorAll('[data-type="image"]');
    imageContainers.forEach(container => {
      container.setAttribute('data-image-slot', 'true');
      // 阻止内部元素的默认行为
      container.querySelectorAll('*').forEach(child => {
        child.style.pointerEvents = 'none';
      });
      container.style.pointerEvents = 'auto';
      container.style.cursor = 'pointer';
      
      container.addEventListener('click', function(e) {
        if (!editModeEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        selectElement(this);
      });
      
      container.addEventListener('dblclick', function(e) {
        if (!editModeEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        replaceImage(this);
      });
    });
    
    // 为 img 标签添加点击替换功能
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      // 跳过已在图片容器内的 img
      if (img.closest('[data-type="image"]')) return;
      
      img.setAttribute('data-image-slot', 'true');
      
      img.addEventListener('click', function(e) {
        if (!editModeEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        selectElement(this);
      });
      
      img.addEventListener('dblclick', function(e) {
        if (!editModeEnabled) return;
        e.preventDefault();
        e.stopPropagation();
        replaceImage(this);
      });
    });
    
    // 为所有文本元素添加可编辑属性
    const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, li, td, th, label, a, text');
    textElements.forEach(el => {
      // 跳过图标元素和图片容器及其子元素
      if (el.classList.contains('material-icons') || 
          el.classList.contains('material-symbols-outlined') ||
          el.closest('[data-type="image"]') ||
          el.hasAttribute('data-type') && el.getAttribute('data-type') === 'image' ||
          el.querySelector('img')) {
        return;
      }
      
      // 判断是否为"可安全编辑"的元素
      // 规则：如果子元素都是内联元素（span, a, strong, em, b, i, br, text）或没有子元素，则可编辑
      const blockTags = ['DIV', 'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI', 'UL', 'OL', 'TABLE', 'TR', 'TD', 'TH', 'SECTION', 'ARTICLE', 'HEADER', 'FOOTER', 'NAV', 'ASIDE'];
      const hasBlockChildren = Array.from(el.children).some(child => {
        return blockTags.includes(child.tagName);
      });
      
      // 如果有块级子元素，跳过（编辑会破坏结构）
      if (hasBlockChildren) {
        return;
      }
      
      // 有文本内容的元素才可编辑
      if (el.innerText && el.innerText.trim()) {
        el.setAttribute('data-editable', 'true');
        
        // 双击进入编辑模式
        el.addEventListener('dblclick', function(e) {
          if (!editModeEnabled) return;
          e.stopPropagation();
          this.setAttribute('contenteditable', 'true');
          this.focus();
        });
        
        el.addEventListener('blur', function() {
          this.removeAttribute('contenteditable');
          notifyChange();
        });
        
        // 单击选中元素
        el.addEventListener('click', function(e) {
          if (!editModeEnabled) return;
          e.stopPropagation();
          selectElement(this);
        });
      }
    });
    
    // 点击空白区域取消选中
    document.addEventListener('click', function(e) {
      if (!editModeEnabled) return;
      if (!e.target.closest('[data-editable], [data-image-slot]')) {
        deselectElement();
      }
    });
    
    // 初始状态
    if (editModeEnabled) {
      document.body.classList.add('edit-mode');
    }
  };
  
  // 选中元素
  function selectElement(el) {
    deselectElement();
    selectedElement = el;
    el.classList.add('element-selected');
    
    // 检查是否为纯文本元素（没有子元素标签，只有文本节点）
    const hasSafeText = el.children.length === 0 || 
      (el.children.length === 1 && el.children[0].tagName === 'BR');
    
    // 获取元素文本内容（仅对纯文本元素）
    let textContent = '';
    if (hasSafeText && el.tagName !== 'IMG' && !el.hasAttribute('data-type')) {
      textContent = el.innerText || '';
    }
    
    // 查找最近的 data-slot 属性（元素自身或父级）
    let slotName = el.getAttribute('data-slot');
    if (!slotName) {
      const slotParent = el.closest('[data-slot]');
      slotName = slotParent ? slotParent.getAttribute('data-slot') : null;
    }
    
    // 获取槽位类型
    let slotType = el.getAttribute('data-type');
    if (!slotType) {
      const typeParent = el.closest('[data-type]');
      slotType = typeParent ? typeParent.getAttribute('data-type') : 'text';
    }
    
    // 通知父窗口
    const rect = el.getBoundingClientRect();
    window.parent.postMessage({
      type: 'elementSelected',
      tagName: el.tagName,
      textContent: textContent,
      canEditText: hasSafeText, // 标志是否可以安全地通过属性面板编辑文本
      slotName: slotName,
      slotType: slotType,
      styles: {
        color: getComputedStyle(el).color,
        backgroundColor: getComputedStyle(el).backgroundColor,
        fontSize: getComputedStyle(el).fontSize,
        fontWeight: getComputedStyle(el).fontWeight,
        textAlign: getComputedStyle(el).textAlign,
        lineHeight: getComputedStyle(el).lineHeight
      },
      position: {
        x: rect.left + window.scrollX,
        y: rect.top + window.scrollY - 50
      },
      isImage: el.tagName === 'IMG' || el.hasAttribute('data-type') && el.getAttribute('data-type') === 'image',
      className: el.className || ''
    }, '*');
  }
  
  // 取消选中
  function deselectElement() {
    if (selectedElement) {
      selectedElement.classList.remove('element-selected');
      selectedElement = null;
      window.parent.postMessage({ type: 'elementDeselected' }, '*');
    }
  }
  
  // 替换图片
  function replaceImage(el) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          if (el.tagName === 'IMG') {
            // 直接替换 img 的 src
            el.src = e.target.result;
          } else {
            // 容器元素：用图片替换内部内容
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.objectFit = 'contain';
            el.innerHTML = '';
            el.appendChild(img);
          }
          notifyChange();
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  }
  
  // 接收父窗口的命令
  window.addEventListener('message', function(e) {
    const { type, property, value } = e.data;
    
    if (type === 'toggleEditMode') {
      window.setEditMode(value);
      return;
    }
    
    if (!selectedElement) return;
    
    if (type === 'setStyle') {
      selectedElement.style[property] = value;
      notifyChange();
    } else if (type === 'setText') {
      if (selectedElement.tagName !== 'IMG') {
        selectedElement.innerText = value;
        notifyChange();
      }
    } else if (type === 'replaceImage') {
      replaceImage(selectedElement);
    }
  });
  
  // 通知父窗口内容已更改
  function notifyChange() {
    // 延迟发送，避免频繁更新
    clearTimeout(window._notifyTimeout);
    window._notifyTimeout = setTimeout(function() {
      window.parent.postMessage({
        type: 'contentChanged',
        html: document.documentElement.outerHTML
      }, '*');
    }, 100);
  }
  
  // 样式
  const style = document.createElement('style');
  style.textContent = \`
    .edit-mode [data-editable="true"]:hover {
      outline: 2px dashed #00f2ff !important;
      outline-offset: 2px !important;
      cursor: text !important;
    }
    .edit-mode [data-image-slot]:hover {
      outline: 2px dashed #facc15 !important;
      outline-offset: 2px !important;
      cursor: pointer !important;
    }
    .element-selected {
      outline: 3px solid #00f2ff !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 20px rgba(0, 242, 255, 0.3) !important;
    }
    [contenteditable="true"] {
      outline: 2px solid #00f2ff !important;
      outline-offset: 2px !important;
    }
    /* 预览模式下可点击元素的样式 */
    [data-slot] {
      cursor: pointer;
    }
    [data-slot]:hover {
      outline: 2px dashed rgba(168, 85, 247, 0.5) !important;
      outline-offset: 2px !important;
    }
    .preview-highlight {
      outline: 3px solid #a855f7 !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 20px rgba(168, 85, 247, 0.4) !important;
      animation: preview-pulse 0.5s ease-out;
    }
    @keyframes preview-pulse {
      0% { box-shadow: 0 0 0 rgba(168, 85, 247, 0.8); }
      100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.4); }
    }
    /* 编辑模式下覆盖预览样式 */
    .edit-mode [data-slot]:hover {
      outline: none !important;
    }
  \`;
  document.head.appendChild(style);
  
  // 初始化
  if (document.readyState === 'complete') {
    window.initElements();
  } else {
    window.addEventListener('load', window.initElements);
  }
})();
</script>
`
    // 在 </body> 前注入脚本
    if (html.includes('</body>')) {
      html = html.replace('</body>', editScript + '</body>')
    } else {
      html = html + editScript
    }
    
    // 在 <head> 后注入 base 标签
    if (baseTag && html.includes('<head>')) {
      html = html.replace('<head>', '<head>' + baseTag)
    } else if (baseTag && html.includes('<head ')) {
      html = html.replace(/<head[^>]*>/, (match) => match + baseTag)
    }
    
    return html
  }, [])

  // 更新 iframe 内容（只在外部变化时更新）
  useEffect(() => {
    // 如果是内部变化引起的 content 更新，不重新加载 iframe
    if (isInternalChange.current) {
      isInternalChange.current = false
      lastContentRef.current = content
      return
    }
    
    if (iframeRef.current) {
      // 模板资源路径改为 /templates/（public目录下）
      const baseUrl = basePath || '/templates/'
      const enhancedHtml = getEnhancedHtml(content, baseUrl, editMode)
      // 使用 srcdoc 而非 blob URL，避免 sandbox 脚本限制
      iframeRef.current.srcdoc = enhancedHtml
      lastContentRef.current = content
    }
  }, [content, getEnhancedHtml, basePath, editMode])

  // 监听来自 iframe 的消息
  useEffect(() => {
    const handleMessage = (event) => {
      const { type } = event.data
      
      if (type === 'contentChanged') {
        // 标记这是内部变化，避免重新加载 iframe
        isInternalChange.current = true
        
        // 清理注入的脚本后返回
        let cleanHtml = event.data.html
        cleanHtml = cleanHtml.replace(/<script>\s*\(function\(\)\s*\{[\s\S]*?initElements[\s\S]*?\}\)\(\);\s*<\/script>/g, '')
        cleanHtml = cleanHtml.replace(/\s*contenteditable="true"/g, '')
        cleanHtml = cleanHtml.replace(/\s*data-editable="true"/g, '')
        cleanHtml = cleanHtml.replace(/\s*data-image-slot="true"/g, '')
        // 清理 element-selected 类，保留其他类
        cleanHtml = cleanHtml.replace(/\bclass="([^"]*)"/g, (match, classes) => {
          const cleanedClasses = classes
            .split(/\s+/)
            .filter(c => c && c !== 'element-selected' && c !== 'edit-mode')
            .join(' ')
          return cleanedClasses ? `class="${cleanedClasses}"` : ''
        })
        // 移除空的 class 属性（包括前面的空格）
        cleanHtml = cleanHtml.replace(/\s+class=""/g, '')
        
        onChange(cleanHtml)
      } else if (type === 'elementSelected') {
        setSelectedElement(event.data)
      } else if (type === 'elementDeselected') {
        setSelectedElement(null)
      } else if (type === 'previewLocate') {
        // 预览模式下点击带有 data-slot 的元素，自动定位到 MD
        const { slotName } = event.data
        if (slotName && onLocateSlot) {
          onLocateSlot(slotName)
        }
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [onChange, onLocateSlot])

  // 切换编辑模式时通知 iframe
  useEffect(() => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.postMessage({
        type: 'toggleEditMode',
        value: editMode
      }, '*')
    }
  }, [editMode])

  // 发送样式修改命令到 iframe
  const sendStyleCommand = useCallback((property, value) => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.postMessage({
        type: 'setStyle',
        property,
        value
      }, '*')
    }
  }, [])

  // 触发图片替换
  const triggerImageReplace = useCallback(() => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.postMessage({
        type: 'replaceImage'
      }, '*')
    }
  }, [])

  // 容器尺寸
  const containerRef = useRef(null)
  const [containerSize, setContainerSize] = useState({ width: 800, height: 600 })

  // 监听容器尺寸变化
  useEffect(() => {
    if (!containerRef.current) return
    
    const resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect
        setContainerSize({ width: width - 32, height: height - 32 }) // 减去 padding
      }
    })
    
    resizeObserver.observe(containerRef.current)
    return () => resizeObserver.disconnect()
  }, [])

  // 设备模拟尺寸（锁定渲染宽度）
  const deviceSizes = {
    desktop: { width: 1920, height: 1080 },
    mobile: { width: 1024, height: 1366 }
  }

  // 获取当前设备尺寸
  const currentSize = deviceSizes[deviceMode]

  // 计算自适应缩放比例
  const fitScale = useMemo(() => {
    const scaleX = containerSize.width / currentSize.width
    const scaleY = containerSize.height / currentSize.height
    return Math.min(scaleX, scaleY, 1) * 100 // 最大不超过100%
  }, [containerSize, currentSize])

  // 实际使用的缩放比例（fit 模式使用自适应，否则使用手动设置）
  const [zoomMode, setZoomMode] = useState('fit') // 'fit' | 'manual'
  const actualZoom = zoomMode === 'fit' ? fitScale : zoom

  // 关闭属性面板
  const closePropertyPanel = useCallback(() => {
    setSelectedElement(null)
    // 清除 MD 高亮
    if (onClearMdHighlight) {
      onClearMdHighlight()
    }
    // 通知 iframe 取消选中
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.postMessage({ type: 'deselect' }, '*')
    }
  }, [onClearMdHighlight])

  return (
    <div className={`h-full preview-container relative flex ${isActive ? '' : ''}`}>
      {/* 主预览区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 预览控制栏 */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-[#0c0c12] border-b border-white/5">
          {/* 左侧：编辑模式开关 */}
          <div className="flex items-center gap-3">
            <button
              className={`px-4 py-2 rounded-xl transition-all flex items-center gap-2 text-sm font-medium ${
                editMode 
                  ? 'bg-gradient-to-r from-primary/20 to-secondary/20 text-primary border border-primary/30 shadow-[0_0_20px_rgba(0,242,255,0.15)]' 
                  : 'bg-white/[0.03] text-gray-400 border border-white/[0.06] hover:bg-white/[0.06] hover:text-gray-300'
              }`}
              onClick={() => {
                setEditMode(!editMode)
                if (editMode) setSelectedElement(null)
              }}
              title={editMode ? '退出编辑模式' : '进入编辑模式'}
            >
              <span className="material-icons text-base">{editMode ? 'edit' : 'edit_off'}</span>
              <span>{editMode ? '编辑中' : '预览模式'}</span>
              {editMode && <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>}
            </button>
            
            {editMode && (
              <div className="flex items-center gap-2 text-xs text-gray-500 pl-2 border-l border-white/10">
                <span className="material-icons text-xs text-primary/60">info</span>
                <span>单击选中 · 双击编辑文字/替换图片</span>
              </div>
            )}
          </div>

          {/* 中间：设备切换 */}
          <div className="flex items-center gap-1 p-1 bg-white/[0.02] rounded-xl">
            <button
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-2 text-xs font-medium ${
                deviceMode === 'desktop' 
                  ? 'bg-primary/10 text-primary shadow-sm' 
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
              onClick={() => { setDeviceMode('desktop'); setZoomMode('fit'); }}
              title="桌面视图 1920×1080"
            >
              <span className="material-icons text-sm">computer</span>
              <span>PC</span>
            </button>
            <button
              className={`px-3 py-1.5 rounded-lg transition-all flex items-center gap-2 text-xs font-medium ${
                deviceMode === 'mobile' 
                  ? 'bg-primary/10 text-primary shadow-sm' 
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
              onClick={() => { setDeviceMode('mobile'); setZoomMode('fit'); }}
              title="移动端视图 1024×1366"
            >
              <span className="material-icons text-sm">smartphone</span>
              <span>Mobile</span>
            </button>
          </div>

          {/* 右侧：缩放控制 */}
          <div className="flex items-center gap-1 p-1 bg-white/[0.02] rounded-xl">
            <button
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                zoomMode === 'fit' 
                  ? 'bg-primary/10 text-primary' 
                  : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
              }`}
              onClick={() => setZoomMode('fit')}
              title="自适应窗口"
            >
              适应
            </button>
            <div className="w-px h-4 bg-white/10 mx-1"></div>
            <button
              className="w-7 h-7 rounded-lg flex items-center justify-center text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all"
              onClick={() => { setZoomMode('manual'); setZoom(z => Math.max(10, z - 10)); }}
              title="缩小"
            >
              <span className="material-icons text-sm">remove</span>
            </button>
            <span 
              className={`text-xs min-w-[44px] text-center font-mono ${zoomMode === 'fit' ? 'text-primary' : 'text-gray-400'}`}
            >
              {Math.round(actualZoom)}%
            </span>
            <button
              className="w-7 h-7 rounded-lg flex items-center justify-center text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all"
              onClick={() => { setZoomMode('manual'); setZoom(z => Math.min(150, z + 10)); }}
              title="放大"
            >
              <span className="material-icons text-sm">add</span>
            </button>
          </div>
        </div>

        {/* iframe 容器 - 锁定尺寸预览 */}
        <div ref={containerRef} className="flex-1 overflow-auto bg-[#08080c] flex items-start justify-center p-4" style={{ minHeight: 0 }}>
          <div
            style={{
              width: currentSize.width,
              height: currentSize.height,
              transform: `scale(${actualZoom / 100})`,
              transformOrigin: 'top center',
              transition: 'transform 0.2s',
              boxShadow: '0 0 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.05)',
              borderRadius: deviceMode === 'mobile' ? '12px' : '4px',
              overflow: 'hidden',
              background: '#020617',
              flexShrink: 0
            }}
          >
            <iframe
              ref={iframeRef}
              style={{ 
                width: currentSize.width,
                height: currentSize.height,
                border: 'none'
              }}
              title="HTML Preview"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        </div>
      </div>
      
      {/* 右侧属性面板 */}
      {editMode && selectedElement && (
        <PropertyPanel
          element={selectedElement}
          onStyleChange={sendStyleCommand}
          onImageReplace={triggerImageReplace}
          onClose={closePropertyPanel}
          onLocateSlot={onLocateSlot}
        />
      )}
    </div>
  )
}

export default HtmlPane
