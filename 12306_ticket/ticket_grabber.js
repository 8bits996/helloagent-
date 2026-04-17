/**
 * 12306 自动抢票脚本
 * 基于浏览器自动化实现
 * 
 * 功能：
 * 1. 自动查询余票
 * 2. 发现有票自动预订
 * 3. 自动填写乘客信息
 * 4. 支持候补购票
 * 5. 抢票成功通知
 */

const CONFIG = require('./config.js');

// 12306 API 地址
const API = {
  // 查询余票
  queryTicket: 'https://kyfw.12306.cn/otn/leftTicket/queryG',
  // 查询余票（备用）
  queryTicketAlt: 'https://kyfw.12306.cn/otn/leftTicket/queryZ',
  // 提交订单
  submitOrder: 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest',
  // 确认乘客
  confirmPassenger: 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue',
  // 候补订单
  candidateOrder: 'https://kyfw.12306.cn/otn/afterNate/submitOrderRequest',
  // 检查用户登录状态
  checkUser: 'https://kyfw.12306.cn/otn/login/checkUser',
  // 车站代码
  stationNames: 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
};

// 座位类型代码映射
const SEAT_TYPE_CODES = {
  '商务座': '9',
  '特等座': 'P',
  '一等座': 'M',
  '二等座': 'O',
  '高级软卧': '6',
  '软卧': '4',
  '动卧': 'F',
  '硬卧': '3',
  '软座': '2',
  '硬座': '1',
  '无座': '1',  // 无座和硬座同代码
};

// 票务状态
const TICKET_STATUS = {
  AVAILABLE: '有',      // 有票
  FEW: '有',           // 余票不多
  NO: '无',            // 无票
  CANDIDATE: '候',     // 候补
  NOT_SALE: '--',      // 未开售
};

class TicketGrabber {
  constructor() {
    this.retryCount = 0;
    this.isRunning = false;
    this.foundTickets = [];
    this.startTime = null;
  }

  /**
   * 生成查询URL
   */
  generateQueryUrl(fromStation, toStation, date) {
    const params = new URLSearchParams({
      'leftTicketDTO.train_date': date,
      'leftTicketDTO.from_station': fromStation.code,
      'leftTicketDTO.to_station': toStation.code,
      'purpose_codes': 'ADULT'
    });
    return `${API.queryTicket}?${params.toString()}`;
  }

  /**
   * 生成12306购票页面URL
   */
  generatePageUrl(fromStation, toStation, date) {
    const fromEncoded = encodeURIComponent(fromStation.name);
    const toEncoded = encodeURIComponent(toStation.name);
    return `https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=${fromEncoded},${fromStation.code}&ts=${toEncoded},${toStation.code}&date=${date}&flag=N,N,Y`;
  }

  /**
   * 解析车次信息
   */
  parseTrainInfo(trainData) {
    if (!trainData || !trainData.queryLeftNewDTO) {
      return null;
    }
    
    const info = trainData.queryLeftNewDTO;
    return {
      trainNo: info.train_no,           // 车次编号
      trainCode: info.station_train_code, // 车次代码 G1234
      fromStation: info.from_station_name,
      toStation: info.to_station_name,
      departTime: info.start_time,       // 出发时间
      arriveTime: info.arrive_time,      // 到达时间
      duration: info.lishi,              // 历时
      date: info.start_train_date,       // 发车日期
      
      // 各座位余票情况
      businessSeat: info.swz_num,        // 商务座
      firstClassSeat: info.zy_num,       // 一等座
      secondClassSeat: info.ze_num,      // 二等座
      advancedSoftSleeper: info.gr_num,  // 高级软卧
      softSleeper: info.rw_num,          // 软卧
      moveSleeper: info.dw_num,          // 动卧
      hardSleeper: info.yw_num,          // 硬卧
      softSeat: info.rz_num,             // 软座
      hardSeat: info.yz_num,             // 硬座
      noSeat: info.wz_num,               // 无座
      
      // 是否可预订
      canBook: info.canWebBuy === 'Y',
      secretStr: trainData.secretStr,    // 预订密钥
      
      // 候补信息
      canCandidate: info.canWebBuy === 'N' && (
        info.swz_num === '候' || 
        info.zy_num === '候' || 
        info.ze_num === '候'
      )
    };
  }

