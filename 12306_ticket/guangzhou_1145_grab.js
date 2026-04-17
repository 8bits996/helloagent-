/**
 * 🚄 广州11:45定时抢票脚本 - 专抢硬卧/二等座
 * 
 * 针对2月7日广州/广州北/广州白云出发
 * 目的地：邓州/襄阳
 * 放票时间：11:45
 * 乘车人：陈卓、冯巧玉、陈苇杭、陈妙可
 * 
 * 【使用方法】
 * 1. 提前打开12306查票页面
 * 2. 确保已登录账号
 * 3. 11:44:50 运行 ticketGrabber.start()
 * 4. 脚本会在11:45:00精准开始抢票
 */

const GUANGZHOU_1145_SCRIPT = `
(function() {
  'use strict';
  
  // ================ 核心配置 ================
  const CONFIG = {
    // 目标车次（11:45起售的广州出发车次）
    targetTrains: ['K932', 'K756', 'K1656', 'K536', 'K1296', 'K922', 'D192'],
    
    // 只抢这两种座位
    acceptSeats: ['硬卧', '二等座', '二等卧'],
    
    // 4位乘车人
    passengers: ['陈卓', '冯巧玉', '陈苇杭', '陈妙可'],
    
    // 放票时间
    releaseTime: '11:45:00',
    
    // 提前开始时间（秒）- 提前10秒开始高频刷新
    advanceSeconds: 10,
    
    // 抢票模式刷新间隔（毫秒）- 放票时刻极速刷新
    grabInterval: 500,
    
    // 普通监控刷新间隔
    normalInterval: 3000,
    
    // 放票后持续抢票时间（秒）
    grabDuration: 60,
    
    // 接受候补
    acceptCandidate: true,
    
    // 最大查询次数
    maxRetries: 9999,
    
    // 路线名称
    routeName: '广州→邓州/襄阳'
  };
  
  // ================ 状态变量 ================
  let isRunning = false;
  let isGrabMode = false;  // 是否在抢票模式
  let retryCount = 0;
  let timer = null;
  let startTime = null;
  let grabStartTime = null;
  
  // ================ 工具函数 ================
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    const styles = {
      info: 'color: #2196F3; font-size: 12px',
      success: 'color: #4CAF50; font-weight: bold; font-size: 14px',
      warning: 'color: #FF9800; font-size: 12px; font-weight: bold',
      error: 'color: #F44336; font-weight: bold',
      ticket: 'color: #E91E63; font-weight: bold; font-size: 20px; background: #FCE4EC; padding: 6px 16px; border-radius: 6px',
      countdown: 'color: #9C27B0; font-weight: bold; font-size: 16px',
      grab: 'color: #FF5722; font-weight: bold; font-size: 14px; background: #FFF3E0; padding: 2px 8px'
    };
    console.log('%c[' + time + '][' + CONFIG.routeName + '] ' + msg, styles[type] || styles.info);
  };
  
  const playSound = (times = 3) => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      for (let i = 0; i < times; i++) {
        setTimeout(() => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = 880;
          osc.type = 'sine';
          gain.gain.value = 0.8;
          osc.start();
          setTimeout(() => osc.stop(), 200);
        }, i * 300);
      }
    } catch(e) {}
  };
  
  const notify = (title, body) => {
    playSound(5);
    if (Notification.permission === 'granted') {
      new Notification(title, { body, requireInteraction: true, icon: '🎫' });
    }
    // 页面标题闪烁
    let flash = true;
    const orig = document.title;
    const fi = setInterval(() => {
      document.title = flash ? '🎫🎫🎫【抢到票了！】' + title : '🚄🚄🚄 ' + orig;
      flash = !flash;
    }, 300);
    setTimeout(() => { clearInterval(fi); document.title = orig; }, 120000);
    
    // 弹窗提醒
    alert('🎫 抢到票了！\\n\\n' + title + '\\n' + body + '\\n\\n请立即完成订单！');
  };
  
  // ================ 时间相关 ================
  const parseTime = (timeStr) => {
    const [h, m, s] = timeStr.split(':').map(Number);
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, s || 0);
  };
  
  const getTimeToRelease = () => {
    const now = new Date();
    const release = parseTime(CONFIG.releaseTime);
    return (release - now) / 1000; // 秒
  };
  
  const formatCountdown = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 10);
    if (m > 0) return m + '分' + s + '秒';
    return s + '.' + ms + '秒';
  };
  
  // ================ 核心功能 ================
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
          '二等卧': tds[6]?.innerText?.trim()  // D字头的二等卧
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
  
  const checkTrain = (train) => {
    // 目标车次优先（如果设置了的话）
    const isTargetTrain = CONFIG.targetTrains.length === 0 || CONFIG.targetTrains.includes(train.trainCode);
    
    if (!train.canBook && !(CONFIG.acceptCandidate && train.canCandidate)) return null;
    
    for (const seatType of CONFIG.acceptSeats) {
      if (hasSeat(train.seats[seatType])) {
        return { 
          found: true, 
          seatType, 
          count: train.seats[seatType],
          trainCode: train.trainCode,
          departTime: train.departTime,
          isTarget: isTargetTrain,
          priority: isTargetTrain ? 1 : 2
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
      train.bookBtn.click(); 
      return true; 
    }
    if (CONFIG.acceptCandidate && train.candidateBtn) { 
      train.candidateBtn.click(); 
      return true; 
    }
    return false;
  };
  
  // ================ 主循环 ================
  const mainLoop = () => {
    retryCount++;
    if (retryCount > CONFIG.maxRetries) { stop(); return; }
    
    const timeToRelease = getTimeToRelease();
    const now = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    
    // 判断是否进入抢票模式
    if (!isGrabMode && timeToRelease <= CONFIG.advanceSeconds && timeToRelease > -CONFIG.grabDuration) {
      isGrabMode = true;
      grabStartTime = Date.now();
      
      // 切换到高频刷新
      if (timer) { clearInterval(timer); }
      timer = setInterval(() => {
        if (isRunning) { clickQuery(); mainLoop(); }
      }, CONFIG.grabInterval);
      
      log('🚀🚀🚀 进入抢票模式！高频刷新启动！', 'grab');
      playSound(2);
    }
    
    // 退出抢票模式
    if (isGrabMode && timeToRelease < -CONFIG.grabDuration) {
      isGrabMode = false;
      if (timer) { clearInterval(timer); }
      timer = setInterval(() => {
        if (isRunning) { clickQuery(); mainLoop(); }
      }, CONFIG.normalInterval);
      log('抢票窗口结束，恢复普通监控', 'warning');
    }
    
    setTimeout(() => {
      const trains = getTrainList();
      let results = [];
      
      // 检查所有车次
      for (const train of trains) {
        const result = checkTrain(train);
        if (result && result.found) {
          results.push({ ...result, train });
        }
      }
      
      // 按优先级排序（目标车次优先）
      results.sort((a, b) => a.priority - b.priority);
      
      if (results.length > 0) {
        const best = results[0];
        const msg = '🎫🎫🎫 ' + best.trainCode + ' ' + best.departTime + ' 有【' + best.seatType + '】' + best.count + '张！';
        log(msg, 'ticket');
        notify('抢到票了！' + best.trainCode, CONFIG.routeName + ' ' + best.seatType + ': ' + best.count);
        
        // 立即点击预订
        clickBook(best.train);
        
        // 不停止，继续监控其他车次
        // stop();
        return;
      }
      
      // 显示状态
      if (isGrabMode) {
        const elapsed = grabStartTime ? ((Date.now() - grabStartTime) / 1000).toFixed(1) : 0;
        let status = trains.filter(t => CONFIG.targetTrains.includes(t.trainCode))
          .map(t => t.trainCode + ':' + (t.seats['硬卧'] || '-'))
          .join(' ');
        log('⚡ #' + retryCount + ' | 抢票中' + elapsed + 's | ' + (status || '等待放票...'), 'grab');
      } else if (timeToRelease > 0) {
        log('⏳ #' + retryCount + ' | 距离11:45还有 ' + formatCountdown(timeToRelease) + ' | 监控中...', 'countdown');
      } else {
        let hardBed = trains.map(t => t.trainCode + ':' + (t.seats['硬卧'] || '-')).join(' ');
        log('#' + retryCount + ' | ' + trains.length + '车次 | 硬卧[' + hardBed.substring(0, 60) + ']');
      }
    }, isGrabMode ? 200 : 800);
  };
  
  // ================ 控制函数 ================
  const start = () => {
    if (isRunning) return '已在运行';
    if (!document.getElementById('query_ticket')) return '请先打开12306查票页面';
    
    console.clear();
    const timeToRelease = getTimeToRelease();
    
    log('═══════════════════════════════════════════════════', 'success');
    log('  🚄 广州 11:45 定时抢票脚本', 'success');
    log('═══════════════════════════════════════════════════', 'success');
    log('');
    log('📋 配置信息:');
    log('   放票时间: ' + CONFIG.releaseTime);
    log('   距离放票: ' + (timeToRelease > 0 ? formatCountdown(timeToRelease) : '已过放票时间'));
    log('   目标车次: ' + CONFIG.targetTrains.join(', '));
    log('   目标座位: ' + CONFIG.acceptSeats.join(', '));
    log('   乘 车 人: ' + CONFIG.passengers.join(', ') + ' (共' + CONFIG.passengers.length + '人)');
    log('   抢票间隔: ' + CONFIG.grabInterval + 'ms（放票时刻）');
    log('');
    log('💡 命令:');
    log('   ticketGrabber.stop()     停止');
    log('   ticketGrabber.status()   查看状态');
    log('═══════════════════════════════════════════════════', 'success');
    
    isRunning = true;
    isGrabMode = false;
    retryCount = 0;
    startTime = Date.now();
    
    Notification.requestPermission();
    clickQuery();
    
    // 根据距离放票时间选择刷新间隔
    const interval = timeToRelease <= CONFIG.advanceSeconds ? CONFIG.grabInterval : CONFIG.normalInterval;
    
    timer = setInterval(() => {
      if (isRunning) { clickQuery(); mainLoop(); }
    }, interval);
    
    if (timeToRelease <= CONFIG.advanceSeconds) {
      isGrabMode = true;
      grabStartTime = Date.now();
      log('🚀 直接进入抢票模式！', 'grab');
    }
    
    return '🚀 已启动！等待11:45放票...';
  };
  
  const stop = () => {
    isRunning = false;
    isGrabMode = false;
    if (timer) { clearInterval(timer); timer = null; }
    log('⏹️ 已停止', 'warning');
    return '已停止';
  };
  
  const status = () => {
    const timeToRelease = getTimeToRelease();
    return {
      running: isRunning,
      grabMode: isGrabMode,
      queries: retryCount,
      timeToRelease: timeToRelease > 0 ? formatCountdown(timeToRelease) : '已过放票时间',
      targetTrains: CONFIG.targetTrains,
      passengers: CONFIG.passengers
    };
  };
  
  // 设置目标车次
  const setTrains = (trains) => {
    CONFIG.targetTrains = trains;
    log('目标车次已更新: ' + trains.join(', '));
  };
  
  // 暴露到全局
  window.ticketGrabber = { 
    start, 
    stop, 
    status,
    config: CONFIG, 
    getTrains: getTrainList, 
    setTrains 
  };
  
  log('✅ 广州11:45抢票脚本已加载！', 'success');
  log('📌 乘车人: ' + CONFIG.passengers.join(', '), 'warning');
  log('📌 输入 ticketGrabber.start() 开始', 'warning');
  
  return '脚本已加载，输入 ticketGrabber.start() 启动';
})();
`;

// 输出使用说明
console.log('═══════════════════════════════════════════════════════');
console.log('  🚄 广州11:45定时抢票脚本 - 使用说明');
console.log('═══════════════════════════════════════════════════════');
console.log('');
console.log('【乘车人】陈卓、冯巧玉、陈苇杭、陈妙可');
console.log('【目标车次】K932, K756, K1656, K536, K1296, K922, D192');
console.log('【放票时间】11:45:00');
console.log('');
console.log('【使用步骤】');
console.log('1. 11:40 打开12306查票页面');
console.log('2. 确保已登录账号');
console.log('3. 复制下方代码到控制台运行');
console.log('4. 输入 ticketGrabber.start() 启动');
console.log('5. 脚本会自动在11:45进入高频抢票模式');
console.log('');
console.log('═══════════════════════════════════════════════════════');
console.log('');
console.log(GUANGZHOU_1145_SCRIPT);

module.exports = { GUANGZHOU_1145_SCRIPT };
