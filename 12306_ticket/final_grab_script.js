/**
 * ═══════════════════════════════════════════════════════════════════════════
 *    🎯 12306 终极抢票脚本 v3.0 - 秒杀级优化
 * ═══════════════════════════════════════════════════════════════════════════
 * 
 * 📌 功能特点:
 *    1. 全自动抢票流程（查票→预订→选人→修改票种→提交）
 *    2. 自动处理所有弹窗（无卡顿）
 *    3. 固化乘客票种配置（避免手动修改）
 *    4. 11:45定时放票高频刷新
 *    5. 声音+视觉提醒
 * 
 * 📌 乘车人配置:
 *    - 陈卓: 成人票
 *    - 冯巧玉: 成人票
 *    - 陈苇杭: 儿童票
 *    - 陈妙可: 成人票（已满14岁）
 * 
 * 📌 使用方法:
 *    在12306查票页面的控制台(F12)中粘贴运行
 * ═══════════════════════════════════════════════════════════════════════════
 */

(function() {
  'use strict';

  // ═══════════════════════════════════════════════════════════════
  // 🔧 核心配置 - 请勿随意修改
  // ═══════════════════════════════════════════════════════════════
  
  const CONFIG = {
    // ────────── 目标车次 ──────────
    targetTrains: ['K756', 'K536', 'K1296', 'K932', 'K1656', 'K922', 'D192', 'G3830'],
    
    // ────────── 接受的席别 ──────────
    acceptSeats: {
      '硬卧': true,
      '二等座': true,
      '二等卧': true
    },
    
    // ────────── 乘车人配置（固化票种）──────────
    passengers: {
      '陈卓': { ticketType: '1', typeName: '成人票' },
      '冯巧玉': { ticketType: '1', typeName: '成人票' },
      '陈苇杭': { ticketType: '2', typeName: '儿童票' },
      '陈妙可': { ticketType: '1', typeName: '成人票' }  // 已满14岁
    },
    
    // ────────── 抢票时间配置 ──────────
    releaseTime: '11:45:00',      // 放票时间
    advanceSeconds: 5,            // 提前几秒进入高频模式
    
    // ────────── 刷新间隔(ms) ──────────
    normalInterval: 3000,         // 普通刷新间隔
    highFreqInterval: 300,        // 高频刷新间隔（放票时）
    
    // ────────── 自动化选项 ──────────
    autoClickBook: true,          // 自动点击预订
    autoSelectPassenger: true,    // 自动选择乘客
    autoFixTicketType: true,      // 自动修改票种
    autoCloseDialog: true,        // 自动关闭弹窗
    autoSubmit: false,            // 自动提交订单（建议false）
    
    // ────────── 提醒 ──────────
    soundAlert: true,             // 声音提醒
    visualAlert: true             // 视觉提醒
  };

  // ═══════════════════════════════════════════════════════════════
  // 📊 状态管理
  // ═══════════════════════════════════════════════════════════════
  
  const state = {
    running: false,
    isHighFreq: false,
    currentPage: 'unknown',     // query | confirm
    checkCount: 0,
    lastFoundTrain: null,
    intervalId: null,
    dialogWatcherId: null
  };

  // ═══════════════════════════════════════════════════════════════
  // 🛠️ 工具函数
  // ═══════════════════════════════════════════════════════════════
  
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    const prefix = {
      info: '📋',
      success: '✅',
      warning: '⚠️',
      error: '❌',
      ticket: '🎫'
    };
    const colors = {
      info: '#2196F3',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
      ticket: '#E91E63'
    };
    console.log(
      `%c[${time}] ${prefix[type] || '📋'} ${msg}`,
      `color: ${colors[type] || colors.info}; font-weight: ${type !== 'info' ? 'bold' : 'normal'}`
    );
  };

  // 播放提示音
  const playSound = () => {
    if (!CONFIG.soundAlert) return;
    try {
      const audio = new (window.AudioContext || window.webkitAudioContext)();
      [523, 659, 784, 1047].forEach((freq, i) => {
        const osc = audio.createOscillator();
        const gain = audio.createGain();
        osc.connect(gain);
        gain.connect(audio.destination);
        osc.frequency.value = freq;
        osc.type = 'sine';
        gain.gain.value = 0.3;
        osc.start(audio.currentTime + i * 0.15);
        osc.stop(audio.currentTime + i * 0.15 + 0.15);
      });
    } catch (e) {}
  };

  // 视觉提醒
  const flashScreen = () => {
    if (!CONFIG.visualAlert) return;
    const div = document.createElement('div');
    div.style.cssText = `
      position:fixed;top:0;left:0;width:100%;height:100%;
      background:rgba(76,175,80,0.3);z-index:999999;
      pointer-events:none;animation:flash 0.5s ease-out;
    `;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 500);
  };

  // ═══════════════════════════════════════════════════════════════
  // 🔍 查票页面逻辑
  // ═══════════════════════════════════════════════════════════════
  
  // 检测当前页面类型
  const detectPage = () => {
    if (location.href.includes('confirmPassenger')) {
      state.currentPage = 'confirm';
      return 'confirm';
    } else if (location.href.includes('leftTicket') || document.getElementById('query_ticket')) {
      state.currentPage = 'query';
      return 'query';
    }
    return 'unknown';
  };

  // 查询车票
  const queryTickets = () => {
    const btn = document.getElementById('query_ticket');
    if (btn) {
      btn.click();
      state.checkCount++;
      return true;
    }
    return false;
  };

  // 检查余票
  const checkTickets = () => {
    const rows = document.querySelectorAll('#queryLeftTable tr:not(.datatran)');
    
    for (const row of rows) {
      // 获取车次
      const trainEl = row.querySelector('.train .number');
      if (!trainEl) continue;
      const trainNo = trainEl.textContent.trim();
      
      // 检查是否是目标车次
      if (!CONFIG.targetTrains.includes(trainNo)) continue;
      
      // 检查席别余票
      const ywCell = row.querySelector('td:nth-child(8)');   // 硬卧
      const ezCell = row.querySelector('td:nth-child(4)');   // 二等座
      const edwCell = row.querySelector('td:nth-child(5)');  // 二等卧
      
      const checkSeat = (cell, seatName) => {
        if (!cell || !CONFIG.acceptSeats[seatName]) return false;
        const text = cell.textContent.trim();
        return text === '有' || /^\d+$/.test(text);
      };
      
      let availableSeat = null;
      if (checkSeat(ezCell, '二等座')) availableSeat = '二等座';
      else if (checkSeat(ywCell, '硬卧')) availableSeat = '硬卧';
      else if (checkSeat(edwCell, '二等卧')) availableSeat = '二等卧';
      
      if (availableSeat) {
        log(`发现有票! ${trainNo} - ${availableSeat}`, 'ticket');
        playSound();
        flashScreen();
        state.lastFoundTrain = trainNo;
        
        // 自动点击预订
        if (CONFIG.autoClickBook) {
          const bookBtn = row.querySelector('a.btn72');
          if (bookBtn) {
            log('自动点击预订...', 'success');
            bookBtn.click();
            return true;
          }
        }
      }
    }
    
    return false;
  };

  // ═══════════════════════════════════════════════════════════════
  // 📝 订单页面逻辑 - 极速版
  // ═══════════════════════════════════════════════════════════════
  
  // 自动关闭所有弹窗
  const autoCloseDialogs = () => {
    // 方式1: DHTMLX弹窗
    document.querySelectorAll('.dhtmlx_wins .btn_def, .dhtmlx_window_active .btn_def').forEach(btn => {
      if (btn.textContent.includes('确认') || btn.textContent.includes('确定') || btn.textContent.includes('知道')) {
        btn.click();
      }
    });
    
    // 方式2: 通用弹窗关闭按钮
    document.querySelectorAll('[class*="modal"] .close, [class*="dialog"] .close, .layui-layer-close').forEach(btn => {
      btn.click();
    });
    
    // 方式3: 确认类按钮
    document.querySelectorAll('.btn-primary, .confirm-btn, [onclick*="confirm"]').forEach(btn => {
      const text = btn.textContent;
      if (text.includes('确认') || text.includes('确定')) {
        btn.click();
      }
    });
  };

  // 极速选择乘客
  const selectPassengers = () => {
    const list = document.getElementById('normal_passenger_id');
    if (!list) return false;
    
    const passengerNames = Object.keys(CONFIG.passengers);
    let selected = 0;
    
    list.querySelectorAll('li').forEach(li => {
      const label = li.querySelector('label');
      const checkbox = li.querySelector('input[type="checkbox"]');
      if (!label || !checkbox) return;
      
      const name = label.textContent.trim();
      if (passengerNames.some(p => name.includes(p))) {
        if (!checkbox.checked) {
          checkbox.click();
        }
        selected++;
      }
    });
    
    log(`已选择 ${selected} 位乘车人`, 'success');
    return selected > 0;
  };

  // 极速修改票种
  const fixTicketTypes = () => {
    // 等待乘客信息表格加载
    const table = document.getElementById('ticketInfo_id');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
      const nameInput = row.querySelector('input[id^="passengerName_"]');
      const ticketSelect = row.querySelector('select[id^="ticketType_"]');
      
      if (!nameInput || !ticketSelect) return;
      
      const name = nameInput.value;
      
      // 查找匹配的乘客配置
      for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
        if (name.includes(pName)) {
          if (ticketSelect.value !== pConfig.ticketType) {
            ticketSelect.value = pConfig.ticketType;
            ticketSelect.dispatchEvent(new Event('change', { bubbles: true }));
            log(`${pName}: 票种→${pConfig.typeName}`, 'success');
          }
          break;
        }
      }
    });
  };

  // 提交订单
  const submitOrder = () => {
    const btn = document.getElementById('submitOrder_id');
    if (!btn || btn.disabled) return;
    
    if (CONFIG.autoSubmit) {
      btn.click();
      log('🚀 订单已自动提交!', 'success');
    } else {
      // 高亮提交按钮
      btn.style.cssText = `
        border: 4px solid red !important;
        box-shadow: 0 0 20px red !important;
        transform: scale(1.1);
      `;
      log('✅ 请手动点击【提交订单】', 'warning');
    }
  };

  // 订单页面极速处理
  const handleConfirmPage = async () => {
    log('═══════════════════════════════════════', 'success');
    log('  ⚡ 进入订单页面 - 极速处理中...', 'success');
    log('═══════════════════════════════════════', 'success');
    
    const fastDelay = 30; // 极短延迟
    
    // 启动弹窗监控（持续关闭弹窗）
    state.dialogWatcherId = setInterval(autoCloseDialogs, 50);
    
    // Step 1: 关闭可能存在的弹窗
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, fastDelay));
    
    // Step 2: 选择乘客
    if (CONFIG.autoSelectPassenger) {
      selectPassengers();
      await new Promise(r => setTimeout(r, fastDelay));
    }
    
    // Step 3: 再次关闭弹窗
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, fastDelay * 2));
    
    // Step 4: 修改票种
    if (CONFIG.autoFixTicketType) {
      fixTicketTypes();
      await new Promise(r => setTimeout(r, fastDelay));
    }
    
    // Step 5: 再次关闭弹窗（票种修改可能触发）
    autoCloseDialogs();
    await new Promise(r => setTimeout(r, fastDelay));
    
    // Step 6: 准备提交
    submitOrder();
    
    // 5秒后停止弹窗监控
    setTimeout(() => {
      if (state.dialogWatcherId) {
        clearInterval(state.dialogWatcherId);
        state.dialogWatcherId = null;
      }
    }, 5000);
    
    log('═══════════════════════════════════════', 'success');
    log('  ✅ 订单页面处理完成!', 'success');
    log('═══════════════════════════════════════', 'success');
  };

  // ═══════════════════════════════════════════════════════════════
  // ⏰ 定时抢票逻辑
  // ═══════════════════════════════════════════════════════════════
  
  // 检查是否到放票时间
  const checkReleaseTime = () => {
    const now = new Date();
    const [h, m, s] = CONFIG.releaseTime.split(':').map(Number);
    const releaseTime = new Date();
    releaseTime.setHours(h, m, s, 0);
    
    const diff = (releaseTime - now) / 1000;
    
    // 提前进入高频模式
    if (diff > 0 && diff <= CONFIG.advanceSeconds && !state.isHighFreq) {
      state.isHighFreq = true;
      log(`⚡ 进入高频抢票模式! ${CONFIG.highFreqInterval}ms/次`, 'warning');
      restartLoop(CONFIG.highFreqInterval);
    }
    
    // 放票后一段时间恢复正常
    if (diff < -60 && state.isHighFreq) {
      state.isHighFreq = false;
      log('恢复正常刷新频率', 'info');
      restartLoop(CONFIG.normalInterval);
    }
    
    return diff;
  };

  // 重启循环
  const restartLoop = (interval) => {
    if (state.intervalId) {
      clearInterval(state.intervalId);
    }
    state.intervalId = setInterval(mainLoop, interval);
  };

  // ═══════════════════════════════════════════════════════════════
  // 🔄 主循环
  // ═══════════════════════════════════════════════════════════════
  
  const mainLoop = () => {
    if (!state.running) return;
    
    const page = detectPage();
    
    if (page === 'query') {
      // 查票页面
      checkReleaseTime();
      queryTickets();
      
      // 等待查询结果
      setTimeout(() => {
        if (checkTickets()) {
          // 发现票了，暂停循环等待页面跳转
          state.running = false;
          log('发现票，等待跳转订单页面...', 'success');
          
          // 监听页面变化
          setTimeout(() => {
            if (detectPage() === 'confirm') {
              handleConfirmPage();
            } else {
              // 可能跳转失败，恢复监控
              state.running = true;
            }
          }, 2000);
        }
      }, 800);
      
    } else if (page === 'confirm') {
      // 订单确认页面
      state.running = false;
      handleConfirmPage();
    }
  };

  // ═══════════════════════════════════════════════════════════════
  // 🎮 控制接口
  // ═══════════════════════════════════════════════════════════════
  
  const start = () => {
    if (state.running) {
      log('脚本已在运行中', 'warning');
      return;
    }
    
    state.running = true;
    const page = detectPage();
    
    if (page === 'confirm') {
      // 已在订单页面，直接处理
      handleConfirmPage();
    } else {
      // 在查票页面，启动监控
      const interval = state.isHighFreq ? CONFIG.highFreqInterval : CONFIG.normalInterval;
      state.intervalId = setInterval(mainLoop, interval);
      log(`🚀 抢票脚本启动! 刷新间隔: ${interval}ms`, 'success');
      mainLoop();
    }
  };
  
  const stop = () => {
    state.running = false;
    if (state.intervalId) {
      clearInterval(state.intervalId);
      state.intervalId = null;
    }
    if (state.dialogWatcherId) {
      clearInterval(state.dialogWatcherId);
      state.dialogWatcherId = null;
    }
    log('⏹️ 抢票脚本已停止', 'warning');
  };
  
  const status = () => {
    console.log('═══════════════════════════════════════');
    console.log('  📊 抢票脚本状态');
    console.log('═══════════════════════════════════════');
    console.log(`  运行状态: ${state.running ? '✅ 运行中' : '⏹️ 已停止'}`);
    console.log(`  当前页面: ${state.currentPage}`);
    console.log(`  高频模式: ${state.isHighFreq ? '⚡ 是' : '否'}`);
    console.log(`  查票次数: ${state.checkCount}`);
    console.log(`  放票时间: ${CONFIG.releaseTime}`);
    console.log('═══════════════════════════════════════');
    return state;
  };

  // ═══════════════════════════════════════════════════════════════
  // 🌐 暴露全局接口
  // ═══════════════════════════════════════════════════════════════
  
  window.grab = {
    start,
    stop,
    status,
    config: CONFIG,
    
    // 单独功能
    query: queryTickets,
    check: checkTickets,
    selectPassengers,
    fixTicketTypes,
    closeDialogs: autoCloseDialogs,
    submit: submitOrder,
    handleConfirm: handleConfirmPage
  };

  // ═══════════════════════════════════════════════════════════════
  // 🎯 自动启动
  // ═══════════════════════════════════════════════════════════════
  
  console.clear();
  console.log('%c═══════════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  console.log('%c  🎯 12306 终极抢票脚本 v3.0 - 秒杀级优化', 'color:#4CAF50;font-size:16px;font-weight:bold');
  console.log('%c═══════════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  console.log('');
  console.log('%c📌 乘车人配置:', 'color:#2196F3;font-weight:bold');
  Object.entries(CONFIG.passengers).forEach(([name, cfg]) => {
    console.log(`   ${name}: ${cfg.typeName}`);
  });
  console.log('');
  console.log('%c📌 控制命令:', 'color:#2196F3;font-weight:bold');
  console.log('   grab.start()   - 启动抢票');
  console.log('   grab.stop()    - 停止抢票');
  console.log('   grab.status()  - 查看状态');
  console.log('');
  console.log('%c📌 单独功能:', 'color:#2196F3;font-weight:bold');
  console.log('   grab.handleConfirm() - 处理订单页面');
  console.log('   grab.fixTicketTypes() - 修改票种');
  console.log('   grab.closeDialogs()  - 关闭弹窗');
  console.log('');
  console.log('%c═══════════════════════════════════════════════════════════', 'color:#4CAF50;font-weight:bold');
  
  // 检测页面类型并自动处理
  const page = detectPage();
  if (page === 'confirm') {
    log('检测到订单页面，自动处理...', 'success');
    handleConfirmPage();
  } else {
    log('输入 grab.start() 启动抢票', 'info');
  }
  
  return '✅ 终极抢票脚本已加载';
})();
