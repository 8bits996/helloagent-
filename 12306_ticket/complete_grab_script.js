/**
 * ═══════════════════════════════════════════════════════════════
 *  🚄 12306 完整抢票脚本 - 广州11:45放票专用
 * ═══════════════════════════════════════════════════════════════
 * 
 * 📅 出行日期: 2026-02-07 (春节)
 * 🚉 出发地: 广州/广州南/广州北/广州白云
 * 🏁 目的地: 邓州/襄阳
 * 🎫 座位类型: 硬卧、二等座
 * 👨‍👩‍👧‍👦 乘车人: 陈卓、冯巧玉、陈苇杭、陈妙可 (4人)
 * ⏰ 放票时间: 11:45:00
 * 
 * 【重要提示】
 * - 11:44:50 启动脚本，脚本会在11:44:50自动进入高频刷新模式
 * - 抢到票后会自动点击预订并发出声音+弹窗提醒
 * - 进入订单页面后需手动确认乘客信息并提交
 * 
 * 【使用步骤】
 * 1. 11:40 打开12306查票页面（广州→邓州 或 广州→襄阳）
 * 2. 确保已登录账号
 * 3. 按F12打开控制台
 * 4. 复制整个脚本粘贴运行
 * 5. 脚本自动启动，等待11:45放票
 * 
 * ═══════════════════════════════════════════════════════════════
 */

// ========== 复制以下代码到12306控制台运行 ==========

