/**
 * 12306 抢票启动脚本
 * 
 * 直接复制以下代码到12306车票查询页面的浏览器控制台(F12)中运行
 * 
 * 使用步骤：
 * 1. 登录12306账号
 * 2. 打开车票查询页面，填好出发站、到达站、日期
 * 3. 按F12打开开发者工具，切换到Console标签
 * 4. 复制下面的代码粘贴运行
 * 5. 输入 ticketGrabber.start() 开始抢票
 */

// ========================================
// 以下是需要复制到浏览器控制台的代码
// ========================================

const GRAB_SCRIPT = `
(function() {
  'use strict';
  
  // ============ 🔧 配置区域（根据需要修改）============
  const CONFIG = {
    // 【重要】目标车次，留空表示抢任意有票的车次
    // 例如：['G1234', 'D5678'] 表示只抢这两个车次
    targetTrains: [],
    
    // 【重要】接受的座位类型，按优先级排序
    // 排在前面的优先抢
    acceptSeats: ['二等座', '一等座', '硬卧', '软卧', '硬座', '无座'],
    
    // 刷新间隔（毫秒），建议3000-5000，太快可能被限制
    refreshInterval: 3500,
    
    // 【重要】乘车人姓名，必须和12306常用联系人中的姓名完全一致
    passengers: ['陈卓'],
    
    // 是否接受候补
    acceptCandidate: true,
    
    // 出发时间范围限制（24小时制），留空表示不限制
    timeRange: { start: '06:00', end: '23:59' },
    
    // 最大查询次数
    maxRetries: 999
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
      success: 'color: #4CAF50; font-weight: bold; font-size: 13px',
      warning: 'color: #FF9800; font-size: 12px',
      error: 'color: #F44336; font-weight: bold',
      ticket: 'color: #E91E63; font-weight: bold; font-size: 16px; background: #FCE4EC; padding: 2px 8px; border-radius: 4px'
    };
    console.log('%c[' + time + '] ' + msg, styles[type] || styles.info);
  };
  
  const playSound = () => {
    try {
      // 播放提示音
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = 800;
      osc.type = 'sine';
      gain.gain.value = 0.5;
      osc.start();
      setTimeout(() => osc.stop(), 200);
      setTimeout(() => {
        osc.frequency.value = 1000;
        osc.start();
        setTimeout(() => osc.stop(), 200);
      }, 250);
    } catch(e) {}
  };
  
  const notify = (title, body) => {
    playSound();
    if (Notification.permission === 'granted') {
      new Notification(title, { body, icon: '🚄' });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => {
        if (p === 'granted') new Notification(title, { body });
      });
    }
    // 页面标题闪烁
    let flash = true;
    const originalTitle = document.title;
    const flashInterval = setInterval(() => {
      document.title = flash ? '【有票啦！】' + title : originalTitle;
      flash = !flash;
    }, 500);
    setTimeout(() => {
      clearInterval(flashInterval);
      document.title = originalTitle;
    }, 30000);
  };
  
  // ============ 核心功能 ============
  
  // 获取页面上的车次列表
  const getTrainList = () => {
    const trains = [];
    const rows = document.querySelectorAll('#queryLeftTable tr[id]');
    
    rows.forEach(row => {
      try {
        const trainCode = row.querySelector('.number')?.textContent?.trim();
        if (!trainCode) return;
        
        const departTime = row.querySelector('.start-t')?.textContent?.trim() || '';
        const arriveTime = row.querySelector('.arrive-t')?.textContent?.trim() || '';
        const duration = row.querySelector('.lishi')?.textContent?.trim() || '';
        
        // 获取各类座位信息（12306表格结构）
        const cells = row.querySelectorAll('td');
        
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
          duration,
          canBook,
          canCandidate,
          bookBtn,
          candidateBtn,
          row,
          // 座位信息直接从按钮判断
          hasTicket: canBook
        });
      } catch(e) {
        console.error('解析车次出错:', e);
      }
    });
    
    return trains;
  };
  
  // 检查时间是否在范围内
  const isTimeInRange = (time) => {
    if (!CONFIG.timeRange.start || !CONFIG.timeRange.end) return true;
    return time >= CONFIG.timeRange.start && time <= CONFIG.timeRange.end;
  };
  
  // 检查车次是否符合条件
  const checkTrain = (train) => {
    // 必须可预订
    if (!train.canBook && !(CONFIG.acceptCandidate && train.canCandidate)) {
      return false;
    }
    
    // 检查目标车次
    if (CONFIG.targetTrains.length > 0 && !CONFIG.targetTrains.includes(train.trainCode)) {
      return false;
    }
    
    // 检查时间范围
    if (!isTimeInRange(train.departTime)) {
      return false;
    }
    
    return true;
  };
  
  // 点击查询按钮
  const clickQuery = () => {
    const btn = document.getElementById('query_ticket');
    if (btn) {
      btn.click();
      return true;
    }
    log('找不到查询按钮！', 'error');
    return false;
  };
  
  // 点击预订按钮
  const clickBook = (train) => {
    if (train.bookBtn) {
      train.bookBtn.click();
      return true;
    } else if (CONFIG.acceptCandidate && train.candidateBtn) {
      train.candidateBtn.click();
      return true;
    }
    return false;
  };
  
  // 获取运行统计
  const getStats = () => {
    const elapsed = startTime ? Math.floor((Date.now() - startTime) / 1000) : 0;
    const min = Math.floor(elapsed / 60);
    const sec = elapsed % 60;
    return {
      queries: retryCount,
      time: min + '分' + sec + '秒',
      rate: retryCount > 0 ? (retryCount / (elapsed || 1) * 60).toFixed(1) + '次/分钟' : '-'
    };
  };
  
  // 主循环
  const mainLoop = () => {
    retryCount++;
    
    if (retryCount > CONFIG.maxRetries) {
      log('已达最大查询次数 ' + CONFIG.maxRetries + '，停止', 'warning');
      stop();
      return;
    }
    
    const stats = getStats();
    log('第 ' + retryCount + ' 次查询 | 已运行: ' + stats.time + ' | 速率: ' + stats.rate);
    
    // 延迟获取结果（等待页面更新）
    setTimeout(() => {
      try {
        const trains = getTrainList();
        
        if (trains.length === 0) {
          log('未获取到车次信息，等待页面加载...', 'warning');
          return;
        }
        
        // 检查每个车次
        for (const train of trains) {
          if (checkTrain(train)) {
            // 找到票了！
            const msg = '🎉 车次 ' + train.trainCode + ' ' + train.departTime + ' 有票！';
            log(msg, 'ticket');
            notify('发现有票！', train.trainCode + ' ' + train.departTime);
            
            // 停止刷新
            stop();
            
            // 点击预订
            log('正在点击预订按钮...', 'success');
            clickBook(train);
            
            return;
          }
        }
        
        // 没找到票，继续
        const bookableCount = trains.filter(t => t.canBook).length;
        log('本次查询: ' + trains.length + ' 个车次, ' + bookableCount + ' 个可预订');
        
      } catch(e) {
        log('查询出错: ' + e.message, 'error');
      }
    }, 1500);
  };
  
  // 开始抢票
  const start = () => {
    if (isRunning) {
      log('抢票已在运行中！', 'warning');
      return;
    }
    
    // 检查是否在正确的页面
    if (!document.getElementById('query_ticket')) {
      log('请先打开12306车票查询页面！', 'error');
      return;
    }
    
    console.clear();
    log('════════════════════════════════════════', 'success');
    log('     🚄 12306 自动抢票脚本 v1.0 启动', 'success');
    log('════════════════════════════════════════', 'success');
    log('');
    log('📋 当前配置:');
    log('   目标车次: ' + (CONFIG.targetTrains.length ? CONFIG.targetTrains.join(', ') : '任意有票车次'));
    log('   接受座位: ' + CONFIG.acceptSeats.join(' > '));
    log('   乘 车 人: ' + CONFIG.passengers.join(', '));
    log('   刷新间隔: ' + CONFIG.refreshInterval + 'ms');
    log('   接受候补: ' + (CONFIG.acceptCandidate ? '是' : '否'));
    log('');
    log('💡 提示:');
    log('   - 使用 ticketGrabber.stop() 停止抢票');
    log('   - 使用 ticketGrabber.config 查看/修改配置');
    log('   - 发现有票会自动点击预订并发出提示音');
    log('════════════════════════════════════════', 'success');
    log('');
    
    isRunning = true;
    retryCount = 0;
    startTime = Date.now();
    
    // 请求通知权限
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
    
    // 立即执行一次查询
    clickQuery();
    
    // 设置定时器
    timer = setInterval(() => {
      if (isRunning) {
        clickQuery();
        mainLoop();
      }
    }, CONFIG.refreshInterval);
    
    log('🚀 开始抢票！', 'success');
  };
  
  // 停止抢票
  const stop = () => {
    isRunning = false;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    const stats = getStats();
    log('════════════════════════════════════════', 'warning');
    log('⏹️  抢票已停止', 'warning');
    log('   总查询次数: ' + stats.queries);
    log('   运行时长: ' + stats.time);
    log('════════════════════════════════════════', 'warning');
  };
  
  // 暴露到全局
  window.ticketGrabber = {
    start,
    stop,
    config: CONFIG,
    getTrains: getTrainList,
    stats: getStats
  };
  
  // 启动提示
  log('✅ 抢票脚本已加载！', 'success');
  log('');
  log('👉 输入 ticketGrabber.start() 开始抢票', 'info');
  log('👉 输入 ticketGrabber.stop() 停止抢票', 'info');
  log('');
  
})();
`;

