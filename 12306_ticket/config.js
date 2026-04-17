/**
 * 12306 抢票配置文件
 * 根据你的需求修改以下配置
 */

const CONFIG = {
  // ========== 行程信息 ==========
  // 出发站（可配置多个，按优先级排序）
  fromStations: [
    { name: '深圳北', code: 'IOQ' },
    { name: '深圳', code: 'SZQ' },
    { name: '深圳东', code: 'BJQ' },
    { name: '东莞', code: 'DAQ' },
    { name: '东莞东', code: 'DMQ' },
    { name: '广州南', code: 'IZQ' },
    { name: '广州', code: 'GZQ' },
    { name: '广州东', code: 'GGQ' }
  ],
  
  // 到达站（可配置多个，按优先级排序）
  toStations: [
    { name: '邓州东', code: 'DZF' },
    { name: '邓州', code: 'DPF' },
    { name: '襄阳东', code: 'XWN' },
    { name: '襄阳', code: 'XFN' },
    { name: '南阳东', code: 'NDG' },
    { name: '南阳', code: 'NYN' }
  ],
  
  // 出发日期（可配置多个日期）
  dates: ['2026-02-07', '2026-02-06', '2026-02-08'],
  
  // ========== 车次筛选 ==========
  // 优先车次（留空则不限制）
  preferTrains: [], // 例如: ['G1234', 'D5678']
  
  // 车次类型筛选
  trainTypes: {
    G: true,  // 高铁
    D: true,  // 动车
    Z: true,  // 直达
    T: true,  // 特快
    K: true,  // 快速
    other: true // 其他
  },
  
  // ========== 座位类型 ==========
  // 按优先级排序，true表示接受该座位类型
  // 【只抢硬卧和二等座】
  seatTypes: {
    '商务座': false,
    '一等座': false,
    '二等座': true,   // ✅ 高铁/动车二等座
    '高级软卧': false,
    '软卧': false,
    '动卧': false,
    '硬卧': true,     // ✅ 普通列车硬卧
    '软座': false,
    '硬座': false,
    '无座': false,
  },
  
  // ========== 乘车人 ==========
  // 需要与12306账号中的常用联系人姓名完全一致
  passengers: ['陈卓'],
  
  // ========== 时间筛选 ==========
  // 出发时间范围（24小时制）
  departTimeRange: {
    start: '06:00',
    end: '23:59'
  },
  
  // ========== 抢票设置 ==========
  // 刷新间隔（毫秒），建议不低于3000，避免被封
  refreshInterval: 3000,
  
  // 最大重试次数
  maxRetries: 1000,
  
  // 抢票模式
  mode: 'normal', // 'normal': 普通模式, 'candidate': 候补模式
  
  // 是否接受候补
  acceptCandidate: true,
  
  // ========== 通知设置 ==========
  notification: {
    sound: true,      // 声音提醒
    desktop: true,    // 桌面通知
  }
};

module.exports = CONFIG;
