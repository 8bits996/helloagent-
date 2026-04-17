/**
 * 12306 抢票脚本 - 襄阳到武当山
 * 
 * 【行程信息】
 * - 出发站: 襄阳 / 襄阳东
 * - 到达站: 武当山西
 * - 出发日期: 2026-02-09
 * - 起售时间: 2026-01-26 16:00:00
 * 
 * 【乘车人】(需提前在12306添加为常用联系人)
 * - 陈卓 (成人票)
 * - 冯巧玉 (成人票)  
 * - 陈妙可 (成人票)
 * - 陈苇杭 (儿童票)
 * 
 * 【座位类型】优先二等座
 * 
 * 【使用方法】
 * 1. 提前登录12306账号，确保4位乘客都在常用联系人中
 * 2. 进入购票页面，设置：襄阳→武当山西，日期2026-02-09
 * 3. 打开F12控制台，粘贴此脚本回车
 * 4. 执行 GrabXY.schedule() 等待16:00自动抢票
 *    或执行 GrabXY.go() 立即开始（已开售后使用）
 */

(function() {
    'use strict';
    
    // ======================== 配置区 ========================
    const CONFIG = {
        // 起售时间: 1月26日16:00
        grabTime: {
            hour: 16,
            minute: 0,
            second: 0,
            preStartMs: 300  // 提前300ms开始
        },
        
        // 座位优先级
        seatPriority: ['二等座', '一等座', '无座'],
        
        // 乘客配置（票种：1=成人票, 2=儿童票）
        // ⚠️ 确保这4人都在12306常用联系人中
        passengers: {
            '陈卓': { ticketType: '1', typeName: '成人票' },
            '冯巧玉': { ticketType: '1', typeName: '成人票' },
            '陈妙可': { ticketType: '1', typeName: '成人票' },
            '陈苇杭': { ticketType: '2', typeName: '儿童票' }
        },
        
        // 性能配置
        queryInterval: 100,      // 刷票间隔(ms)
        maxRetries: 1000,        // 最大重试次数
        passengerDelay: 100      // 选择乘客后等待(ms)
    };
    
    // ======================== 日志 ========================
    const log = (msg, type = 'info') => {
        const styles = {
            info: 'color:#2196F3',
            success: 'color:#4CAF50;font-weight:bold',
            error: 'color:#f44336;font-weight:bold',
            warn: 'color:#FF9800',
            critical: 'color:#fff;background:#E91E63;font-weight:bold;padding:2px 6px;font-size:14px'
        };
        const t = new Date().toLocaleTimeString('zh-CN',{hour12:false}) + '.' + String(Date.now()%1000).padStart(3,'0');
        console.log(`%c[抢票] ${t} ${msg}`, styles[type]);
    };
    
    // ======================== 工具函数 ========================
    const wait = ms => new Promise(r => setTimeout(r, ms));
    
    const trigger = (el, type) => el.dispatchEvent(new Event(type, { bubbles: true }));
    
    const getMsToTarget = () => {
        const now = new Date();
        const target = new Date(now);
        target.setHours(CONFIG.grabTime.hour, CONFIG.grabTime.minute, CONFIG.grabTime.second, 0);
        return target - now;
    };
    
    // ======================== 弹窗处理 ========================
    const closeDialogs = () => {
        ['.dhtmlx_window_active .btn_def', '.layui-layer-btn0', '.modal-footer .btn-primary']
            .forEach(sel => {
                document.querySelectorAll(sel).forEach(btn => {
                    if (/确认|确定|知道|关闭|OK/i.test(btn.textContent)) btn.click();
                });
            });
        if (typeof layer !== 'undefined') try { layer.closeAll(); } catch(e) {}
    };
    
    // 监控弹窗自动关闭
    const observer = new MutationObserver(mutations => {
        mutations.forEach(m => {
            m.addedNodes.forEach(node => {
                if (node.nodeType === 1 && (node.classList?.contains('dhtmlx_window_active') || 
                    node.classList?.contains('layui-layer'))) {
                    setTimeout(closeDialogs, 50);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // ======================== 查票模块 ========================
    let isRunning = false;
    let retryCount = 0;
    
    const clickQuery = () => {
        const btn = document.getElementById('query_ticket');
        if (btn) { btn.click(); return true; }
        return false;
    };
    
    const findTicket = () => {
        const rows = document.querySelectorAll('#queryLeftTable tr[id]');
        
        for (const row of rows) {
            // 查找预订按钮（非灰色）
            const bookBtn = row.querySelector('a.btn72:not(.btn-disabled)');
            if (bookBtn) {
                // 检查二等座是否有票
                const tds = row.querySelectorAll('td');
                for (const td of tds) {
                    const text = td.textContent.trim();
                    // "有" 或 数字表示有票
                    if (text === '有' || /^\d+$/.test(text)) {
                        const trainNum = row.querySelector('.number')?.textContent?.trim() || 'unknown';
                        log(`✓ 找到有票车次: ${trainNum}`, 'success');
                        return { row, bookBtn };
                    }
                }
            }
        }
        return null;
    };
    
    const startGrab = () => {
        if (isRunning) { log('已在运行中', 'warn'); return; }
        isRunning = true;
        retryCount = 0;
        
        const loop = () => {
            if (!isRunning) return;
            
            retryCount++;
            if (retryCount > CONFIG.maxRetries) {
                log(`达到最大重试${CONFIG.maxRetries}次`, 'error');
                isRunning = false;
                return;
            }
            
            closeDialogs();
            
            const result = findTicket();
            if (result) {
                log('🎫 点击预订!', 'critical');
                result.bookBtn.click();
                isRunning = false;
                
                // 等待跳转到订单页面后自动处理
                setTimeout(() => {
                    if (location.href.includes('confirmPassenger') || location.href.includes('initDc')) {
                        processOrder(true);
                    }
                }, 1500);
                return;
            }
            
            if (retryCount % 20 === 0) {
                log(`第${retryCount}次查询...`, 'info');
            }
            
            clickQuery();
            setTimeout(loop, CONFIG.queryInterval);
        };
        
        log('🔥 开始抢票!', 'critical');
        loop();
    };
    
    const stopGrab = () => {
        isRunning = false;
        log('抢票已停止', 'warn');
    };
    
    // ======================== 订单页面处理 ========================
    const selectPassengers = async () => {
        const list = document.getElementById('normal_passenger_id');
        if (!list) {
            log('等待乘客列表加载...', 'info');
            await wait(300);
            return selectPassengers();
        }
        
        const names = Object.keys(CONFIG.passengers);
        let count = 0;
        
        list.querySelectorAll('li').forEach(li => {
            const label = li.querySelector('label');
            const checkbox = li.querySelector('input[type="checkbox"]');
            if (label && checkbox) {
                const name = label.textContent.trim();
                if (names.some(p => name.includes(p)) && !checkbox.checked) {
                    checkbox.click();
                    count++;
                    log(`✓ 选择: ${name}`, 'success');
                }
            }
        });
        
        return count;
    };
    
    const fixTicketTypes = () => {
        const rows = document.querySelectorAll('#ticketInfo_id tr');
        let fixed = 0;
        
        rows.forEach(row => {
            const nameInput = row.querySelector('input[readonly]');
            const ticketSelect = row.querySelector('select[id^="ticketType"]');
            if (!nameInput || !ticketSelect) return;
            
            const name = nameInput.value;
            for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
                if (name.includes(pName)) {
                    if (ticketSelect.value !== pConfig.ticketType) {
                        ticketSelect.value = pConfig.ticketType;
                        trigger(ticketSelect, 'change');
                        log(`修正票种: ${pName} → ${pConfig.typeName}`, 'success');
                        fixed++;
                    }
                    break;
                }
            }
        });
        
        return fixed;
    };
    
    const submitOrder = () => {
        const btn = document.getElementById('submitOrder_id');
        if (btn && !btn.disabled) {
            log('📤 提交订单!', 'critical');
            btn.click();
            return true;
        }
        log('提交按钮不可用', 'error');
        return false;
    };
    
    const processOrder = async (autoSubmit = false) => {
        log('处理订单页面...', 'info');
        
        closeDialogs();
        await wait(200);
        
        // 选择乘客
        const selected = await selectPassengers();
        log(`已选择 ${selected} 位乘客`, selected === 4 ? 'success' : 'warn');
        
        await wait(CONFIG.passengerDelay * selected);
        closeDialogs();
        await wait(200);
        
        // 修正票种（确保陈苇杭是儿童票）
        fixTicketTypes();
        
        // 验证
        const rows = document.querySelectorAll('#ticketInfo_id tr');
        log(`订单中有 ${rows.length} 位乘客`, 'info');
        
        if (autoSubmit) {
            await wait(100);
            submitOrder();
        }
    };
    
    // ======================== 定时启动 ========================
    const schedule = () => {
        const ms = getMsToTarget();
        
        if (ms <= 0) {
            log('已过16:00，立即开始抢票', 'warn');
            startGrab();
            return;
        }
        
        const secs = Math.ceil(ms / 1000);
        log(`⏰ 距离16:00起售还有 ${secs} 秒，已进入等待`, 'critical');
        log(`👥 乘客: 陈卓(成人) 冯巧玉(成人) 陈妙可(成人) 陈苇杭(儿童)`, 'info');
        log(`🎫 目标: 二等座`, 'info');
        
        // 倒计时显示
        let countdown = secs;
        const timer = setInterval(() => {
            countdown--;
            if (countdown <= 10 && countdown > 0) {
                log(`⏳ ${countdown}秒...`, 'warn');
            }
            if (countdown <= 0) {
                clearInterval(timer);
            }
        }, 1000);
        
        // 定时启动
        setTimeout(() => {
            log('🚀 时间到! 开始抢票!', 'critical');
            startGrab();
        }, ms - CONFIG.grabTime.preStartMs);
    };
    
    // ======================== 暴露全局接口 ========================
    window.GrabXY = {
        go: startGrab,           // 立即抢票
        stop: stopGrab,          // 停止
        schedule: schedule,      // 定时16:00抢票
        order: () => processOrder(true),  // 处理订单页并提交
        test: () => processOrder(false),  // 测试订单页（不提交）
        config: CONFIG
    };
    
    // ======================== 启动信息 ========================
    console.clear();
    console.log('%c╔════════════════════════════════════════════════════════╗', 'color:#4CAF50');
    console.log('%c║     12306 抢票脚本 - 襄阳 → 武当山西                   ║', 'color:#4CAF50;font-weight:bold;font-size:16px');
    console.log('%c╠════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 📅 日期: 2026-02-09                                    ║', 'color:#2196F3');
    console.log('%c║ ⏰ 起售: 2026-01-26 16:00                              ║', 'color:#2196F3');
    console.log('%c║ 🎫 座位: 二等座                                        ║', 'color:#2196F3');
    console.log('%c╠════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 👥 乘车人:                                             ║', 'color:#FF9800');
    console.log('%c║    陈卓 (成人) | 冯巧玉 (成人)                         ║', 'color:#FF9800');
    console.log('%c║    陈妙可 (成人) | 陈苇杭 (儿童)                       ║', 'color:#FF9800');
    console.log('%c╠════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 💡 命令:                                               ║', 'color:#9C27B0');
    console.log('%c║    GrabXY.schedule()  - 定时16:00自动抢票              ║', 'color:#9C27B0');
    console.log('%c║    GrabXY.go()        - 立即开始抢票                   ║', 'color:#9C27B0');
    console.log('%c║    GrabXY.stop()      - 停止抢票                       ║', 'color:#9C27B0');
    console.log('%c║    GrabXY.order()     - 处理订单页(自动提交)           ║', 'color:#9C27B0');
    console.log('%c║    GrabXY.test()      - 测试订单页(不提交)             ║', 'color:#9C27B0');
    console.log('%c╚════════════════════════════════════════════════════════╝', 'color:#4CAF50');
    console.log('%c⚠️ 使用前请确保4位乘客都已添加到12306常用联系人!', 'color:#f44336;font-weight:bold');
    
    log('脚本已加载，弹窗监控已启动', 'success');
    
})();