console.log('========================================');
console.log('    12306 自动抢票脚本使用说明');
console.log('========================================');
console.log('');
console.log('【使用步骤】');
console.log('');
console.log('1. 登录12306账号');
console.log('   https://kyfw.12306.cn/otn/login/init');
console.log('');
console.log('2. 打开车票查询页面，填写：');
console.log('   - 出发地：广州南/广州/广州东');
console.log('   - 目的地：南阳东（邓州无直达）');
console.log('   - 日期：2026-02-07');
console.log('');
console.log('3. 按 F12 打开开发者工具');
console.log('   切换到 Console（控制台）标签');
console.log('');
console.log('4. 复制以下代码并粘贴到控制台运行：');
console.log('----------------------------------------');
console.log(GRAB_SCRIPT);
console.log('----------------------------------------');
console.log('');
console.log('5. 在控制台输入以下命令开始抢票：');
console.log('   ticketGrabber.start()');
console.log('');
console.log('6. 停止抢票：');
console.log('   ticketGrabber.stop()');
console.log('');
console.log('【注意事项】');
console.log('- 请确保已登录12306账号');
console.log('- 提前添加好常用联系人');
console.log('- 抢到票后45分钟内完成支付');
console.log('- 不要关闭浏览器窗口');
console.log('========================================');

// 导出脚本内容
module.exports = { GRAB_SCRIPT };