  /**
   * 检查是否有可用座位
   */
  hasAvailableSeat(trainInfo) {
    const seatChecks = [
      { type: '商务座', value: trainInfo.businessSeat },
      { type: '一等座', value: trainInfo.firstClassSeat },
      { type: '二等座', value: trainInfo.secondClassSeat },
      { type: '高级软卧', value: trainInfo.advancedSoftSleeper },
      { type: '软卧', value: trainInfo.softSleeper },
      { type: '动卧', value: trainInfo.moveSleeper },
      { type: '硬卧', value: trainInfo.hardSleeper },
      { type: '软座', value: trainInfo.softSeat },
      { type: '硬座', value: trainInfo.hardSeat },
      { type: '无座', value: trainInfo.noSeat },
    ];

    for (const seat of seatChecks) {
      if (!CONFIG.seatTypes[seat.type]) continue;
      
      if (seat.value && seat.value !== '' && seat.value !== '无' && seat.value !== '--') {
        // 有票或者显示数字
        if (seat.value === '有' || /^\d+$/.test(seat.value)) {
          return { available: true, seatType: seat.type, count: seat.value };
        }
      }
    }
    
    return { available: false };
  }

  /**
   * 检查出发时间是否在范围内
   */
  isTimeInRange(departTime) {
    const { start, end } = CONFIG.departTimeRange;
    return departTime >= start && departTime <= end;
  }

  /**
   * 检查车次类型是否符合要求
   */
  isTrainTypeAllowed(trainCode) {
    const firstChar = trainCode.charAt(0);
    
    if (/^G/.test(trainCode)) return CONFIG.trainTypes.G;
    if (/^D/.test(trainCode)) return CONFIG.trainTypes.D;
    if (/^Z/.test(trainCode)) return CONFIG.trainTypes.Z;
    if (/^T/.test(trainCode)) return CONFIG.trainTypes.T;
    if (/^K/.test(trainCode)) return CONFIG.trainTypes.K;
    
    return CONFIG.trainTypes.other;
  }

  /**
   * 格式化日志输出
   */
  log(message, type = 'info') {
    const time = new Date().toLocaleTimeString('zh-CN');
    const prefix = {
      info: '📋',
      success: '✅',
      warning: '⚠️',
      error: '❌',
      ticket: '🎫'
    }[type] || '📋';
    
    console.log(`[${time}] ${prefix} ${message}`);
  }

  /**
   * 获取运行统计信息
   */
  getStats() {
    const runTime = this.startTime 
      ? Math.floor((Date.now() - this.startTime) / 1000)
      : 0;
    
    const minutes = Math.floor(runTime / 60);
    const seconds = runTime % 60;
    
    return {
      retryCount: this.retryCount,
      runTime: `${minutes}分${seconds}秒`,
      foundTickets: this.foundTickets.length
    };
  }
}

// 导出类供外部使用
module.exports = TicketGrabber;

// 打印配置信息
console.log('========================================');
console.log('       12306 自动抢票脚本 v1.0');
console.log('========================================');
console.log('');
console.log('📍 行程配置:');
console.log(`   出发站: ${CONFIG.fromStations.map(s => s.name).join(', ')}`);
console.log(`   到达站: ${CONFIG.toStations.map(s => s.name).join(', ')}`);
console.log(`   出发日期: ${CONFIG.dates.join(', ')}`);
console.log(`   乘车人: ${CONFIG.passengers.join(', ')}`);
console.log('');
console.log('⚙️  抢票设置:');
console.log(`   刷新间隔: ${CONFIG.refreshInterval}ms`);
console.log(`   接受候补: ${CONFIG.acceptCandidate ? '是' : '否'}`);
console.log(`   接受无座: ${CONFIG.seatTypes['无座'] ? '是' : '否'}`);
console.log('========================================');
