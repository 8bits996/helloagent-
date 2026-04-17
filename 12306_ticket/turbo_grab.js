/**
 * ⚡ 12306 极速抢票脚本 - 秒杀优化版
 * 
 * 🎯 核心优化:
 * 1. 自动处理所有弹窗（无需等待）
 * 2. 自动修改票种（陈妙可→成人票，陈苇杭→儿童票）
 * 3. 进入订单页面后极速执行
 * 4. 减少所有延迟
 */

(function() {
  'use strict';
  
  // ═══════════════════════════════════════════════════════════════
  // 🔧 配置区 - 按需修改
  // ═══════════════════════════════════════════════════════════════
  const CONFIG = {
    // 乘车人配置（顺序很重要！）
    passengers: [
      { name: '陈卓', ticketType: '1' },    // 1=成人票
      { name: '陈妙可', ticketType: '1' },  // 1=成人票（已满14岁）
      { name: '陈苇杭', ticketType: '2' },  // 2=儿童票
      { name: '冯巧玉', ticketType: '1' }   // 1=成人票
    ],
    
    // 优先席别（O=二等座, 3=硬卧, M=一等座）
    preferSeat: 'O',
    
    // 自动提交订单（true=自动提交，false=停在确认页）
    autoSubmit: false,
    
    // 超高速模式（减少所有延迟）
    turboMode: true
  };
  
  // ═══════════════════════════════════════════════════════════════
  // 🚀 核心函数
  // ═══════════════════════════════════════════════════════════════
  
  const log = (msg, type = 'info') => {
    const styles = {
      info: 'color:#2196F3',
      ok: 'color:#4CAF50;font-weight:bold',
      warn: 'color:#FF9800;font-weight:bold',
      err: 'color:#F44336;font-weight:bold'
    };
    console.log(`%c⚡ ${msg}`, styles[type] || styles.info);
  };
  
  // 自动关闭所有弹窗
  const autoCloseDialogs = () => {
    // 处理温馨提示弹窗（陈妙可年龄提示）
    const confirmBtns = document.querySelectorAll('.dhtmlx_window_active a.btn_def, .dhtmlx_wins a.btn_def');
    confirmBtns.forEach(btn => {
      if (btn.textContent.includes('确认') || btn.textContent.includes('确定')) {
        btn.click();
        log('自动关闭弹窗', 'ok');
      }
    });
    
    // 通用弹窗关闭
    const closeBtns = document.querySelectorAll('.dhtmlx_window_active .modal-close, .layui-layer-close, .close-btn');
    closeBtns.forEach(btn => btn.click());
  };
  
  // 极速选择乘车人
  const selectPassengers = () => {
    const list = document.getElementById('normal_passenger_id');
    if (!list) return false;
    
    const labels = list.querySelectorAll('li label');
    let count = 0;
    
    labels.forEach(label => {
      const name = label.textContent.trim();
      const checkbox = label.previousElementSibling;
      
      if (CONFIG.passengers.some(p => name.includes(p.name))) {
        if (checkbox && !checkbox.checked) {
          checkbox.click();
        }
        count++;
      }
    });
    
    log(`已选择 ${count} 位乘车人`, 'ok');
    return count > 0;
  };
  
  // 极速修改票种
  const fixTicketTypes = () => {
    // 获取所有乘客行
    const rows = document.querySelectorAll('#ticketInfo_id tr');
    
    rows.forEach((row, index) => {
      if (index === 0) return; // 跳过表头
      
      const nameInput = row.querySelector('input[id^="passengerName_"]');
      const ticketSelect = row.querySelector('select[id^="ticketType_"]');
      
      if (!nameInput || !ticketSelect) return;
      
      const name = nameInput.value;
      const passenger = CONFIG.passengers.find(p => name.includes(p.name));
      
      if (passenger && ticketSelect.value !== passenger.ticketType) {
        ticketSelect.value = passenger.ticketType;
        ticketSelect.dispatchEvent(new Event('change', { bubbles: true }));
        log(`${name} 票种→${passenger.ticketType === '1' ? '成人票' : '儿童票'}`, 'ok');
      }
    });
  };
  
  // 极速选择席别
  const selectSeatType = () => {
    const seatSelects = document.querySelectorAll('select[id^="seatType_"]');
    seatSelects.forEach(select => {
      if (select.querySelector(`option[value="${CONFIG.preferSeat}"]`)) {
        select.value = CONFIG.preferSeat;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  };
  
  // 提交订单
  const submitOrder = () => {
    const btn = document.getElementById('submitOrder_id');
    if (btn && !btn.disabled) {
      if (CONFIG.autoSubmit) {
        btn.click();
        log('🚀 订单已提交！', 'ok');
      } else {
        btn.style.cssText = 'border:3px solid red !important;animation:blink 0.3s infinite;';
        log('✅ 已准备好，请点击【提交订单】', 'warn');
      }
    }
  };
  
  // ═══════════════════════════════════════════════════════════════
  // ⚡ 主执行流程 - 极速串行
  // ═══════════════════════════════════════════════════════════════
  
  const turboExecute = async () => {
    console.clear();
    log('═══════════════════════════════════════', 'ok');
    log('  ⚡ 12306 极速抢票 - 执行中...', 'ok');
    log('═══════════════════════════════════════', 'ok');
    
    const delay = CONFIG.turboMode ? 50 : 300;
    
    // Step 1: 关闭弹窗
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 2: 选择乘车人
    selectPassengers();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 3: 再次关闭可能出现的弹窗
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 4: 修改票种
    fixTicketTypes();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 5: 关闭票种修改后的弹窗
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 6: 选择席别
    selectSeatType();
    await new Promise(r => setTimeout(r, delay));
    
    // Step 7: 准备提交
    submitOrder();
    
    log('═══════════════════════════════════════', 'ok');
    log('  ✅ 极速填写完成！', 'ok');
    log('═══════════════════════════════════════', 'ok');
  };
  
  // ═══════════════════════════════════════════════════════════════
  // 🔄 持续监控弹窗
  // ═══════════════════════════════════════════════════════════════
  
  // 每100ms检查并关闭弹窗
  const dialogWatcher = setInterval(() => {
    autoCloseDialogs();
  }, 100);
  
  // 10秒后停止监控
  setTimeout(() => clearInterval(dialogWatcher), 10000);
  
  // ═══════════════════════════════════════════════════════════════
  // 🎯 暴露全局接口
  // ═══════════════════════════════════════════════════════════════
  
  window.turboGrab = {
    execute: turboExecute,
    selectPassengers,
    fixTicketTypes,
    autoCloseDialogs,
    submitOrder,
    config: CONFIG
  };
  
  // 立即执行
  turboExecute();
  
  return '⚡ 极速抢票脚本已执行';
})();
