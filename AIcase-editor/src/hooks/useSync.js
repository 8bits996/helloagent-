import { useState, useCallback, useEffect, useRef } from 'react'

/**
 * 基于槽位的 MD ↔ HTML 同步 Hook
 * 
 * 核心原理：
 * 1. HTML 中用 data-slot="xxx" 标记可编辑区域
 * 2. MD 中用 <!-- @slot:xxx --> 内容 <!-- @/slot --> 对应
 * 3. 同步时只替换槽位内容，保留所有样式和结构
 */

// MD 槽位正则
const MD_SLOT_REGEX = /<!--\s*@slot:(\w+)\s*-->([\s\S]*?)<!--\s*@\/slot\s*-->/g
const MD_SLOT_SINGLE_REGEX = /<!--\s*@slot:(\w+)\s*-->([\s\S]*?)<!--\s*@\/slot\s*-->/

/**
 * 从 HTML 中提取所有槽位及其内容
 */
function extractSlotsFromHtml(html) {
  const slots = {}
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  
  // 查找所有带 data-slot 的元素
  const slotElements = doc.querySelectorAll('[data-slot]')
  
  slotElements.forEach(el => {
    const slotName = el.getAttribute('data-slot')
    const slotType = el.getAttribute('data-type') || 'text'
    
    let content = ''
    if (slotType === 'image') {
      // 图片槽位取 src
      const img = el.tagName === 'IMG' ? el : el.querySelector('img')
      content = img ? img.src : ''
    } else {
      // 文本/富文本槽位取 innerHTML 或 textContent
      const rawContent = slotType === 'richtext' ? el.innerHTML : el.textContent
      content = rawContent ? rawContent.trim() : ''
    }
    
    slots[slotName] = {
      content,
      type: slotType
    }
  })
  
  return slots
}

/**
 * 从 MD 中提取所有槽位及其内容
 */
function extractSlotsFromMd(md) {
  const slots = {}
  let match
  
  // 重置正则
  MD_SLOT_REGEX.lastIndex = 0
  
  while ((match = MD_SLOT_REGEX.exec(md)) !== null) {
    const slotName = match[1]
    const content = match[2] ? match[2].trim() : ''
    slots[slotName] = { content }
  }
  
  return slots
}

/**
 * 将槽位内容应用到 HTML
 */
function applySlotsToHtml(html, slots) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  
  Object.entries(slots).forEach(([slotName, slotData]) => {
    const el = doc.querySelector(`[data-slot="${slotName}"]`)
    if (!el) return
    
    const slotType = el.getAttribute('data-type') || 'text'
    
    if (slotType === 'image') {
      const img = el.tagName === 'IMG' ? el : el.querySelector('img')
      if (img && slotData.content) {
        img.src = slotData.content
      }
    } else if (slotType === 'richtext') {
      // 富文本：简单的 MD 转 HTML
      el.innerHTML = simpleMarkdownToHtml(slotData.content)
    } else {
      // 纯文本
      el.textContent = slotData.content
    }
  })
  
  return '<!DOCTYPE html>\n' + doc.documentElement.outerHTML
}

/**
 * 将槽位内容应用到 MD
 */
function applySlotsToMd(md, slots) {
  let result = md
  
  Object.entries(slots).forEach(([slotName, slotData]) => {
    const regex = new RegExp(
      `<!--\\s*@slot:${slotName}\\s*-->[\\s\\S]*?<!--\\s*@\\/slot\\s*-->`,
      'g'
    )
    result = result.replace(regex, `<!-- @slot:${slotName} -->\n${slotData.content}\n<!-- @/slot -->`)
  })
  
  return result
}

/**
 * 从 HTML 生成结构化 MD（初始化时使用）
 */
function generateMdFromHtml(html, templateConfig = null) {
  const slots = extractSlotsFromHtml(html)
  const sections = templateConfig?.sections || []
  
  let md = '# 案例内容编辑\n\n'
  md += '> 提示：修改下方槽位内容，右侧 HTML 会实时同步更新\n\n'
  
  if (sections.length > 0) {
    // 按 section 分组生成
    sections.forEach(section => {
      md += `## ${section.label}\n\n`
      
      section.slots?.forEach(slotName => {
        const slot = slots[slotName]
        if (slot) {
          const label = templateConfig?.slots?.[slotName]?.label || slotName
          md += `### ${label}\n`
          md += `<!-- @slot:${slotName} -->\n`
          md += `${slot.content || '【待填写】'}\n`
          md += `<!-- @/slot -->\n\n`
        }
      })
    })
  } else {
    // 无配置时，按槽位顺序生成
    Object.entries(slots).forEach(([slotName, slot]) => {
      md += `### ${slotName}\n`
      md += `<!-- @slot:${slotName} -->\n`
      md += `${slot.content || '【待填写】'}\n`
      md += `<!-- @/slot -->\n\n`
    })
  }
  
  return md
}