const COMPLETE_SCRIPT = `
(function() {
  'use strict';
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     核心配置区域                          ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const CONFIG = {
    // ========== 目标车次 ==========
    // 11:45起售的广州出发K字头列车
    targetTrains: [
      'K756',   // 广州白云→邓州 15:15
      'K536',   // 广州北→邓州 18:16
      'K1296',  // 广州白云→邓州 18:20
      'K932',   // 广州北→襄阳 13:32
      'K1656',  // 广州北→襄阳 15:22
      'K922',   // 广州北→襄阳 19:50
      'D192'    // 广州白云→襄阳 20:50
    ],
    
    // ========== 座位类型 ==========
    // 只抢这些座位
    acceptSeats: ['硬卧', '二等座', '二等卧'],
    
    // ========== 乘车人 ==========
    passengers: ['陈卓', '冯巧玉', '陈苇杭', '陈妙可'],
    passengerCount: 4,
    
    // ========== 放票时间 ==========
    releaseTime: '11:45:00',
    
    // ========== 抢票参数 ==========
    advanceSeconds: 10,      // 提前多少秒进入高频模式
    grabInterval: 400,       // 放票时刷新间隔（毫秒）- 越小越快
    normalInterval: 3000,    // 普通监控间隔
    grabDuration: 120,       // 放票后持续抢票时间（秒）
    
    // ========== 其他设置 ==========
    acceptCandidate: true,   // 接受候补
    maxRetries: 99999,       // 最大查询次数
    routeName: '广州→邓州/襄阳'
  };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     状态变量                              ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  let isRunning = false;
  let isGrabMode = false;
  let retryCount = 0;
  let timer = null;
  let startTime = null;
  let grabStartTime = null;
  let ticketFound = false;
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     工具函数                              ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const ms = String(new Date().getMilliseconds()).padStart(3, '0');
    const styles = {
      info: 'color: #2196F3; font-size: 11px',
      success: 'color: #4CAF50; font-weight: bold; font-size: 14px',
      warning: 'color: #FF9800; font-weight: bold; font-size: 12px',
      error: 'color: #F44336; font-weight: bold',
      countdown: 'color: #9C27B0; font-weight: bold; font-size: 16px',
      grab: 'color: #FF5722; font-weight: bold; font-size: 13px; background: #FFF3E0; padding: 2px 8px',
      ticket: 'color: #FFFFFF; font-weight: bold; font-size: 24px; background: #E91E63; padding: 10px 20px; border-radius: 8px'
    };
    console.log('%c[' + time + '.' + ms + '] ' + msg, styles[type] || styles.info);
  };
  
  const playAlarm = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      // 播放紧急警报声
      for (let i = 0; i < 10; i++) {
        setTimeout(() => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = i % 2 === 0 ? 880 : 660;
          osc.type = 'square';
          gain.gain.value = 0.9;
          osc.start();
          setTimeout(() => osc.stop(), 150);
        }, i * 200);
      }
    } catch(e) {}
  };
  
  const notify = (title, body) => {
    playAlarm();
    
    // 浏览器通知
    if (Notification.permission === 'granted') {
      new Notification('🎫🎫🎫 ' + title, { body, requireInteraction: true });
    }
    
    // 页面标题闪烁
    let flash = true;
    const orig = document.title;
    const fi = setInterval(() => {
      document.title = flash ? '🎫🎫🎫【有票！有票！有票！】' : '🚄🚄🚄【快去付款！】';
      flash = !flash;
    }, 250);
    setTimeout(() => { clearInterval(fi); document.title = orig; }, 180000);
    
    // 弹窗提醒
    setTimeout(() => {
      alert('🎫🎫🎫 抢到票了！！！\\n\\n' + title + '\\n' + body + '\\n\\n⚠️ 请立即完成订单付款！\\n\\n乘车人: ' + CONFIG.passengers.join(', '));
    }, 500);
  };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     时间函数                              ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const parseTime = (timeStr) => {
    const [h, m, s] = timeStr.split(':').map(Number);
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, s || 0);
  };
  
  const getTimeToRelease = () => {
    return (parseTime(CONFIG.releaseTime) - new Date()) / 1000;
  };
  
  const formatCountdown = (seconds) => {
    if (seconds <= 0) return '已放票';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    if (m > 0) return m + '分' + s + '秒';
    if (seconds < 10) return seconds.toFixed(1) + '秒';
    return s + '秒';
  };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     核心抢票逻辑                          ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const getTrainList = () => {
    const trains = [];
    document.querySelectorAll('#queryLeftTable tr[id]').forEach(row => {
      try {
        const trainCode = row.querySelector('.number')?.textContent?.trim();
        if (!trainCode) return;
        
        const departTime = row.querySelector('.start-t')?.textContent?.trim() || '';
        const tds = row.querySelectorAll('td');
        
        const seats = {
          '商务座': tds[1]?.innerText?.trim(),
          '一等座': tds[2]?.innerText?.trim(),
          '二等座': tds[3]?.innerText?.trim(),
          '高级软卧': tds[4]?.innerText?.trim(),
          '软卧': tds[5]?.innerText?.trim(),
          '动卧': tds[6]?.innerText?.trim(),
          '硬卧': tds[7]?.innerText?.trim(),
          '软座': tds[8]?.innerText?.trim(),
          '硬座': tds[9]?.innerText?.trim(),
          '无座': tds[10]?.innerText?.trim(),
          '二等卧': tds[6]?.innerText?.trim()
        };
        
        const bookBtn = row.querySelector('a.btn72:not(.btn-disabled)');
        const canBook = !!bookBtn;
        const candidateBtn = row.querySelector('a.btn-hb');
        const canCandidate = !!candidateBtn;
        
        trains.push({ trainCode, departTime, seats, canBook, canCandidate, bookBtn, candidateBtn, row });
      } catch(e) {}
    });
    return trains;
  };
  
  const hasSeat = (v) => {
    if (!v || v === '' || v === '--' || v === '无' || v === '*') return false;
    return v === '有' || /^\\d+$/.test(v);
  };
  
  const getSeatCount = (v) => {
    if (v === '有') return 99;
    if (/^\\d+$/.test(v)) return parseInt(v);
    return 0;
  };
  
  const checkTrain = (train) => {
    const isTarget = CONFIG.targetTrains.length === 0 || CONFIG.targetTrains.includes(train.trainCode);
    
    if (!train.canBook && !(CONFIG.acceptCandidate && train.canCandidate)) return null;
    
    for (const seatType of CONFIG.acceptSeats) {
      if (hasSeat(train.seats[seatType])) {
        const count = getSeatCount(train.seats[seatType]);
        // 优先选择票数>=乘客数的车次
        return { 
          found: true, 
          seatType, 
          count: train.seats[seatType],
          numCount: count,
          trainCode: train.trainCode,
          departTime: train.departTime,
          isTarget,
          priority: isTarget ? (count >= CONFIG.passengerCount ? 0 : 1) : 2
        };
      }
    }
    return null;
  };
  
  const clickQuery = () => {
    const btn = document.getElementById('query_ticket');
    if (btn) { btn.click(); return true; }
    return false;
  };
  
  const clickBook = (train) => {
    if (train.bookBtn) { 
      train.row.style.backgroundColor = '#FFEB3B';
      train.bookBtn.style.transform = 'scale(1.2)';
      setTimeout(() => train.bookBtn.click(), 50);
      return 'book'; 
    }
    if (CONFIG.acceptCandidate && train.candidateBtn) { 
      train.row.style.backgroundColor = '#FFF3E0';
      setTimeout(() => train.candidateBtn.click(), 50);
      return 'candidate'; 
    }
    return null;
  };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     主循环                                ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const mainLoop = () => {
    if (ticketFound) return;
    
    retryCount++;
    if (retryCount > CONFIG.maxRetries) { stop(); return; }
    
    const timeToRelease = getTimeToRelease();
    
    // 进入抢票模式
    if (!isGrabMode && timeToRelease <= CONFIG.advanceSeconds && timeToRelease > -CONFIG.grabDuration) {
      isGrabMode = true;
      grabStartTime = Date.now();
      
      if (timer) clearInterval(timer);
      timer = setInterval(() => {
        if (isRunning && !ticketFound) { clickQuery(); mainLoop(); }
      }, CONFIG.grabInterval);
      
      log('', 'success');
      log('🚀🚀🚀🚀🚀 进入高频抢票模式！！！🚀🚀🚀🚀🚀', 'grab');
      log('', 'success');
      playAlarm();
    }
    
    // 退出抢票模式
    if (isGrabMode && timeToRelease < -CONFIG.grabDuration) {
      isGrabMode = false;
      if (timer) clearInterval(timer);
      timer = setInterval(() => {
        if (isRunning && !ticketFound) { clickQuery(); mainLoop(); }
      }, CONFIG.normalInterval);
      log('⏹️ 抢票窗口结束，恢复普通监控', 'warning');
    }
    
    // 检查车票
    setTimeout(() => {
      if (ticketFound) return;
      
      const trains = getTrainList();
      let results = [];
      
      for (const train of trains) {
        const result = checkTrain(train);
        if (result && result.found) {
          results.push({ ...result, train });
        }
      }
      
      // 按优先级排序
      results.sort((a, b) => a.priority - b.priority);
      
      if (results.length > 0) {
        ticketFound = true;
        const best = results[0];
        
        log('', 'ticket');
        log('🎫🎫🎫 发现车票！' + best.trainCode + ' ' + best.departTime + ' 【' + best.seatType + '】' + best.count + '张 🎫🎫🎫', 'ticket');
        log('', 'ticket');
        
        notify('抢到票了！' + best.trainCode, best.seatType + ': ' + best.count + '\\n' + CONFIG.routeName);
        
        // 点击预订
        const action = clickBook(best.train);
        if (action === 'book') {
          log('✅ 已点击【预订】按钮，请完成订单！', 'success');
        } else if (action === 'candidate') {
          log('✅ 已点击【候补】按钮，请完成候补！', 'warning');
        }
        
        return;
      }
      
      // 显示状态
      if (isGrabMode) {
        const elapsed = grabStartTime ? ((Date.now() - grabStartTime) / 1000).toFixed(1) : 0;
        const targetStatus = trains
          .filter(t => CONFIG.targetTrains.includes(t.trainCode))
          .map(t => t.trainCode + ':' + (t.seats['硬卧'] || '-'))
          .join(' | ');
        log('⚡ #' + retryCount + ' | 抢票中 ' + elapsed + 's | ' + (targetStatus || '等待数据...'), 'grab');
      } else if (timeToRelease > 0) {
        if (retryCount % 5 === 0) {
          log('⏳ 距离11:45放票还有 【' + formatCountdown(timeToRelease) + '】 | 已查询' + retryCount + '次', 'countdown');
        }
      } else {
        const hardBed = trains.map(t => t.trainCode + ':' + (t.seats['硬卧'] || '-')).join(' ');
        log('#' + retryCount + ' | ' + trains.length + '车次 | ' + hardBed.substring(0, 80));
      }
      
    }, isGrabMode ? 100 : 600);
  };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     控制函数                              ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  const start = () => {
    if (isRunning) return '⚠️ 已在运行中';
    if (!document.getElementById('query_ticket')) return '❌ 请先打开12306查票页面';
    
    console.clear();
    const timeToRelease = getTimeToRelease();
    
    log('');
    log('╔═══════════════════════════════════════════════════════════════╗', 'success');
    log('║                                                               ║', 'success');
    log('║      🚄 12306 完整抢票脚本 - 广州11:45放票专用                ║', 'success');
    log('║                                                               ║', 'success');
    log('╚═══════════════════════════════════════════════════════════════╝', 'success');
    log('');
    log('📅 日期: 2026-02-07 (除夕前)');
    log('🚉 路线: ' + CONFIG.routeName);
    log('⏰ 放票: ' + CONFIG.releaseTime + ' (' + (timeToRelease > 0 ? '还有' + formatCountdown(timeToRelease) : '已过') + ')');
    log('🎫 座位: ' + CONFIG.acceptSeats.join(', '));
    log('🚆 车次: ' + CONFIG.targetTrains.join(', '));
    log('');
    log('👨‍👩‍👧‍👦 乘车人 (' + CONFIG.passengerCount + '人):', 'warning');
    CONFIG.passengers.forEach((p, i) => log('   ' + (i+1) + '. ' + p));
    log('');
    log('⚡ 抢票间隔: ' + CONFIG.grabInterval + 'ms（放票时刻）', 'info');
    log('');
    log('💡 命令:', 'info');
    log('   ticketGrabber.stop()   - 停止脚本');
    log('   ticketGrabber.status() - 查看状态');
    log('');
    log('═══════════════════════════════════════════════════════════════', 'success');
    log('');
    
    isRunning = true;
    isGrabMode = false;
    ticketFound = false;
    retryCount = 0;
    startTime = Date.now();
    
    Notification.requestPermission();
    clickQuery();
    
    // 根据距离放票时间选择刷新间隔
    if (timeToRelease <= CONFIG.advanceSeconds) {
      isGrabMode = true;
      grabStartTime = Date.now();
      timer = setInterval(() => {
        if (isRunning && !ticketFound) { clickQuery(); mainLoop(); }
      }, CONFIG.grabInterval);
      log('🚀 直接进入高频抢票模式！', 'grab');
    } else {
      timer = setInterval(() => {
        if (isRunning && !ticketFound) { clickQuery(); mainLoop(); }
      }, CONFIG.normalInterval);
      log('⏳ 等待11:45放票...', 'countdown');
    }
    
    return '🚀 已启动！乘车人: ' + CONFIG.passengers.join(', ');
  };
  
  const stop = () => {
    isRunning = false;
    isGrabMode = false;
    if (timer) { clearInterval(timer); timer = null; }
    log('');
    log('⏹️ 脚本已停止', 'warning');
    log('   查询次数: ' + retryCount);
    log('');
    return '已停止';
  };
  
  const status = () => {
    const timeToRelease = getTimeToRelease();
    return {
      running: isRunning,
      grabMode: isGrabMode,
      queries: retryCount,
      ticketFound: ticketFound,
      timeToRelease: timeToRelease > 0 ? formatCountdown(timeToRelease) : '已放票',
      passengers: CONFIG.passengers,
      targetTrains: CONFIG.targetTrains
    };
  };
  
  // 暴露到全局
  window.ticketGrabber = { start, stop, status, config: CONFIG, getTrains: getTrainList };
  
  // ╔═══════════════════════════════════════════════════════════╗
  // ║                     自动启动                              ║
  // ╚═══════════════════════════════════════════════════════════╝
  
  log('');
  log('✅ 脚本已加载完成！', 'success');
  log('');
  log('👨‍👩‍👧‍👦 乘车人: ' + CONFIG.passengers.join(', '), 'warning');
  log('');
  log('📌 输入 ticketGrabber.start() 启动抢票', 'warning');
  log('');
  
  return '脚本已加载，输入 ticketGrabber.start() 启动';
})();
`;

// 导出
console.log('═══════════════════════════════════════════════════════════════════');
console.log('');
console.log('  🚄 12306 完整抢票脚本 - 广州11:45放票专用');
console.log('');
console.log('═══════════════════════════════════════════════════════════════════');
console.log('');
console.log('【乘车人】陈卓、冯巧玉、陈苇杭、陈妙可 (4人)');
console.log('【目标车次】K756, K536, K1296, K932, K1656, K922, D192');
console.log('【放票时间】11:45:00');
console.log('【目标座位】硬卧、二等座');
console.log('');
console.log('【使用步骤】');
console.log('1. 11:40 打开12306 广州→邓州/襄阳 查票页面');
console.log('2. 确保已登录账号');
console.log('3. F12打开控制台');
console.log('4. 复制下方代码粘贴运行');
console.log('5. 输入 ticketGrabber.start() 启动');
console.log('');
console.log('═══════════════════════════════════════════════════════════════════');
console.log('');
console.log(COMPLETE_SCRIPT);

module.exports = { COMPLETE_SCRIPT };
