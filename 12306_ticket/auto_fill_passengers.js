/**
 * 🎫 12306 自动选择乘客脚本
 * 
 * 在点击"预订"进入订单页面后使用
 * 自动选择乘车人并提交订单
 * 
 * 乘车人：陈卓、冯巧玉、陈苇杭、陈妙可
 */

const AUTO_FILL_SCRIPT = `
(function() {
  'use strict';
  
  const CONFIG = {
    // 成人乘车人
    adults: ['陈卓', '冯巧玉'],
    // 儿童乘车人（需要确认）
    children: ['陈苇杭', '陈妙可'],
    // 所有乘车人
    allPassengers: ['陈卓', '冯巧玉', '陈苇杭', '陈妙可'],
    // 优先座位类型
    preferSeat: ['硬卧', '二等座'],
    // 自动提交（建议设为false，手动确认）
    autoSubmit: false
  };
  
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN');
    const styles = {
      info: 'color: #2196F3',
      success: 'color: #4CAF50; font-weight: bold',
      warning: 'color: #FF9800; font-weight: bold',
      error: 'color: #F44336; font-weight: bold'
    };
    console.log('%c[' + time + '] ' + msg, styles[type] || styles.info);
  };
  
  // 等待元素出现
  const waitForElement = (selector, timeout = 10000) => {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      const check = () => {
        const el = document.querySelector(selector);
        if (el) {
          resolve(el);
        } else if (Date.now() - startTime > timeout) {
          reject(new Error('Element not found: ' + selector));
        } else {
          setTimeout(check, 200);
        }
      };
      check();
    });
  };
  
  // 选择乘车人
  const selectPassengers = async () => {
    log('开始选择乘车人...', 'info');
    
    // 等待乘车人列表加载
    await new Promise(r => setTimeout(r, 1000));
    
    // 查找所有乘车人复选框
    const passengerList = document.querySelectorAll('#normal_passenger_id li');
    
    if (passengerList.length === 0) {
      log('未找到乘车人列表，请确认页面已加载', 'error');
      return false;
    }
    
    let selectedCount = 0;
    
    passengerList.forEach(li => {
      const label = li.querySelector('label');
      const checkbox = li.querySelector('input[type="checkbox"]');
      
      if (label && checkbox) {
        const name = label.textContent.trim();
        
        // 检查是否是目标乘车人
        if (CONFIG.allPassengers.some(p => name.includes(p))) {
          if (!checkbox.checked) {
            checkbox.click();
            log('✅ 已选择乘车人: ' + name, 'success');
          } else {
            log('☑️ 乘车人已选中: ' + name, 'info');
          }
          selectedCount++;
        }
      }
    });
    
    log('共选择 ' + selectedCount + ' 位乘车人', 'success');
    return selectedCount > 0;
  };
  
  // 选择座位类型
  const selectSeatType = async () => {
    log('检查座位选择...', 'info');
    
    // 座位类型选择（如果有的话）
    const seatSelects = document.querySelectorAll('select[id^="seatType_"]');
    
    seatSelects.forEach((select, index) => {
      // 找硬卧或二等座
      for (const option of select.options) {
        const text = option.text;
        if (CONFIG.preferSeat.some(s => text.includes(s))) {
          select.value = option.value;
          log('座位' + (index + 1) + '选择: ' + text, 'info');
          break;
        }
      }
    });
  };
  
  // 提交订单
  const submitOrder = () => {
    const submitBtn = document.getElementById('submitOrder_id');
    if (submitBtn && !submitBtn.disabled) {
      if (CONFIG.autoSubmit) {
        submitBtn.click();
        log('🚀 订单已提交！', 'success');
      } else {
        log('⚠️ 已准备好，请手动点击【提交订单】确认', 'warning');
        submitBtn.style.border = '3px solid red';
        submitBtn.style.animation = 'pulse 0.5s infinite';
      }
    }
  };
  
  // 主流程
  const autoFill = async () => {
    console.clear();
    log('═══════════════════════════════════════════', 'success');
    log('  🎫 12306 自动填写乘客信息', 'success');
    log('═══════════════════════════════════════════', 'success');
    log('');
    log('乘车人: ' + CONFIG.allPassengers.join(', '));
    log('');
    
    try {
      // 1. 选择乘车人
      const selected = await selectPassengers();
      
      if (!selected) {
        log('请先手动勾选乘车人', 'warning');
        return;
      }
      
      // 2. 选择座位
      await selectSeatType();
      
      // 3. 准备提交
      await new Promise(r => setTimeout(r, 500));
      submitOrder();
      
    } catch (e) {
      log('出错: ' + e.message, 'error');
    }
  };
  
  // 监听页面变化，自动执行
  const observer = new MutationObserver((mutations) => {
    // 检测是否进入订单确认页面
    const confirmPage = document.getElementById('normal_passenger_id');
    if (confirmPage && !window._autoFillExecuted) {
      window._autoFillExecuted = true;
      setTimeout(autoFill, 1500);
    }
  });
  
  // 暴露到全局
  window.passengerFill = {
    fill: autoFill,
    config: CONFIG,
    selectPassengers,
    selectSeatType,
    submitOrder
  };
  
  // 如果已经在订单页面，直接执行
  if (document.getElementById('normal_passenger_id')) {
    setTimeout(autoFill, 1000);
  } else {
    // 否则监听页面变化
    observer.observe(document.body, { childList: true, subtree: true });
    log('✅ 乘客自动填写脚本已加载', 'success');
    log('📌 进入订单页面后自动执行', 'warning');
    log('📌 或手动执行: passengerFill.fill()', 'warning');
  }
  
  return '乘客自动填写脚本已就绪';
})();
`;

console.log('═══════════════════════════════════════════════════════');
console.log('  🎫 自动选择乘客脚本 - 使用说明');
console.log('═══════════════════════════════════════════════════════');
console.log('');
console.log('【乘车人】陈卓、冯巧玉、陈苇杭、陈妙可');
console.log('');
console.log('【使用方法】');
console.log('1. 点击"预订"进入订单页面后');
console.log('2. 复制下方代码到控制台运行');
console.log('3. 脚本会自动选择乘车人');
console.log('4. 手动确认并点击提交订单');
console.log('');
console.log('═══════════════════════════════════════════════════════');
console.log('');
console.log(AUTO_FILL_SCRIPT);

module.exports = { AUTO_FILL_SCRIPT };