/**
 * 简单的 Markdown 转 HTML（用于富文本槽位）
 */
function simpleMarkdownToHtml(md) {
  if (!md) return ''
  
  return md
    // 加粗
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 链接
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2">$1</a>')
    // 换行
    .replace(/\n/g, '<br>')
}

/**
 * HTML 富文本转 Markdown
 */
function htmlToSimpleMarkdown(html) {
  if (!html) return ''
  
  return html
    .replace(/<strong>(.+?)<\/strong>/g, '**$1**')
    .replace(/<b>(.+?)<\/b>/g, '**$1**')
    .replace(/<em>(.+?)<\/em>/g, '*$1*')
    .replace(/<i>(.+?)<\/i>/g, '*$1*')
    .replace(/<a href="(.+?)">(.+?)<\/a>/g, '[$2]($1)')
    .replace(/<br\s*\/?>/g, '\n')
    .replace(/<[^>]+>/g, '') // 移除其他标签
    .trim()
}

/**
 * useSync Hook
 */
export function useSync(initialHtml, initialMd, activePane) {
  const [htmlContent, setHtmlContent] = useState(initialHtml)
  const [mdContent, setMdContent] = useState('')
  const htmlTemplateRef = useRef(initialHtml) // 保存原始模板结构
  const syncLock = useRef(false)
  const templateConfigRef = useRef(null)
  const isInitializedRef = useRef(false)
  
  // 监听外部传入的 initialHtml 变化（撤销/重做时触发）
  useEffect(() => {
    if (syncLock.current) return
    
    // 跳过首次渲染，避免覆盖初始化逻辑
    if (!isInitializedRef.current) {
      isInitializedRef.current = true
      return
    }
    
    syncLock.current = true
    setHtmlContent(initialHtml)
    
    // 同步更新 MD 中的槽位
    const slots = extractSlotsFromHtml(initialHtml)
    setMdContent(prev => {
      let updated = prev
      Object.entries(slots).forEach(([slotName, slotData]) => {
        const regex = new RegExp(
          `(<!--\\s*@slot:${slotName}\\s*-->)[\\s\\S]*?(<!--\\s*@\\/slot\\s*-->)`,
          'g'
        )
        if (regex.test(updated)) {
          updated = updated.replace(regex, `$1\n${slotData.content}\n$2`)
        }
      })
      return updated
    })
    
    htmlTemplateRef.current = initialHtml
    
    setTimeout(() => {
      syncLock.current = false
    }, 50)
  }, [initialHtml])
  
  // 初始化：从 HTML 生成 MD
  useEffect(() => {
    if (initialHtml && !initialMd) {
      // 尝试加载模板配置
      loadTemplateConfig(initialHtml).then(config => {
        templateConfigRef.current = config
        const generatedMd = generateMdFromHtml(initialHtml, config)
        setMdContent(generatedMd)
      })
    } else if (initialMd) {
      setMdContent(initialMd)
    }
    htmlTemplateRef.current = initialHtml
  }, [])

  /**
   * 尝试加载模板配置
   */
  async function loadTemplateConfig(html) {
    try {
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const templateType = doc.querySelector('[data-template]')?.getAttribute('data-template')
      
      if (templateType === '16x9') {
        // 在实际项目中，这里会从 JSON 文件加载
        // 这里简化处理，返回基本配置
        return {
          name: '横版16:9模板',
          sections: [
            { id: 'header', label: '头部区域', slots: ['title', 'title_highlight', 'subtitle', 'tag'] },
            { id: 'background', label: '客户背景', slots: ['customer_info', 'challenge', 'metric1_value', 'metric1_name', 'metric2_value', 'metric2_name'] },
            { id: 'strategy', label: '投放方案', slots: ['strategy1_title', 'strategy1_desc', 'strategy2_title', 'strategy2_desc', 'strategy3_title', 'strategy3_desc'] },
            { id: 'result', label: '数据表现', slots: ['chart_title', 'chart_value', 'trend_title', 'trend_note'] },
            { id: 'footer', label: '底部区域', slots: ['pill1_name', 'pill1_value', 'pill2_name', 'pill2_value', 'why_desc', 'step1', 'step2', 'step3', 'copyright', 'contact'] }
          ],
          slots: {
            title: { label: '主标题' },
            title_highlight: { label: '高亮关键词' },
            subtitle: { label: '英文副标题' },
            tag: { label: '标签' },
            customer_info: { label: '客户信息' },
            challenge: { label: '面临挑战' },
            metric1_value: { label: '指标1数值' },
            metric1_name: { label: '指标1名称' },
            metric2_value: { label: '指标2数值' },
            metric2_name: { label: '指标2名称' },
            strategy1_title: { label: '策略1标题' },
            strategy1_desc: { label: '策略1描述' },
            strategy2_title: { label: '策略2标题' },
            strategy2_desc: { label: '策略2描述' },
            strategy3_title: { label: '策略3标题' },
            strategy3_desc: { label: '策略3描述' },
            chart_title: { label: '图表标题' },
            chart_value: { label: '图表数值' },
            trend_title: { label: '趋势标题' },
            trend_note: { label: '趋势说明' },
            pill1_name: { label: '数据药丸1名称' },
            pill1_value: { label: '数据药丸1数值' },
            pill2_name: { label: '数据药丸2名称' },
            pill2_value: { label: '数据药丸2数值' },
            why_desc: { label: '核心价值' },
            step1: { label: '步骤1' },
            step2: { label: '步骤2' },
            step3: { label: '步骤3' },
            copyright: { label: '版权信息' },
            contact: { label: '联系方式' }
          }
        }
      } else if (templateType === 'long') {
        return {
          name: '长图模板',
          sections: [
            { id: 'header', label: '头部区域', slots: ['tag', 'title', 'title_highlight', 'subtitle', 'intro'] },
            { id: 'data_cards', label: '核心数据', slots: ['data1_value', 'data1_name', 'data2_value', 'data2_name', 'data3_value', 'data3_name'] },
            { id: 'background', label: '客户背景', slots: ['customer_info', 'painpoint1', 'painpoint2', 'painpoint3', 'goal1', 'goal2', 'goal3'] },
            { id: 'strategy', label: '投放方案', slots: ['solution_name', 'strategy1_title', 'strategy1_desc', 'strategy2_title', 'strategy2_desc', 'strategy3_title', 'strategy3_desc'] },
            { id: 'result', label: '投放效果', slots: ['result_metric1_name', 'result_metric1_value', 'result_metric2_name', 'result_metric2_value'] }
          ]
        }
      }
      
      return null
    } catch (e) {
      console.error('Failed to load template config:', e)
      return null
    }
  }

  /**
   * 更新 HTML（从 HTML 面板编辑）
   */
  const updateHtml = useCallback((newHtml) => {
    if (syncLock.current) return
    
    syncLock.current = true
    setHtmlContent(newHtml)
    
    // 提取槽位变化，同步到 MD
    const slots = extractSlotsFromHtml(newHtml)
    setMdContent(prev => {
      // 更新 MD 中对应的槽位
      let updated = prev
      Object.entries(slots).forEach(([slotName, slotData]) => {
        const regex = new RegExp(
          `(<!--\\s*@slot:${slotName}\\s*-->)[\\s\\S]*?(<!--\\s*@\\/slot\\s*-->)`,
          'g'
        )
        if (regex.test(updated)) {
          updated = updated.replace(regex, `$1\n${slotData.content}\n$2`)
        }
      })
      return updated
    })
    
    // 更新模板引用
    htmlTemplateRef.current = newHtml
    
    setTimeout(() => {
      syncLock.current = false
    }, 50)
  }, [])

  /**
   * 更新 MD（从 MD 面板编辑）
   */
  const updateMd = useCallback((newMd) => {
    if (syncLock.current) return
    
    syncLock.current = true
    setMdContent(newMd)
    
    // 提取 MD 中的槽位内容，应用到 HTML
    const slots = extractSlotsFromMd(newMd)
    const newHtml = applySlotsToHtml(htmlTemplateRef.current, slots)
    setHtmlContent(newHtml)
    
    setTimeout(() => {
      syncLock.current = false
    }, 50)
  }, [])

  /**
   * 手动从 HTML 同步到 MD
   */
  const syncFromHtml = useCallback(() => {
    const generatedMd = generateMdFromHtml(htmlContent, templateConfigRef.current)
    setMdContent(generatedMd)
  }, [htmlContent])

  /**
   * 手动从 MD 同步到 HTML
   */
  const syncFromMd = useCallback(() => {
    const slots = extractSlotsFromMd(mdContent)
    const newHtml = applySlotsToHtml(htmlTemplateRef.current, slots)
    setHtmlContent(newHtml)
  }, [mdContent])

  /**
   * 获取当前所有槽位
   */
  const getSlots = useCallback(() => {
    return extractSlotsFromHtml(htmlContent)
  }, [htmlContent])

  /**
   * 直接设置内容（不触发同步，用于版本恢复等场景）
   */
  const setContents = useCallback((html, md) => {
    syncLock.current = true
    setHtmlContent(html)
    setMdContent(md)
    htmlTemplateRef.current = html
    setTimeout(() => {
      syncLock.current = false
    }, 50)
  }, [])

  return {
    htmlContent,
    mdContent,
    updateHtml,
    updateMd,
    syncFromHtml,
    syncFromMd,
    getSlots,
    setContents
  }
}

// 导出工具函数供其他模块使用
export {
  extractSlotsFromHtml,
  extractSlotsFromMd,
  applySlotsToHtml,
  applySlotsToMd,
  generateMdFromHtml
}
