/**
 * 12306 专用抢票脚本 - 只抢硬卧/二等座
 * 
 * 出发地：深圳/东莞/广州
 * 目的地：邓州/襄阳
 * 日期：2026-02-07
 * 座位：仅硬卧、二等座
 * 
 * 使用方法：
 * 1. 打开 12306 车票查询页面
 * 2. 按 F12 打开控制台
 * 3. 复制下方代码粘贴运行
 * 4. 输入 ticketGrabber.start() 开始
 */

const OPTIMIZED_SCRIPT = `
(function() {
  'use strict';
  
  // ============ 配置：只抢硬卧和二等座 ============
  const CONFIG = {
    // 目标车次（留空表示任意车次）
    targetTrains: [],
    
    // 【核心】只接受这两种座位
    acceptSeats: ['二等座', '硬卧'],
    
    // 刷新间隔（毫秒）
    refreshInterval: 3000,
    
    // 乘车人
    passengers: ['陈卓'],
    
    // 接受候补
    acceptCandidate: true,
    
    // 时间范围（不要太早太晚的车）
    timeRange: { start: '06:00', end: '23:59' },
    
    // 最大查询次数
    maxRetries: 9999
  };
  
  // ============ 状态变量 ============
  let isRunning = false;
  let retryCount = 0;
  let timer = null;
  let startTime = null;
  
  // ============ 工具函数 ============
  const log = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('zh-CN');
    const styles = {
      info: 'color: #2196F3; font-size: 12px',
      success: 'color: #4CAF50; font-weight: bold; font-size: 14px',
      warning: 'color: #FF9800; font-size: 12px',
      error: 'color: #F44336; font-weight: bold',
      ticket: 'color: #E91E63; font-weight: bold; font-size: 18px; background: #FCE4EC; padding: 4px 12px; border-radius: 4px'
    };
    console.log('%c[' + time + '] ' + msg, styles[type] || styles.info);
  };
  
  const playSound = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      // 播放3声提示音
      [0, 300, 600].forEach(delay => {
        setTimeout(() => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.frequency.value = 880;
          osc.type = 'sine';
          gain.gain.value = 0.6;
          osc.start();
          setTimeout(() => osc.stop(), 150);
        }, delay);
      });
    } catch(e) {}
  };
  
  const notify = (title, body) => {
    playSound();
    if (Notification.permission === 'granted') {
      new Notification(title, { body, requireInteraction: true });
    }
    // 页面标题闪烁
    let flash = true;
    const originalTitle = document.title;
    const flashInterval = setInterval(() => {
      document.title = flash ? '🎫【有票！】' + title : '🚄 ' + originalTitle;
      flash = !flash;
    }, 400);
    setTimeout(() => {
      clearInterval(flashInterval);
      document.title = originalTitle;
    }, 60000);
  };
  
  // ============ 核心功能 ============
  
  // 获取车次列表并检查座位
  const getTrainList = () => {
    const trains = [];
    const rows = document.querySelectorAll('#queryLeftTable tr[id]');
    
    rows.forEach(row => {
      try {
        const trainCode = row.querySelector('.number')?.textContent?.trim();
        if (!trainCode) return;
        
        const departTime = row.querySelector('.start-t')?.textContent?.trim() || '';
        const arriveTime = row.querySelector('.arrive-t')?.textContent?.trim() || '';
        
        // 获取座位信息 - 12306表格列索引
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
          '无座': tds[10]?.innerText?.trim()
        };
        
        // 预订按钮
        const bookBtn = row.querySelector('a.btn72:not(.btn-disabled)');
        const canBook = !!bookBtn;
        
        // 候补按钮
        const candidateBtn = row.querySelector('a.btn-hb');
        const canCandidate = !!candidateBtn;
        
        trains.push({
          trainCode,
          departTime,
          arriveTime,
          seats,
          canBook,
          canCandidate,
          bookBtn,
          candidateBtn,
          row
        });
      } catch(e) {}
    });
    
    return trains;
  };
  
  // 检查座位是否有票
  const hasSeat = (value) => {
    if (!value || value === '' || value === '--' || value === '无' || value === '*') return false;
    if (value === '有' || /^\\d+$/.test(value)) return true;
    return false;
  };
  
  // 检查车次是否符合条件（只检查硬卧和二等座）
  const checkTrain = (train) => {
    // 时间检查
    if (CONFIG.timeRange.start && train.departTime < CONFIG.timeRange.start) return null;
    if (CONFIG.timeRange.end && train.departTime > CONFIG.timeRange.end) return null;
    
    // 目标车次检查
    if (CONFIG.targetTrains.length > 0 && !CONFIG.targetTrains.includes(train.trainCode)) return null;
    
    // 必须可预订或可候补
    if (!train.canBook && !(CONFIG.acceptCandidate && train.canCandidate)) return null;
    
    // 【核心】只检查二等座和硬卧
    for (const seatType of CONFIG.acceptSeats) {
      if (hasSeat(train.seats[seatType])) {
        return { 
          found: true, 
          seatType, 
          count: train.seats[seatType],
          trainCode: train.trainCode,
          departTime: train.departTime
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
    if (train.bookBtn) { train.bookBtn.click(); return true; }
    if (CONFIG.acceptCandidate && train.candidateBtn) { train.candidateBtn.click(); return true; }
    return false;
  };
  
  const getStats = () => {
    const elapsed = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
    return {
      queries: retryCount,
      time: Math.floor(elapsed/60) + '分' + (elapsed%60) + '秒',
      rate: elapsed > 0 ? (retryCount / elapsed * 60).toFixed(1) + '次/分' : '-'
    };
  };
  
  // 主循环
  const mainLoop = () => {
    retryCount++;
    if (retryCount > CONFIG.maxRetries) { stop(); return; }
    
    const stats = getStats();
    
    setTimeout(() => {
      const trains = getTrainList();
      let found = null;
      
      // 检查每个车次
      for (const train of trains) {
        const result = checkTrain(train);
        if (result && result.found) {
          found = { ...result, train };
          break;
        }
      }
      
      if (found) {
        // 🎉 找到票了
        const msg = '🎫 ' + found.trainCode + ' ' + found.departTime + ' 有 ' + found.seatType + '（' + found.count + '）';
        log(msg, 'ticket');
        notify('有票！' + found.trainCode, found.seatType + ': ' + found.count);
        stop();
        clickBook(found.train);
        return;
      }
      
      // 统计当前座位情况
      let secondSeatStatus = [];
      let hardBedStatus = [];
      
      trains.forEach(t => {
        if (t.seats['二等座'] && t.seats['二等座'] !== '--') {
          secondSeatStatus.push(t.trainCode + ':' + t.seats['二等座']);
        }
        if (t.seats['硬卧'] && t.seats['硬卧'] !== '--') {
          hardBedStatus.push(t.trainCode + ':' + t.seats['硬卧']);
        }
      });
      
      log('#' + retryCount + ' | ' + stats.time + ' | ' + trains.length + '车次 | 二等座[' + (secondSeatStatus.join(',') || '无') + '] | 硬卧[' + (hardBedStatus.join(',') || '无') + ']');
      
    }, 1200);
  };
  
  const start = () => {
    if (isRunning) return '已在运行';
    if (!document.getElementById('query_ticket')) return '请先打开12306查票页面';
    
    console.clear();
    log('══════════════════════════════════════════', 'success');
    log('  🚄 12306 抢票脚本 - 专抢硬卧/二等座', 'success');
    log('══════════════════════════════════════════', 'success');
    log('');
    log('📋 配置信息:');
    log('   目标座位: ' + CONFIG.acceptSeats.join(', '));
    log('   乘 车 人: ' + CONFIG.passengers.join(', '));
    log('   刷新间隔: ' + CONFIG.refreshInterval + 'ms');
    log('   接受候补: ' + (CONFIG.acceptCandidate ? '是' : '否'));
    log('');
    log('💡 使用 ticketGrabber.stop() 停止');
    log('══════════════════════════════════════════', 'success');
    
    isRunning = true;
    retryCount = 0;
    startTime = Date.now();
    
    Notification.requestPermission();
    clickQuery();
    
    timer = setInterval(() => {
      if (isRunning) { clickQuery(); mainLoop(); }
    }, CONFIG.refreshInterval);
    
    return '🚀 开始抢票！只抢硬卧和二等座';
  };
  
  const stop = () => {
    isRunning = false;
    if (timer) { clearInterval(timer); timer = null; }
    const stats = getStats();
    log('══════════════════════════════════════════', 'warning');
    log('⏹️  已停止 | 查询' + stats.queries + '次 | 用时' + stats.time, 'warning');
    log('══════════════════════════════════════════', 'warning');
    return '已停止';
  };
  
  // 设置配置
  const setTrains = (trains) => {
    CONFIG.targetTrains = trains;
    log('目标车次已更新: ' + trains.join(', '));
  };
  
  window.ticketGrabber = { start, stop, config: CONFIG, getTrains: getTrainList, stats: getStats, setTrains };
  
  log('✅ 脚本已加载！输入 ticketGrabber.start() 开始', 'success');
})();
`;

console.log('======================================================');
console.log('  12306 专用抢票脚本 - 只抢硬卧/二等座');
console.log('======================================================');
console.log('');
console.log('【复制以下代码到12306页面控制台运行】');
console.log('');
console.log(OPTIMIZED_SCRIPT);
console.log('');
console.log('======================================================');

module.exports = { OPTIMIZED_SCRIPT };
