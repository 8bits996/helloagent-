import React, { useState, useCallback, useRef, useEffect } from 'react'

// 预设颜色
const PRESET_COLORS = [
  '#ffffff', '#000000', '#00f2ff', '#7000ff', '#facc15',
  '#ef4444', '#22c55e', '#3b82f6', '#f97316', '#ec4899'
]

// 预设字号
const FONT_SIZES = [
  { label: '12px', value: '12px' },
  { label: '14px', value: '14px' },
  { label: '16px', value: '16px' },
  { label: '18px', value: '18px' },
  { label: '20px', value: '20px' },
  { label: '24px', value: '24px' },
  { label: '28px', value: '28px' },
  { label: '32px', value: '32px' },
  { label: '36px', value: '36px' },
  { label: '48px', value: '48px' },
  { label: '64px', value: '64px' },
]

function ElementToolbar({ element, position, onStyleChange, onImageReplace }) {
  const [showColorPicker, setShowColorPicker] = useState(null) // 'color' | 'background' | null
  const [showFontSizes, setShowFontSizes] = useState(false)
  const [customColor, setCustomColor] = useState('#00f2ff')
  const toolbarRef = useRef(null)

  // 当前样式
  const currentStyles = element?.styles || {}

  // 关闭所有下拉
  const closeDropdowns = useCallback(() => {
    setShowColorPicker(null)
    setShowFontSizes(false)
  }, [])

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (toolbarRef.current && !toolbarRef.current.contains(e.target)) {
        closeDropdowns()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [closeDropdowns])

  // 设置颜色
  const handleColorSelect = useCallback((color, type) => {
    onStyleChange(type, color)
    setShowColorPicker(null)
  }, [onStyleChange])

  // 设置字号
  const handleFontSizeSelect = useCallback((size) => {
    onStyleChange('fontSize', size)
    setShowFontSizes(false)
  }, [onStyleChange])

  // 切换粗体
  const toggleBold = useCallback(() => {
    const isBold = currentStyles.fontWeight === '700' || currentStyles.fontWeight === 'bold'
    onStyleChange('fontWeight', isBold ? 'normal' : 'bold')
  }, [currentStyles.fontWeight, onStyleChange])

  // 如果是图片，显示图片工具栏
  if (element?.isImage) {
    return (
      <div
        ref={toolbarRef}
        className="absolute z-50 bg-editor-sidebar rounded-lg shadow-2xl border border-editor-border p-2 flex items-center gap-2"
        style={{
          left: Math.max(10, position.x),
          top: Math.max(10, position.y),
        }}
      >
        <button
          className="toolbar-btn"
          onClick={onImageReplace}
          title="替换图片"
        >
          <span className="material-icons text-sm">image</span>
          <span>替换图片</span>
        </button>
      </div>
    )
  }

  return (
    <div
      ref={toolbarRef}
      className="absolute z-50 bg-editor-sidebar rounded-lg shadow-2xl border border-editor-border p-2 flex items-center gap-1"
      style={{
        left: Math.max(10, position.x),
        top: Math.max(10, position.y),
      }}
    >
      {/* 文字颜色 */}
      <div className="relative">
        <button
          className={`toolbar-btn px-2 ${showColorPicker === 'color' ? 'bg-editor-border' : ''}`}
          onClick={() => setShowColorPicker(showColorPicker === 'color' ? null : 'color')}
          title="文字颜色"
        >
          <span className="material-icons text-sm">format_color_text</span>
          <div 
            className="w-3 h-1 rounded-sm mt-0.5"
            style={{ backgroundColor: currentStyles.color || '#ffffff' }}
          />
        </button>
        
        {showColorPicker === 'color' && (
          <ColorPicker
            currentColor={currentStyles.color}
            onSelect={(color) => handleColorSelect(color, 'color')}
            customColor={customColor}
            onCustomChange={setCustomColor}
          />
        )}
      </div>

      {/* 背景颜色 */}
      <div className="relative">
        <button
          className={`toolbar-btn px-2 ${showColorPicker === 'background' ? 'bg-editor-border' : ''}`}
          onClick={() => setShowColorPicker(showColorPicker === 'background' ? null : 'background')}
          title="背景颜色"
        >
          <span className="material-icons text-sm">format_color_fill</span>
          <div 
            className="w-3 h-1 rounded-sm mt-0.5"
            style={{ backgroundColor: currentStyles.backgroundColor || 'transparent' }}
          />
        </button>
        
        {showColorPicker === 'background' && (
          <ColorPicker
            currentColor={currentStyles.backgroundColor}
            onSelect={(color) => handleColorSelect(color, 'backgroundColor')}
            customColor={customColor}
            onCustomChange={setCustomColor}
            showTransparent
          />
        )}
      </div>

      <div className="w-px h-6 bg-editor-border mx-1" />

      {/* 字号 */}
      <div className="relative">
        <button
          className={`toolbar-btn px-2 ${showFontSizes ? 'bg-editor-border' : ''}`}
          onClick={() => setShowFontSizes(!showFontSizes)}
          title="字号"
        >
          <span className="material-icons text-sm">format_size</span>
          <span className="text-xs ml-1">{currentStyles.fontSize || '16px'}</span>
        </button>
        
        {showFontSizes && (
          <div className="absolute top-full left-0 mt-1 bg-editor-sidebar rounded-lg shadow-2xl border border-editor-border p-1 min-w-[80px] max-h-[200px] overflow-y-auto">
            {FONT_SIZES.map(size => (
              <button
                key={size.value}
                className={`w-full text-left px-3 py-1.5 text-sm rounded hover:bg-editor-border transition-colors ${
                  currentStyles.fontSize === size.value ? 'text-primary' : 'text-gray-300'
                }`}
                onClick={() => handleFontSizeSelect(size.value)}
              >
                {size.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 粗体 */}
      <button
        className={`toolbar-btn px-2 ${
          currentStyles.fontWeight === '700' || currentStyles.fontWeight === 'bold'
            ? 'bg-primary/20 text-primary'
            : ''
        }`}
        onClick={toggleBold}
        title="粗体"
      >
        <span className="material-icons text-sm">format_bold</span>
      </button>
    </div>
  )
}

// 颜色选择器组件
function ColorPicker({ currentColor, onSelect, customColor, onCustomChange, showTransparent }) {
  return (
    <div className="absolute top-full left-0 mt-1 bg-editor-sidebar rounded-lg shadow-2xl border border-editor-border p-3 min-w-[180px]">
      {/* 预设颜色 */}
      <div className="grid grid-cols-5 gap-2 mb-3">
        {PRESET_COLORS.map(color => (
          <button
            key={color}
            className={`w-6 h-6 rounded border-2 transition-transform hover:scale-110 ${
              currentColor === color ? 'border-primary' : 'border-transparent'
            }`}
            style={{ backgroundColor: color }}
            onClick={() => onSelect(color)}
            title={color}
          />
        ))}
      </div>

      {/* 透明选项 */}
      {showTransparent && (
        <button
          className="w-full text-left px-2 py-1.5 text-sm rounded hover:bg-editor-border transition-colors text-gray-400 mb-2"
          onClick={() => onSelect('transparent')}
        >
          透明
        </button>
      )}

      {/* 自定义颜色 */}
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={customColor}
          onChange={(e) => onCustomChange(e.target.value)}
          className="w-8 h-8 rounded cursor-pointer border-0"
        />
        <input
          type="text"
          value={customColor}
          onChange={(e) => onCustomChange(e.target.value)}
          className="flex-1 px-2 py-1 text-sm bg-editor-bg rounded border border-editor-border text-white"
          placeholder="#000000"
        />
        <button
          className="px-2 py-1 text-sm bg-primary/20 text-primary rounded hover:bg-primary/30"
          onClick={() => onSelect(customColor)}
        >
          应用
        </button>
      </div>
    </div>
  )
}

export default ElementToolbar
