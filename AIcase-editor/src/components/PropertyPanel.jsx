import React from 'react'

// 预设颜色
const PRESET_COLORS = [
  '#ffffff', '#f8fafc', '#e2e8f0', '#94a3b8', '#64748b',
  '#1e293b', '#0f172a', '#000000', '#00f2ff', '#7000ff',
  '#facc15', '#ef4444', '#22c55e', '#3b82f6', '#f97316',
]

// 预设字号
const FONT_SIZES = [
  '12px', '14px', '16px', '18px', '20px', '24px', 
  '28px', '32px', '36px', '42px', '48px', '56px', '64px', '72px'
]

function PropertyPanel({ element, onStyleChange, onImageReplace, onClose, onLocateSlot }) {
  // 当前样式
  const styles = element?.styles || {}
  const isImage = element?.isImage
  const slotName = element?.slotName
  const slotType = element?.slotType

  // 样式助手
  const setColor = (color) => onStyleChange('color', color)
  const setBgColor = (color) => onStyleChange('backgroundColor', color)
  const setFontSize = (size) => onStyleChange('fontSize', size)

  return (
    <div className="w-80 bg-[#0c0c12] border-l border-white/[0.06] flex flex-col h-full">
      {/* 面板头部 */}
      <div className="px-4 py-3 border-b border-white/[0.06] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-icons text-primary text-lg">
            {isImage ? 'image' : 'text_fields'}
          </span>
          <span className="text-sm font-medium text-white">
            {isImage ? '图片属性' : '元素属性'}
          </span>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 rounded-lg flex items-center justify-center text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all"
          title="关闭"
        >
          <span className="material-icons text-lg">close</span>
        </button>
      </div>

      {/* 元素信息 */}
      <div className="px-4 py-3 border-b border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="px-2 py-0.5 rounded bg-white/[0.05] font-mono">{element?.tagName || 'ELEMENT'}</span>
          {element?.className && (
            <span className="truncate opacity-60">.{element.className.split(' ')[0]}</span>
          )}
        </div>
        
        {/* 槽位信息和定位按钮 */}
        {slotName && (
          <div className="mt-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="material-icons text-xs text-secondary">bookmark</span>
              <span className="text-xs text-secondary font-mono">{slotName}</span>
              {slotType && slotType !== 'text' && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary/10 text-secondary/80">{slotType}</span>
              )}
            </div>
            <button
              onClick={() => onLocateSlot && onLocateSlot(slotName)}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded-lg bg-secondary/10 text-secondary hover:bg-secondary/20 transition-all"
              title="在 Markdown 中定位"
            >
              <span className="material-icons text-xs">find_in_page</span>
              <span>定位MD</span>
            </button>
          </div>
        )}
      </div>

      {/* 图片操作 */}
      {isImage ? (
        <div className="p-4">
          <button
            onClick={onImageReplace}
            className="w-full px-4 py-3 rounded-xl bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 text-yellow-400 flex items-center justify-center gap-2 hover:from-yellow-500/20 hover:to-orange-500/20 transition-all"
          >
            <span className="material-icons">upload</span>
            <span>替换图片</span>
          </button>
          <p className="text-xs text-gray-600 mt-3 text-center">
            双击预览区图片也可替换
          </p>
        </div>
      ) : (
        <>
          {/* 编辑提示 */}
          <div className="px-4 py-3 border-b border-white/[0.06] bg-primary/5">
            <div className="flex items-center gap-2 text-xs text-primary">
              <span className="material-icons text-sm">edit</span>
              <span>双击预览区文字可直接编辑</span>
            </div>
          </div>

          {/* 样式编辑 */}
          <div className="p-4 flex-1 overflow-auto space-y-5">
              {/* 文字颜色 */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">文字颜色</label>
                <div className="grid grid-cols-5 gap-2">
                  {PRESET_COLORS.map(color => (
                    <button
                      key={color}
                      className={`w-8 h-8 rounded-lg border-2 transition-all hover:scale-110 ${
                        styles.color === color ? 'border-primary shadow-[0_0_8px_rgba(0,242,255,0.3)]' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color }}
                      onClick={() => setColor(color)}
                      title={color}
                    />
                  ))}
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <input
                    type="color"
                    value={styles.color?.startsWith('#') ? styles.color : '#ffffff'}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-8 h-8 rounded cursor-pointer border-0 bg-transparent"
                  />
                  <input
                    type="text"
                    value={styles.color || ''}
                    onChange={(e) => setColor(e.target.value)}
                    className="flex-1 px-2 py-1.5 text-xs bg-white/[0.03] rounded-lg border border-white/[0.08] text-white font-mono focus:outline-none focus:border-primary/50"
                    placeholder="#ffffff"
                  />
                </div>
              </div>

              {/* 背景颜色 */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">背景颜色</label>
                <div className="grid grid-cols-5 gap-2">
                  {PRESET_COLORS.map(color => (
                    <button
                      key={color}
                      className={`w-8 h-8 rounded-lg border-2 transition-all hover:scale-110 ${
                        styles.backgroundColor === color ? 'border-primary shadow-[0_0_8px_rgba(0,242,255,0.3)]' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color }}
                      onClick={() => setBgColor(color)}
                      title={color}
                    />
                  ))}
                </div>
                <button
                  className="mt-2 px-3 py-1.5 text-xs rounded-lg bg-white/[0.03] border border-white/[0.08] text-gray-400 hover:bg-white/[0.06] transition-all"
                  onClick={() => setBgColor('transparent')}
                >
                  透明背景
                </button>
              </div>

              {/* 字号 */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">
                  字号 <span className="text-primary font-mono ml-1">{styles.fontSize || '16px'}</span>
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {FONT_SIZES.map(size => (
                    <button
                      key={size}
                      className={`px-2.5 py-1.5 text-xs rounded-lg transition-all ${
                        styles.fontSize === size 
                          ? 'bg-primary/20 text-primary border border-primary/30' 
                          : 'bg-white/[0.03] text-gray-400 border border-white/[0.06] hover:bg-white/[0.06]'
                      }`}
                      onClick={() => setFontSize(size)}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              </div>

              {/* 字重 */}
              <div>
                <label className="block text-xs text-gray-500 mb-2">字重</label>
                <div className="flex gap-2">
                  <button
                    className={`flex-1 px-3 py-2 text-sm rounded-lg transition-all ${
                      styles.fontWeight === 'normal' || !styles.fontWeight || styles.fontWeight === '400'
                        ? 'bg-primary/20 text-primary border border-primary/30' 
                        : 'bg-white/[0.03] text-gray-400 border border-white/[0.06] hover:bg-white/[0.06]'
                    }`}
                    onClick={() => onStyleChange('fontWeight', 'normal')}
                  >
                    常规
                  </button>
                  <button
                    className={`flex-1 px-3 py-2 text-sm rounded-lg font-bold transition-all ${
                      styles.fontWeight === '700' || styles.fontWeight === 'bold'
                        ? 'bg-primary/20 text-primary border border-primary/30' 
                        : 'bg-white/[0.03] text-gray-400 border border-white/[0.06] hover:bg-white/[0.06]'
                    }`}
                    onClick={() => onStyleChange('fontWeight', 'bold')}
                  >
                    粗体
                  </button>
                </div>
              </div>
            </div>
        </>
      )}

      {/* 提示区 */}
      <div className="px-4 py-3 border-t border-white/[0.06] bg-white/[0.02]">
        <div className="flex items-start gap-2 text-xs text-gray-500">
          <span className="material-icons text-sm text-primary/60">tips_and_updates</span>
          <div>
            {slotName ? (
              <>
                <p>点击<strong className="text-secondary">「定位MD」</strong>可跳转到对应的 Markdown 区域编辑</p>
                <p className="mt-1 opacity-80">槽位映射：<code className="text-secondary/80">{slotName}</code></p>
              </>
            ) : (
              <>
                <p>在预览区<strong className="text-gray-400">双击</strong>可直接编辑文字</p>
                <p className="mt-1">点击空白处取消选中</p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PropertyPanel
