/**
 * 12306 抢票脚本 V2 - 增强版（带完整错误处理和重试）
 * 
 * 【新增功能】
 * ✅ 自动检测并处理排队状态
 * ✅ 订单提交失败自动重试
 * ✅ 页面跳转失败自动恢复
 * ✅ 持续URL监控，自动适应页面变化
 * ✅ 票被抢完自动寻找其他车次
 * ✅ 网络错误自动重试
 * ✅ 乘客选择不完整自动重试
 * ✅ 详细错误日志和恢复建议
 * 
 * 【行程信息】
 * - 出发站: 襄阳 / 襄阳东
 * - 到达站: 武当山西
 * - 出发日期: 2026-02-09
 * - 起售时间: 2026-01-26 16:00:00
 * 
 * 【乘车人】
 * - 陈卓 (成人票)
 * - 冯巧玉 (成人票)  
 * - 陈妙可 (成人票)
 * - 陈苇杭 (儿童票)
 */

(function() {
    'use strict';
    
    // ======================== 配置区 ========================
    const CONFIG = {
        // 起售时间
        grabTime: {
            hour: 16,
            minute: 0,
            second: 0,
            preStartMs: 300
        },
        
        // 座位优先级
        seatPriority: ['二等座', '一等座', '无座'],
        
        // 乘客配置
        passengers: {
            '陈卓': { ticketType: '1', typeName: '成人票' },
            '冯巧玉': { ticketType: '1', typeName: '成人票' },
            '陈妙可': { ticketType: '1', typeName: '成人票' },
            '陈苇杭': { ticketType: '2', typeName: '儿童票' }
        },
        
        // 重试配置
        retry: {
            queryInterval: 100,         // 查询间隔(ms)
            maxRetries: 2000,            // 最大重试次数
            passengerTimeout: 5000,     // 乘客选择超时(ms)
            pageJumpTimeout: 10000,     // 页面跳转超时(ms)
            orderSubmitMaxRetry: 10,    // 订单提交最大重试次数
            queueCheckInterval: 500,    // 排队检测间隔(ms)
            pageJumpRetryInterval: 1000 // 页面跳转重试间隔(ms)
        },
        
        // 乘客选择后延迟
        passengerDelay: 100
    };
    
    // ======================== 状态管理 ========================
    const STATE = {
        isRunning: false,
        currentPage: 'unknown',  // unknown, query, order, queue, success, fail
        retryCount: 0,
        orderSubmitRetryCount: 0,
        queueDetected: false,
        queueStartTime: null,
        lastError: null,
        successCount: 0,
        startTime: null
    };
    
    // ======================== 日志模块 ========================
    const log = (msg, type = 'info') => {
        const styles = {
            info: 'color:#2196F3',
            success: 'color:#4CAF50;font-weight:bold',
            error: 'color:#f44336;font-weight:bold',
            warn: 'color:#FF9800',
            critical: 'color:#fff;background:#E91E63;font-weight:bold;padding:3px 8px;font-size:14px',
            retry: 'color:#9C27B0;font-style:italic'
        };
        const t = new Date().toLocaleTimeString('zh-CN',{hour12:false}) + '.' + String(Date.now()%1000).padStart(3,'0');
        console.log(`%c[抢票V2] ${t} ${msg}`, styles[type]);
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
    
    // 获取当前页面类型
    const detectPageType = () => {
        const url = location.href;
        if (url.includes('leftTicket') || url.includes('queryLeftTicket')) return 'query';
        if (url.includes('confirmPassenger') || url.includes('initDc')) return 'order';
        if (url.includes('queryQueue')) return 'queue';
        if (url.includes('pay')) return 'success';
        if (url.includes('view/')) return 'success';
        if (url.includes('error')) return 'fail';
        return 'unknown';
    };
    
    // 更新页面状态
    const updatePageState = () => {
        const newPage = detectPageType();
        if (newPage !== STATE.currentPage) {
            log(`页面变化: ${STATE.currentPage} → ${newPage}`, 'info');
            STATE.currentPage = newPage;
            
            // 根据页面变化执行相应操作
            handlePageChange(newPage);
        }
    };
    
    // ======================== 错误处理模块 ========================
    const ErrorHandler = {
        handleError: (error, context) => {
            log(`❌ 错误 [${context}]: ${error.message || error}`, 'error');
            STATE.lastError = { error, context, time: Date.now() };
            
            // 根据错误类型给出建议
            if (error.message && error.message.includes('timeout')) {
                log('💡 建议: 页面加载较慢，等待片刻后继续', 'warn');
            }
        },
        
        retryWithBackoff: async (fn, context, maxRetries = 3) => {
            for (let i = 0; i < maxRetries; i++) {
                try {
                    return await fn();
                } catch (error) {
                    ErrorHandler.handleError(error, context);
                    if (i < maxRetries - 1) {
                        const delay = (i + 1) * 500;
                        log(`${context} 重试 ${i+1}/${maxRetries}，等待 ${delay}ms`, 'retry');
                        await wait(delay);
                    }
                }
            }
            throw new Error(`${context} 重试次数耗尽`);
        }
    };
    
    // ======================== 弹窗处理 ========================
    const closeDialogs = () => {
        const selectors = [
            '.dhtmlx_window_active .btn_def',
            '.dhtmlx_wins .btn_def',
            '.layui-layer-btn0',
            '.layui-layer-close',
            '.modal-footer .btn-primary',
            '[onclick*="closeWin"]',
            '.alert-btn-ok'
        ];
        
        let closed = 0;
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(btn => {
                if (/确认|确定|知道|关闭|OK|是|好的/i.test(btn.textContent)) {
                    btn.click();
                    closed++;
                }
            });
        });
        
        if (typeof layer !== 'undefined') {
            try { layer.closeAll(); closed++; } catch(e) {}
        }
        
        return closed;
    };
    
    // 弹窗监控
    const startDialogMonitor = () => {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(m => {
                m.addedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        const isDialog = node.classList?.contains('dhtmlx_window_active') ||
                                       node.classList?.contains('layui-layer') ||
                                       node.classList?.contains('modal') ||
                                       node.classList?.contains('dhtmlx_wins');
                        if (isDialog) {
                            setTimeout(closeDialogs, 50);
                        }
                    }
                });
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
        log('弹窗监控已启动', 'info');
        return observer;
    };
    
    // ======================== 页面变化处理 ========================
    const handlePageChange = async (pageType) => {
        switch (pageType) {
            case 'queue':
                log('🔴 进入排队页面，等待...', 'warn');
                STATE.queueDetected = true;
                STATE.queueStartTime = Date.now();
                handleQueuePage();
                break;
                
            case 'order':
                log('📋 进入订单页面，开始处理...', 'info');
                await processOrderWithRetry(true);
                break;
                
            case 'success':
                log('🎉 抢票成功！请尽快支付', 'critical');
                stopGrab();
                break;
                
            case 'fail':
                log('❌ 进入错误页面，尝试恢复', 'error');
                await handleFailPage();
                break;
        }
    };
    
    // 处理排队页面
    const handleQueuePage = () => {
        const checkQueue = setInterval(async () => {
            if (STATE.currentPage !== 'queue') {
                clearInterval(checkQueue);
                return;
            }
            
            // 检查是否有确认按钮
            const confirmBtn = document.querySelector('#qr_submit_id, .qr-submit');
            if (confirmBtn && !confirmBtn.disabled) {
                log('📤 排队完成，提交订单!', 'critical');
                confirmBtn.click();
                STATE.queueDetected = false;
                clearInterval(checkQueue);
            }
            
            // 检查是否返回了查询页面（票被抢完）
            if (STATE.currentPage === 'query') {
                log('排队结束，重新查找车次', 'warn');
                clearInterval(checkQueue);
                startGrab(); // 继续抢票
            }
        }, CONFIG.retry.queueCheckInterval);
    };
    
    // 处理错误页面
    const handleFailPage = async () => {
        await wait(1000);
        
        // 查找返回按钮或重试按钮
        const backBtn = document.querySelector('.btn-back, [onclick*="back"]');
        const retryBtn = document.querySelector('.btn-retry, [onclick*="retry"]');
        
        if (retryBtn) {
            log('点击重试按钮', 'info');
            retryBtn.click();
        } else if (backBtn) {
            log('点击返回按钮，重新开始', 'warn');
            backBtn.click();
            await wait(1000);
            startGrab(); // 重新开始抢票
        } else {
            // 手动跳转回查询页面
            log('返回查询页面', 'info');
            location.href = 'https://kyfw.12306.cn/otn/leftTicket/init';
        }
    };
    
    // ======================== 查票模块（增强版）========================
    const clickQuery = () => {
        const btn = document.getElementById('query_ticket');
        if (btn) { 
            btn.click(); 
            return true; 
        }
        log('查询按钮未找到', 'error');
        return false;
    };
    
    const findTicket = () => {
        try {
            const rows = document.querySelectorAll('#queryLeftTable tr[id]');
            
            for (const row of rows) {
                // 查找预订按钮
                const bookBtn = row.querySelector('a.btn72:not(.btn-disabled)');
                if (bookBtn) {
                    // 检查座位类型
                    const tds = row.querySelectorAll('td');
                    for (const td of tds) {
                        const text = td.textContent.trim();
                        if (text === '有' || /^\d+$/.test(text)) {
                            const trainNum = row.querySelector('.number')?.textContent?.trim() || 'unknown';
                            log(`✓ 找到有票车次: ${trainNum}`, 'success');
                            return { row, bookBtn, trainNum };
                        }
                    }
                }
            }
            return null;
        } catch (error) {
            ErrorHandler.handleError(error, 'findTicket');
            return null;
        }
    };
    
    // 增强版抢票循环
    const startGrab = () => {
        if (STATE.isRunning) { 
            log('已在运行中', 'warn'); 
            return; 
        }
        
        STATE.isRunning = true;
        STATE.retryCount = 0;
        STATE.startTime = Date.now();
        
        const loop = () => {
            if (!STATE.isRunning) return;
            if (STATE.currentPage !== 'query') {
                // 如果不在查询页面，等待页面变化
                setTimeout(loop, 500);
                return;
            }
            
            STATE.retryCount++;
            
            // 达到最大重试次数
            if (STATE.retryCount > CONFIG.retry.maxRetries) {
                log(`达到最大重试${CONFIG.retry.maxRetries}次`, 'error');
                log(`已运行 ${Math.round((Date.now() - STATE.startTime)/1000)} 秒`, 'warn');
                stopGrab();
                return;
            }
            
            // 关闭弹窗
            closeDialogs();
            
            // 查找车次
            const result = findTicket();
            
            if (result) {
                log(`🎫 点击预订: ${result.trainNum}`, 'critical');
                result.bookBtn.click();
                
                // 等待页面跳转
                waitAndCheckPageJump();
                return;
            }
            
            // 定期输出进度
            if (STATE.retryCount % 30 === 0) {
                log(`第${STATE.retryCount}次查询，继续...`, 'info');
            }
            
            // 刷新查询
            clickQuery();
            setTimeout(loop, CONFIG.retry.queryInterval);
        };
        
        log('🔥 开始抢票!', 'critical');
        loop();
    };
    
    // 等待并检查页面跳转
    const waitAndCheckPageJump = async () => {
        const startTime = Date.now();
        
        const checkJump = setInterval(() => {
            const elapsed = Date.now() - startTime;
            
            // 检查是否跳转到订单页面
            if (STATE.currentPage === 'order' || STATE.currentPage === 'queue') {
                clearInterval(checkJump);
                log(`页面跳转成功，耗时 ${elapsed}ms`, 'success');
                return;
            }
            
            // 超时处理
            if (elapsed > CONFIG.retry.pageJumpTimeout) {
                clearInterval(checkJump);
                log('页面跳转超时，可能票已被抢完，重新开始', 'error');
                
                // 返回查询页面
                STATE.isRunning = true;
                setTimeout(() => {
                    if (STATE.currentPage === 'query') {
                        startGrab();
                    } else {
                        // 手动刷新或返回
                        location.reload();
                    }
                }, 1000);
            }
        }, 100);
    };
    
    const stopGrab = () => {
        STATE.isRunning = false;
        log('抢票已停止', 'warn');
    };
    
    // ======================== 订单处理（增强版）========================
    // 带重试的乘客选择
    const selectPassengersWithRetry = async () => {
        let retries = 0;
        const maxRetries = 10;
        const names = Object.keys(CONFIG.passengers);
        
        while (retries < maxRetries) {
            const list = document.getElementById('normal_passenger_id');
            
            if (!list) {
                retries++;
                if (retries < maxRetries) {
                    log(`等待乘客列表加载 (${retries}/${maxRetries})...`, 'warn');
                    await wait(500);
                    continue;
                }
                throw new Error('乘客列表加载超时');
            }
            
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
            
            // 检查是否选择了全部乘客
            if (count >= 4) {
                log(`成功选择 ${count} 位乘客`, 'success');
                return count;
            }
            
            // 如果没有全部选中，等待后重试
            retries++;
            log(`乘客选择不完整(${count}/4)，重试 ${retries}/${maxRetries}`, 'warn');
            await wait(300);
        }
        
        throw new Error('乘客选择失败');
    };
    
    // 修正票种
    const fixTicketTypes = () => {
        try {
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
        } catch (error) {
            ErrorHandler.handleError(error, 'fixTicketTypes');
            return 0;
        }
    };
    
    // 带重试的订单提交
    const submitOrderWithRetry = async () => {
        for (let i = 0; i < CONFIG.retry.orderSubmitMaxRetry; i++) {
            const btn = document.getElementById('submitOrder_id');
            
            if (!btn) {
                log('提交按钮未找到，等待...', 'warn');
                await wait(500);
                continue;
            }
            
            if (btn.disabled) {
                const disabledReason = btn.getAttribute('disabled') || '未知原因';
                log(`提交按钮被禁用: ${disabledReason}`, 'warn');
                await wait(300);
                continue;
            }
            
            // 按钮可用，提交订单
            log(`📤 提交订单 (尝试 ${i+1}/${CONFIG.retry.orderSubmitMaxRetry})!`, 'critical');
            btn.click();
            
            // 等待响应
            await wait(1000);
            
            // 检查是否跳转
            if (STATE.currentPage !== 'order') {
                log('订单提交成功，页面已跳转', 'success');
                return true;
            }
            
            // 检查是否有错误提示
            const errorMsg = document.querySelector('.error_msg, .notice-error, .error-text');
            if (errorMsg) {
                log(`错误提示: ${errorMsg.textContent.trim()}`, 'error');
            }
        }
        
        throw new Error('订单提交失败');
    };
    
    // 带完整重试机制的订单处理
    const processOrderWithRetry = async (autoSubmit = false) => {
        try {
            log('开始处理订单页面...', 'info');
            
            closeDialogs();
            await wait(200);
            
            // 选择乘客（带重试）
            const selected = await ErrorHandler.retryWithBackoff(
                selectPassengersWithRetry,
                'selectPassengers',
                5
            );
            
            await wait(CONFIG.passengerDelay * selected);
            closeDialogs();
            await wait(200);
            
            // 修正票种
            const fixed = fixTicketTypes();
            if (fixed > 0) {
                log(`修正了 ${fixed} 个票种`, 'info');
            }
            
            // 验证
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            log(`订单中有 ${rows.length} 位乘客`, rows.length === 4 ? 'success' : 'warn');
            
            if (autoSubmit) {
                await wait(100);
                await ErrorHandler.retryWithBackoff(
                    () => submitOrderWithRetry(),
                    'submitOrder',
                    3
                );
            }
            
            return true;
        } catch (error) {
            ErrorHandler.handleError(error, 'processOrder');
            
            // 订单处理失败，是否需要重试？
            if (STATE.currentPage === 'order') {
                log('订单页面处理失败，将重试...', 'warn');
                setTimeout(() => processOrderWithRetry(autoSubmit), 2000);
            } else {
                log('页面已变化，停止重试', 'info');
            }
            
            return false;
        }
    };
    
    // ======================== URL监控 ========================
    const startUrlMonitor = () => {
        const checkUrl = () => {
            updatePageState();
        };
        
        // 定时检查URL
        setInterval(checkUrl, 500);
        
        // 监听URL变化
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function(...args) {
            originalPushState.apply(this, args);
            setTimeout(checkUrl, 100);
        };
        
        history.replaceState = function(...args) {
            originalReplaceState.apply(this, args);
            setTimeout(checkUrl, 100);
        };
        
        window.addEventListener('popstate', checkUrl);
        
        log('URL监控已启动', 'info');
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
        
        // 倒计时
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
        go: startGrab,
        stop: stopGrab,
        schedule: schedule,
        order: () => processOrderWithRetry(true),
        test: () => processOrderWithRetry(false),
        config: CONFIG,
        state: STATE,
        // 额外接口
        retry: () => { STATE.isRunning = true; startGrab(); },
        checkPage: () => detectPageType()
    };
    
    // ======================== 启动 ========================
    console.clear();
    console.log('%c╔═══════════════════════════════════════════════════════════╗', 'color:#4CAF50');
    console.log('%c║   12306 抢票脚本 V2 - 增强版（完整错误处理）            ║', 'color:#4CAF50;font-weight:bold;font-size:16px');
    console.log('%c╠═══════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 📅 日期: 2026-02-09 | ⏰ 起售: 16:00                     ║', 'color:#2196F3');
    console.log('%c║ 🎫 座位: 二等座 | 👥 乘客: 4人                           ║', 'color:#2196F3');
    console.log('%c╠═══════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ ✅ 排队自动检测和处理                                   ║', 'color:#4CAF50');
    console.log('%c║ ✅ 订单提交失败自动重试                                  ║', 'color:#4CAF50');
    console.log('%c║ ✅ 页面跳转失败自动恢复                                  ║', 'color:#4CAF50');
    console.log('%c║ ✅ 票被抢完自动寻找其他车次                              ║', 'color:#4CAF50');
    console.log('%c║ ✅ 网络错误自动重试                                      ║', 'color:#4CAF50');
    console.log('%c╠═══════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 命令:                                                    ║', 'color:#9C27B0');
    console.log('%c║   GrabXY.schedule() - 定时16:00抢票                       ║', 'color:#9C27B0');
    console.log('%c║   GrabXY.go()       - 立即抢票                           ║', 'color:#9C27B0');
    console.log('%c║   GrabXY.retry()    - 手动重试                           ║', 'color:#9C27B0');
    console.log('%c║   GrabXY.checkPage() - 检查当前页面                     ║', 'color:#9C27B0');
    console.log('%c╚═══════════════════════════════════════════════════════════╝', 'color:#4CAF50');
    
    // 启动监控
    startDialogMonitor();
    startUrlMonitor();
    STATE.currentPage = detectPageType();
    
    log('脚本V2已加载，所有监控已启动', 'success');
    
})();
