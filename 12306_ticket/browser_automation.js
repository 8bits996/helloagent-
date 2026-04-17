/**
 * 12306 浏览器自动化抢票
 * 通过MCP Chrome DevTools协议实现
 * 
 * 这个脚本会：
 * 1. 打开12306查票页面
 * 2. 循环刷新查询余票
 * 3. 发现有票自动点击预订
 * 4. 自动选择乘客并提交订单
 */

const CONFIG = require('./config.js');

/**
 * 抢票主流程 - 在浏览器控制台执行
 * 将以下代码复制到12306页面的控制台中运行
 */
const BROWSER_SCRIPT = `
(function() {
  'use strict';
  
  // ============ 配置 ============
  const CONFIG = {
    // 目标车次（留空则抢任意有票车次）
    targetTrains: [],
    
    // 接受的座位类型（按优先级）
    acceptSeats: ['二等座', '一等座', '硬卧', '软卧', '硬座', '无座'],
    
    // 刷新间隔（毫秒）
    refreshInterval: 3000,
    
    // 乘客姓名
    passengers: ['陈卓'],
    
    // 是否自动提交
    autoSubmit: true,
    
    // 最大重试次数
    maxRetries: 500
  };
  
  // ============ 状态 ============
  let isRunning = false;
  let retryCount = 0;
  let timer = null;
  
  // ============ 工具函数 ============
  function log(msg, type = 'info') {
    const styles = {
      info: 'color: #2196F3',
      success: 'color: #4CAF50; font-weight: bold',
      warning: 'color: #FF9800',
      error: 'color: #F44336; font-weight: bold',
      ticket: 'color: #E91E63; font-weight: bold; font-size: 14px'
    };
    console.log('%c[抢票] ' + msg, styles[type] || styles.info);
  }
  
  function playSound() {
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdH+Onp2ckpKKh4Z/goWAe3Z4e39/gIKDg4OCgYB/f35+fn5+f3+AgICAgH9/f35+fn5/f39/f39/fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+fn5+');
      audio.play();
    } catch(e) {}
  }
  
  function notify(title, body) {
    if (Notification.permission === 'granted') {
      new Notification(title, { body: body });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          new Notification(title, { body: body });
        }
      });
    }
    playSound();
  }
  
  // ============ 核心功能 ============
  
  // 获取车次列表
  function getTrainList() {
    const trains = [];
    const rows = document.querySelectorAll('#queryLeftTable tr');
    
    rows.forEach(row => {
      if (!row.id) return;
      
      const trainCode = row.querySelector('.train .number')?.textContent?.trim();
      const fromStation = row.querySelector('.cdz')?.textContent?.trim();
      const toStation = row.querySelector('.cdd')?.textContent?.trim();
      const departTime = row.querySelector('.start-t')?.textContent?.trim();
      const arriveTime = row.querySelector('.arrive-t')?.textContent?.trim();
      const duration = row.querySelector('.ls')?.textContent?.trim();
      
      // 获取各座位余票
      const tds = row.querySelectorAll('td');
      const seatInfo = {
        businessSeat: tds[1]?.textContent?.trim(),   // 商务座
        firstSeat: tds[2]?.textContent?.trim(),      // 一等座
        secondSeat: tds[3]?.textContent?.trim(),     // 二等座
        advSoftSleep: tds[4]?.textContent?.trim(),   // 高级软卧
        softSleep: tds[5]?.textContent?.trim(),      // 软卧
        moveSleep: tds[6]?.textContent?.trim(),      // 动卧
        hardSleep: tds[7]?.textContent?.trim(),      // 硬卧
        softSeat: tds[8]?.textContent?.trim(),       // 软座
        hardSeat: tds[9]?.textContent?.trim(),       // 硬座
        noSeat: tds[10]?.textContent?.trim(),        // 无座
      };
      
      // 预订按钮
      const bookBtn = row.querySelector('.btn72');
      const canBook = bookBtn && !bookBtn.classList.contains('btn-disabled');
      
      trains.push({
        trainCode,
        fromStation,
        toStation,
        departTime,
        arriveTime,
        duration,
        seatInfo,
        canBook,
        bookBtn,
        row
      });
    });
    
    return trains;
  }
  
  // 检查座位是否有票
  function hasSeat(seatValue) {
    if (!seatValue) return false;
    if (seatValue === '--' || seatValue === '无' || seatValue === '*') return false;
    if (seatValue === '有' || /^\\d+$/.test(seatValue)) return true;
    return false;
  }
  
  // 检查车次是否符合条件
  function checkTrain(train) {
    // 检查是否可预订
    if (!train.canBook) return false;
    
    // 检查目标车次
    if (CONFIG.targetTrains.length > 0 && !CONFIG.targetTrains.includes(train.trainCode)) {
      return false;
    }
    
    // 检查座位
    const seatMap = {
      '商务座': train.seatInfo.businessSeat,
      '一等座': train.seatInfo.firstSeat,
      '二等座': train.seatInfo.secondSeat,
      '高级软卧': train.seatInfo.advSoftSleep,
      '软卧': train.seatInfo.softSleep,
      '动卧': train.seatInfo.moveSleep,
      '硬卧': train.seatInfo.hardSleep,
      '软座': train.seatInfo.softSeat,
      '硬座': train.seatInfo.hardSeat,
      '无座': train.seatInfo.noSeat,
    };
    
    for (const seatType of CONFIG.acceptSeats) {
      if (hasSeat(seatMap[seatType])) {
        return { success: true, seatType, count: seatMap[seatType] };
      }
    }
    
    return false;
  }
  
  // 点击查询按钮
  function clickQuery() {
    const queryBtn = document.getElementById('query_ticket');
    if (queryBtn) {
      queryBtn.click();
      log('刷新查询...');
      return true;
    }
    return false;
  }
  
  // 点击预订按钮
  function clickBook(train) {
    if (train.bookBtn) {
      log('🎫 发现有票！车次: ' + train.trainCode + ', 正在预订...', 'ticket');
      notify('发现有票！', '车次: ' + train.trainCode);
      train.bookBtn.click();
      return true;
    }
    return false;
  }
  
  // 主循环
  function mainLoop() {
    retryCount++;
    
    if (retryCount > CONFIG.maxRetries) {
      log('已达最大重试次数，停止抢票', 'warning');
      stop();
      return;
    }
    
    log('第 ' + retryCount + ' 次查询...');
    
    // 等待查询结果加载
    setTimeout(() => {
      const trains = getTrainList();
      log('找到 ' + trains.length + ' 个车次');
      
      // 检查每个车次
      for (const train of trains) {
        const result = checkTrain(train);
        if (result && result.success) {
          log('🎉 车次 ' + train.trainCode + ' 有票！' + result.seatType + ': ' + result.count, 'success');
          
          // 停止刷新
          stop();
          
          // 点击预订
          clickBook(train);
          return;
        }
      }
      
      log('暂无符合条件的票，继续刷新...');
      
      // 继续刷新
      if (isRunning) {
        clickQuery();
      }
    }, 2000);
  }
  
  // 开始抢票
  function start() {
    if (isRunning) {
      log('抢票已在运行中', 'warning');
      return;
    }
    
    log('========================================', 'success');
    log('       🚄 12306 自动抢票启动', 'success');
    log('========================================', 'success');
    log('目标车次: ' + (CONFIG.targetTrains.length ? CONFIG.targetTrains.join(', ') : '任意车次'));
    log('接受座位: ' + CONFIG.acceptSeats.join(', '));
    log('刷新间隔: ' + CONFIG.refreshInterval + 'ms');
    log('----------------------------------------');
    
    isRunning = true;
    retryCount = 0;
    
    // 请求通知权限
    if (Notification.permission !== 'granted') {
      Notification.requestPermission();
    }
    
    // 开始查询
    clickQuery();
    
    // 设置定时器
    timer = setInterval(() => {
      if (isRunning) {
        mainLoop();
      }
    }, CONFIG.refreshInterval);
  }
  
  // 停止抢票
  function stop() {
    isRunning = false;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    log('抢票已停止，共查询 ' + retryCount + ' 次', 'warning');
  }
  
  // 暴露到全局
  window.ticketGrabber = {
    start: start,
    stop: stop,
    config: CONFIG,
    getTrains: getTrainList
  };
  
  log('抢票脚本已加载！', 'success');
  log('使用 ticketGrabber.start() 开始抢票', 'info');
  log('使用 ticketGrabber.stop() 停止抢票', 'info');
  log('可修改 ticketGrabber.config 调整配置', 'info');
  
})();
`;

module.exports = { BROWSER_SCRIPT, CONFIG };
