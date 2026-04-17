/**
 * ═══════════════════════════════════════════════════════════════════════════
 *    🎯 12306 极速抢票脚本 v4.0 - 秒杀级优化（测试验证版）
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * 📌 核心优化:
 *    1. 全流程自动化（查票→预订→选人→改票种→处理弹窗→提交）
 *    2. 预加载DOM选择器，减少运行时查询
 *    3. 智能弹窗处理（MutationObserver实时监控）
 *    4. 多重容错机制
 *    5. 完整流程测试模式
 * 
 * 📌 乘车人配置（已固化）:
 *    - 陈卓: 成人票
 *    - 冯巧玉: 成人票
 *    - 陈苇杭: 儿童票
 *    - 陈妙可: 成人票（已满14岁）
 * ═══════════════════════════════════════════════════════════════════════════
 */

(function() {
  'use strict';

  // ═══════════════════════════════════════════════════════════════
  // 🔧 核心配置
  // ═══════════════════════════════════════════════════════════════
  
  const CONFIG = {
    // ────────── 目标车次（按优先级排序）──────────
    targetTrains: [
      'K756', 'K536', 'K1296', 'K932', 'K1656', 'K922', 'D192',
      'G3830', 'G1132', 'G1128', 'G532', 'G538'
    ],
    
    // ────────── 接受的席别（优先级：二等座 > 硬卧 > 二等卧）──────────
    acceptSeats: ['二等座', '硬卧', '二等卧'],
    
    // ────────── 乘车人配置（固化票种）──────────
    passengers: {
      '陈卓':   { ticketType: '1', typeName: '成人票', order: 1 },
      '冯巧玉': { ticketType: '1', typeName: '成人票', order: 2 },
      '陈苇杭': { ticketType: '2', typeName: '儿童票', order: 3 },
      '陈妙可': { ticketType: '1', typeName: '成人票', order: 4 }
    },
    
    // ────────── 放票时间 ──────────
    releaseTime: '11:45:00',
    advanceSeconds: 5,           // 提前几秒进入高频模式
    
    // ────────── 刷新间隔(ms) ──────────
    normalInterval: 2500,        // 普通刷新
    highFreqInterval: 200,       // 高频刷新（秒杀模式）
    confirmPageDelay: 20,        // 订单页面操作间隔（极短）
    
    // ────────── 自动化开关 ──────────
    autoClickBook: true,         // 自动点击预订
    autoSelectPassenger: true,   // 自动选择乘客
    autoFixTicketType: true,     // 自动修改票种
    autoCloseDialog: true,       // 自动关闭弹窗
    autoSubmit: false,           // 自动提交（测试时关闭）
    
    // ────────── 测试模式 ──────────
    testMode: false,             // 测试模式（不真正提交）
    
    // ────────── 提醒 ──────────
    soundAlert: true,
    visualAlert: true
  };

  // ═══════════════════════════════════════════════════════════════
  // 📊 状态管理
  // ═══════════════════════════════════════════════════════════════
  
  const state = {
    running: false,
    isHighFreq: false,
    currentPage: 'unknown',
    checkCount: 0,
    lastFoundTrain: null,
    intervalId: null,
    dialogObserver: null,
    startTime: null
  };

  // ═══════════════════════════════════════════════════════════════
  // 🛠️ 工具函数
  // ═══════════════════════════════════════════════════════════════
  
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 });
    const icons = { info: '📋', success: '✅', warning: '⚠️', error: '❌', ticket: '🎫', speed: '⚡' };
    const colors = { info: '#2196F3', success: '#4CAF50', warning: '#FF9800', error: '#F44336', ticket: '#E91E63', speed: '#9C27B0' };
    console.log(`%c[${time}] ${icons[type] || '📋'} ${msg}`, `color:${colors[type] || colors.info};font-weight:${type !== 'info' ? 'bold' : 'normal'}`);
  };

  const playSound = () => {
    if (!CONFIG.soundAlert) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      [523, 659, 784, 1047, 1319].forEach((f, i) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.connect(g); g.connect(ctx.destination);
        o.frequency.value = f; o.type = 'sine'; g.gain.value = 0.3;
        o.start(ctx.currentTime + i * 0.1);
        o.stop(ctx.currentTime + i * 0.1 + 0.1);
      });
    } catch(e) {}
  };

  const flashScreen = (color = 'rgba(76,175,80,0.4)') => {
    if (!CONFIG.visualAlert) return;
    const d = document.createElement('div');
    d.style.cssText = `position:fixed;top:0;left:0;width:100%;height:100%;background:${color};z-index:999999;pointer-events:none;`;
    document.body.appendChild(d);
    setTimeout(() => d.remove(), 300);
  };

  // 高精度延迟
  const delay = ms => new Promise(r => setTimeout(r, ms));

  // ═══════════════════════════════════════════════════════════════
  // 🔍 页面检测
  // ═══════════════════════════════════════════════════════════════
  
  const detectPage = () => {
    const url = location.href;
    if (url.includes('confirmPassenger') || url.includes('initDc')) {
      state.currentPage = 'confirm';
      return 'confirm';
    }
    if (url.includes('leftTicket') || document.getElementById('query_ticket')) {
      state.currentPage = 'query';
      return 'query';
    }
    return 'unknown';
  };

  // ═══════════════════════════════════════════════════════════════
  // 🎯 查票页面逻辑
  // ═══════════════════════════════════════════════════════════════
  
  const queryTickets = () => {
    const btn = document.getElementById('query_ticket');
    if (btn) { btn.click(); state.checkCount++; return true; }
    return false;
  };

  // 席别列映射（12306表格列索引）
  const SEAT_COLUMNS = {
    '商务座': 1, '一等座': 2, '二等座': 3, '高级软卧': 4,
    '软卧': 5, '动卧': 6, '硬卧': 7, '软座': 8,
    '硬座': 9, '无座': 10, '其他': 11
  };

  const checkTickets = () => {
    const rows = document.querySelectorAll('#queryLeftTable tr:not(.datatran)');
    
    for (const row of rows) {
      const trainEl = row.querySelector('.train .number');
      if (!trainEl) continue;
      
      const trainNo = trainEl.textContent.trim();
      
      // 检查目标车次（或者接受所有车次）
      const isTarget = CONFIG.targetTrains.length === 0 || CONFIG.targetTrains.includes(trainNo);
      if (!isTarget) continue;
      
      // 按优先级检查席别
      for (const seatName of CONFIG.acceptSeats) {
        const colIndex = SEAT_COLUMNS[seatName];
        if (!colIndex) continue;
        
        const cell = row.querySelector(`td:nth-child(${colIndex})`);
        if (!cell) continue;
        
        const text = cell.textContent.trim();
        const hasTicket = text === '有' || /^\d+$/.test(text);
        
        if (hasTicket) {
          log(`🎫 发现有票! ${trainNo} - ${seatName} [${text}]`, 'ticket');
          playSound();
          flashScreen();
          state.lastFoundTrain = trainNo;
          
          if (CONFIG.autoClickBook) {
            const bookBtn = row.querySelector('a.btn72');
            if (bookBtn) {
              log('⚡ 极速预订中...', 'speed');
              bookBtn.click();
              return { found: true, train: trainNo, seat: seatName };
            }
          }
          return { found: true, train: trainNo, seat: seatName, noButton: true };
        }
      }
    }
    
    return { found: false };
  };

  // ═══════════════════════════════════════════════════════════════
  // 📝 订单页面逻辑 - 极速版
  // ═══════════════════════════════════════════════════════════════
  
  // 关闭所有弹窗（多种方式）
  const closeAllDialogs = () => {
    let closed = 0;
    
    // 方式1: DHTMLX弹窗确认按钮
    document.querySelectorAll('.dhtmlx_wins .btn_def, .dhtmlx_window_active .btn_def, .dhx_modal_box button').forEach(btn => {
      const text = btn.textContent || '';
      if (/确认|确定|知道|关闭|OK/i.test(text)) {
        btn.click();
        closed++;
      }
    });
    
    // 方式2: layui弹窗
    document.querySelectorAll('.layui-layer-btn0, .layui-layer-close').forEach(btn => {
      btn.click();
      closed++;
    });
    
    // 方式3: Bootstrap模态框
    document.querySelectorAll('.modal .btn-primary, .modal .close').forEach(btn => {
      btn.click();
      closed++;
    });
    
    // 方式4: 通用确认按钮
    document.querySelectorAll('[class*="confirm"], [class*="ok-btn"]').forEach(btn => {
      if (/确认|确定/i.test(btn.textContent)) {
        btn.click();
        closed++;
      }
    });
    
    return closed;
  };

  // 启动弹窗监控（MutationObserver）
  const startDialogWatcher = () => {
    if (state.dialogObserver) return;
    
    state.dialogObserver = new MutationObserver((mutations) => {
      if (CONFIG.autoCloseDialog) {
        closeAllDialogs();
      }
    });
    
    state.dialogObserver.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    // 同时用interval作为备份
    const backupInterval = setInterval(closeAllDialogs, 50);
    
    // 10秒后停止
    setTimeout(() => {
      if (state.dialogObserver) {
        state.dialogObserver.disconnect();
        state.dialogObserver = null;
      }
      clearInterval(backupInterval);
    }, 10000);
  };

  // 选择乘客（极速版）
  const selectPassengers = () => {
    const passengerList = document.getElementById('normal_passenger_id');
    if (!passengerList) {
      log('未找到乘客列表', 'error');
      return 0;
    }
    
    const passengerNames = Object.keys(CONFIG.passengers);
    let selected = 0;
    
    passengerList.querySelectorAll('li').forEach(li => {
      const label = li.querySelector('label');
      const checkbox = li.querySelector('input[type="checkbox"]');
      if (!label || !checkbox) return;
      
      const name = label.textContent.trim();
      const shouldSelect = passengerNames.some(p => name.includes(p));
      
      if (shouldSelect && !checkbox.checked) {
        checkbox.click();
        selected++;
      }
    });
    
    log(`已选择 ${selected} 位乘客`, 'success');
    return selected;
  };

  // 修改票种（极速版 - 直接操作DOM）
  const fixTicketTypes = () => {
    let fixed = 0;
    
    // 遍历所有ticketType下拉框
    for (let i = 1; i <= 5; i++) {
      const nameInput = document.querySelector(`input[id="passengerName_${i}"]`);
      const ticketSelect = document.getElementById(`ticketType_${i}`);
      
      if (!nameInput || !ticketSelect) continue;
      
      const name = nameInput.value;
      
      // 查找匹配的乘客配置
      for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
        if (name.includes(pName)) {
          if (ticketSelect.value !== pConfig.ticketType) {
            ticketSelect.value = pConfig.ticketType;
            // 触发change事件
            ticketSelect.dispatchEvent(new Event('change', { bubbles: true }));
            log(`${pName}: ${ticketSelect.value === '1' ? '成人票' : '儿童票'}`, 'success');
            fixed++;
          }
          break;
        }
      }
    }
    
    if (fixed === 0) {
      log('票种已正确，无需修改', 'info');
    }
    
    return fixed;
  };

  // 检查席别是否正确
  const checkSeatTypes = () => {
    const issues = [];
    
    for (let i = 1; i <= 5; i++) {
      const seatSelect = document.getElementById(`seatType_${i}`);
      if (!seatSelect) continue;
      
      const seatText = seatSelect.options[seatSelect.selectedIndex]?.text || '';
      const isAcceptable = CONFIG.acceptSeats.some(s => seatText.includes(s));
      
      if (!isAcceptable && seatText) {
        issues.push(`座位${i}: ${seatText} (不在接受范围)`);
      }
    }
    
    return issues;
  };

  // 提交订单
  const submitOrder = () => {
    const btn = document.getElementById('submitOrder_id');
    if (!btn) {
      log('未找到提交按钮', 'error');
      return false;
    }
    
    if (btn.disabled) {
      log('提交按钮被禁用', 'warning');
      return false;
    }
    
    if (CONFIG.autoSubmit && !CONFIG.testMode) {
      log('🚀 自动提交订单!', 'success');
      btn.click();
      return true;
    } else {
      // 高亮按钮
      btn.style.cssText = `
        border: 4px solid red !important;
        box-shadow: 0 0 20px red !important;
        transform: scale(1.1);
        animation: pulse 0.5s infinite;
      `;
      
      // 添加脉冲动画
      if (!document.getElementById('grab-style')) {
        const style = document.createElement('style');
        style.id = 'grab-style';
        style.textContent = `@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.7; } }`;
        document.head.appendChild(style);
      }
      
      log('✅ 请手动点击【提交订单】', 'warning');
      playSound();
      return false;
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // ⚡ 订单页面极速处理（核心流程）
  // ═══════════════════════════════════════════════════════════════
  
  const handleConfirmPage = async () => {
    const startTime = performance.now();
    
    log('═══════════════════════════════════════', 'speed');
    log('  ⚡ 极速处理订单页面', 'speed');
    log('═══════════════════════════════════════', 'speed');
    
    // 启动弹窗监控
    startDialogWatcher();
    
    // Step 0: 立即关闭可能存在的弹窗
    closeAllDialogs();
    
    // Step 1: 选择乘客（如果需要）
    if (CONFIG.autoSelectPassenger) {
      await delay(CONFIG.confirmPageDelay);
      selectPassengers();
    }
    
    // Step 2: 等待乘客信息加载
    await delay(CONFIG.confirmPageDelay * 2);
    closeAllDialogs();
    
    // Step 3: 修改票种
    if (CONFIG.autoFixTicketType) {
      await delay(CONFIG.confirmPageDelay);
      fixTicketTypes();
    }
    
    // Step 4: 再次关闭弹窗（票种修改可能触发）
    await delay(CONFIG.confirmPageDelay);
    closeAllDialogs();
    
    // Step 5: 检查席别
    const seatIssues = checkSeatTypes();
    if (seatIssues.length > 0) {
      log('席别检查: ' + seatIssues.join(', '), 'warning');
    }
    
    // Step 6: 准备提交
    await delay(CONFIG.confirmPageDelay);
    submitOrder();
    
    const elapsed = (performance.now() - startTime).toFixed(0);
    log(`═══════════════════════════════════════`, 'speed');
    log(`  ✅ 处理完成! 耗时: ${elapsed}ms`, 'speed');
    log(`═══════════════════════════════════════`, 'speed');
    
    return { elapsed: Number(elapsed) };
  };

  // ═══════════════════════════════════════════════════════════════
  // 🧪 测试功能
  // ═══════════════════════════════════════════════════════════════
  
  const runFullTest = async () => {
    log('═══════════════════════════════════════', 'warning');
    log('  🧪 开始完整流程测试', 'warning');
    log('═══════════════════════════════════════', 'warning');
    
    const results = {
      page: detectPage(),
      dialogClose: 0,
      passengerSelect: 0,
      ticketTypeFix: 0,
      seatCheck: [],
      submitReady: false,
      errors: [],
      elapsed: 0
    };
    
    const startTime = performance.now();
    
    try {
      // 1. 测试弹窗关闭
      log('测试1: 弹窗关闭...', 'info');
      results.dialogClose = closeAllDialogs();
      log(`  关闭了 ${results.dialogClose} 个弹窗`, 'success');
      
      await delay(100);
      
      // 2. 测试乘客选择
      log('测试2: 乘客选择...', 'info');
      results.passengerSelect = selectPassengers();
      
      await delay(200);
      closeAllDialogs();
      
      // 3. 测试票种修改
      log('测试3: 票种修改...', 'info');
      results.ticketTypeFix = fixTicketTypes();
      
      await delay(100);
      closeAllDialogs();
      
      // 4. 检查当前状态
      log('测试4: 状态检查...', 'info');
      
      // 获取当前乘客信息
      const currentPassengers = [];
      for (let i = 1; i <= 5; i++) {
        const nameInput = document.querySelector(`input[id="passengerName_${i}"]`);
        const ticketSelect = document.getElementById(`ticketType_${i}`);
        const seatSelect = document.getElementById(`seatType_${i}`);
        
        if (nameInput && nameInput.value) {
          currentPassengers.push({
            name: nameInput.value,
            ticketType: ticketSelect?.value === '1' ? '成人票' : '儿童票',
            seatType: seatSelect?.options[seatSelect.selectedIndex]?.text
          });
        }
      }
      
      log('当前乘客状态:', 'info');
      currentPassengers.forEach((p, i) => {
        log(`  ${i+1}. ${p.name}: ${p.ticketType} - ${p.seatType}`, 'info');
      });
      
      // 5. 验证票种是否正确
      log('测试5: 验证票种配置...', 'info');
      let allCorrect = true;
      currentPassengers.forEach(p => {
        for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
          if (p.name.includes(pName)) {
            const expectedType = pConfig.ticketType === '1' ? '成人票' : '儿童票';
            if (p.ticketType !== expectedType) {
              log(`  ❌ ${pName}: 期望${expectedType}, 实际${p.ticketType}`, 'error');
              results.errors.push(`${pName}票种不正确`);
              allCorrect = false;
            } else {
              log(`  ✅ ${pName}: ${p.ticketType} 正确`, 'success');
            }
            break;
          }
        }
      });
      
      // 6. 检查提交按钮
      log('测试6: 提交按钮...', 'info');
      const submitBtn = document.getElementById('submitOrder_id');
      if (submitBtn && !submitBtn.disabled) {
        results.submitReady = true;
        log('  ✅ 提交按钮就绪', 'success');
      } else {
        log('  ❌ 提交按钮不可用', 'error');
        results.errors.push('提交按钮不可用');
      }
      
    } catch (e) {
      results.errors.push(e.message);
      log(`测试出错: ${e.message}`, 'error');
    }
    
    results.elapsed = Math.round(performance.now() - startTime);
    
    log('═══════════════════════════════════════', 'warning');
    log('  📊 测试结果汇总', 'warning');
    log('═══════════════════════════════════════', 'warning');
    log(`  页面类型: ${results.page}`, 'info');
    log(`  弹窗关闭: ${results.dialogClose}`, 'info');
    log(`  乘客选择: ${results.passengerSelect}`, 'info');
    log(`  票种修改: ${results.ticketTypeFix}`, 'info');
    log(`  提交就绪: ${results.submitReady ? '✅' : '❌'}`, results.submitReady ? 'success' : 'error');
    log(`  总耗时: ${results.elapsed}ms`, 'info');
    
    if (results.errors.length > 0) {
      log(`  ⚠️ 发现问题: ${results.errors.join(', ')}`, 'error');
    } else {
      log(`  ✅ 全部测试通过!`, 'success');
    }
    
    log('═══════════════════════════════════════', 'warning');
    
    return results;
  };

  // ═══════════════════════════════════════════════════════════════
  // ⏰ 定时抢票
  // ═══════════════════════════════════════════════════════════════
  
  const checkReleaseTime = () => {
    const now = new Date();
    const [h, m, s] = CONFIG.releaseTime.split(':').map(Number);
    const release = new Date();
    release.setHours(h, m, s, 0);
    
    const diff = (release - now) / 1000;
    
    // 提前进入高频模式
    if (diff > 0 && diff <= CONFIG.advanceSeconds && !state.isHighFreq) {
      state.isHighFreq = true;
      log(`⚡ 进入秒杀模式! ${CONFIG.highFreqInterval}ms/次`, 'speed');
      restartLoop(CONFIG.highFreqInterval);
      playSound();
    }
    
    // 放票后恢复
    if (diff < -120 && state.isHighFreq) {
      state.isHighFreq = false;
      restartLoop(CONFIG.normalInterval);
    }
    
    return diff;
  };

  const restartLoop = (interval) => {
    if (state.intervalId) clearInterval(state.intervalId);
    state.intervalId = setInterval(mainLoop, interval);
  };

  // ═══════════════════════════════════════════════════════════════
  // 🔄 主循环
  // ═══════════════════════════════════════════════════════════════
  
  const mainLoop = () => {
    if (!state.running) return;
    
    const page = detectPage();
    
    if (page === 'query') {
      checkReleaseTime();
      queryTickets();
      
      setTimeout(() => {
        const result = checkTickets();
        if (result.found) {
          state.running = false;
          log('发现票，等待跳转...', 'success');
          
          // 监听页面跳转
          const checkConfirm = setInterval(() => {
            if (detectPage() === 'confirm') {
              clearInterval(checkConfirm);
              handleConfirmPage();
            }
          }, 100);
          
          // 超时恢复
          setTimeout(() => {
            clearInterval(checkConfirm);
            if (detectPage() !== 'confirm') {
              log('跳转超时，恢复监控', 'warning');
              state.running = true;
            }
          }, 5000);
        }
      }, 500);
      
    } else if (page === 'confirm') {
      state.running = false;
      handleConfirmPage();
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // 🎮 控制接口
  // ═══════════════════════════════════════════════════════════════
  
  const start = () => {
    if (state.running) {
      log('已在运行中', 'warning');
      return;
    }
    
    state.running = true;
    state.startTime = new Date();
    
    const page = detectPage();
    
    if (page === 'confirm') {
      handleConfirmPage();
    } else {
      const interval = state.isHighFreq ? CONFIG.highFreqInterval : CONFIG.normalInterval;
      state.intervalId = setInterval(mainLoop, interval);
      log(`🚀 启动! 刷新: ${interval}ms`, 'success');
      mainLoop();
    }
  };
  
  const stop = () => {
    state.running = false;
    if (state.intervalId) {
      clearInterval(state.intervalId);
      state.intervalId = null;
    }
    if (state.dialogObserver) {
      state.dialogObserver.disconnect();
      state.dialogObserver = null;
    }
    log('⏹️ 已停止', 'warning');
  };
  
  const status = () => {
    const info = {
      running: state.running,
      page: state.currentPage,
      highFreq: state.isHighFreq,
      checkCount: state.checkCount,
      releaseTime: CONFIG.releaseTime
    };
    console.table(info);
    return info;
  };

  // ═══════════════════════════════════════════════════════════════
  // 🌐 暴露接口
  // ═══════════════════════════════════════════════════════════════
  
  window.grab = {
    // 控制
    start,
    stop,
    status,
    
    // 测试
    test: runFullTest,
    
    // 订单页面
    handleConfirm: handleConfirmPage,
    selectPassengers,
    fixTicketTypes,
    closeDialogs: closeAllDialogs,
    submit: submitOrder,
    
    // 查票
    query: queryTickets,
    check: checkTickets,
    
    // 配置
    config: CONFIG
  };

  // ═══════════════════════════════════════════════════════════════
  // 🎯 初始化
  // ═══════════════════════════════════════════════════════════════
  
  console.clear();
  console.log('%c═════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  console.log('%c  🎯 12306 极速抢票 v4.0 - 秒杀级优化', 'color:#4CAF50;font-size:16px;font-weight:bold');
  console.log('%c═════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  console.log('');
  console.log('%c📌 乘客配置:', 'color:#2196F3;font-weight:bold');
  Object.entries(CONFIG.passengers).forEach(([n, c]) => console.log(`   ${n}: ${c.typeName}`));
  console.log('');
  console.log('%c📌 命令:', 'color:#2196F3;font-weight:bold');
  console.log('   grab.start()   - 启动抢票');
  console.log('   grab.stop()    - 停止');
  console.log('   grab.test()    - 完整测试');
  console.log('   grab.handleConfirm() - 处理订单页');
  console.log('');
  console.log('%c═════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  
  // 自动检测并处理
  const page = detectPage();
  if (page === 'confirm') {
    log('检测到订单页面', 'success');
    log('输入 grab.test() 测试完整流程', 'info');
  } else {
    log('输入 grab.start() 启动抢票', 'info');
  }
  
  return '✅ 极速抢票脚本 v4.0 已加载';
})();
