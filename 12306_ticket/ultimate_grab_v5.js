/**
 * 12306 终极抢票脚本 V5 - 预填优化版
 * 
 * 核心优化：
 * 1. 支持预填功能 - 提前填写购票信息，起售时自动提交
 * 2. 极速选座 - 并行处理，减少等待时间
 * 3. 智能票种修复 - 自动修正陈妙可为成人票
 * 4. 弹窗自动处理 - 0延迟关闭各种提示
 * 5. 网络请求优化 - 最小化HTTP请求
 * 
 * 使用方法：
 * - 方式1：11:45前使用预填功能，系统自动提交
 * - 方式2：11:45时在查票页面自动执行
 */

(function() {
    'use strict';
    
    // ======================== 配置区 ========================
    const CONFIG = {
        // 目标车次（优先级从高到低）
        targetTrains: ['G3830'],
        
        // 目标座位类型（优先级从高到低）
        seatPriority: ['二等座', '无座', '一等座'],
        
        // 乘客配置（票种：1=成人票, 2=儿童票）
        passengers: {
            '陈卓': { ticketType: '1', priority: 1 },
            '冯巧玉': { ticketType: '1', priority: 2 },
            '陈苇杭': { ticketType: '2', priority: 3 },  // 儿童票
            '陈妙可': { ticketType: '1', priority: 4 }   // 成人票（已满14岁）
        },
        
        // 抢票时间配置
        grabTime: {
            hour: 11,
            minute: 45,
            second: 0,
            preStartMs: 500  // 提前500ms开始
        },
        
        // 性能配置
        performance: {
            queryInterval: 100,      // 查询间隔(ms)
            maxRetries: 50,          // 最大重试次数
            submitDelay: 0,          // 提交延迟(ms)
            usePreFill: true         // 是否使用预填功能
        }
    };
    
    // ======================== 工具函数 ========================
    const Utils = {
        log: (msg, type = 'info') => {
            const styles = {
                info: 'color: #2196F3',
                success: 'color: #4CAF50; font-weight: bold',
                error: 'color: #f44336; font-weight: bold',
                warn: 'color: #FF9800'
            };
            console.log(`%c[抢票V5] ${new Date().toLocaleTimeString()}.${Date.now() % 1000} - ${msg}`, styles[type]);
        },
        
        // 高精度等待
        wait: ms => new Promise(r => setTimeout(r, ms)),
        
        // 等待元素出现
        waitFor: (selector, timeout = 5000) => {
            return new Promise((resolve, reject) => {
                const start = Date.now();
                const check = () => {
                    const el = document.querySelector(selector);
                    if (el) return resolve(el);
                    if (Date.now() - start > timeout) return reject(new Error(`Timeout: ${selector}`));
                    requestAnimationFrame(check);
                };
                check();
            });
        },
        
        // 触发原生事件
        triggerEvent: (el, type) => {
            el.dispatchEvent(new Event(type, { bubbles: true }));
        },
        
        // 获取距离目标时间的毫秒数
        getMsToTarget: () => {
            const now = new Date();
            const target = new Date(now);
            target.setHours(CONFIG.grabTime.hour, CONFIG.grabTime.minute, CONFIG.grabTime.second, 0);
            return target - now;
        },
        
        // 检查是否到抢票时间
        isGrabTime: () => {
            const now = new Date();
            return now.getHours() === CONFIG.grabTime.hour && 
                   now.getMinutes() === CONFIG.grabTime.minute;
        }
    };
    
    // ======================== 预填功能模块 ========================
    const PreFill = {
        // 检查是否有预填入口
        checkPreFillAvailable: () => {
            const preFillBtn = document.querySelector('a[href*="preFill"], .pre-fill-btn, [class*="prefill"]');
            const preFillBanner = Array.from(document.querySelectorAll('*')).find(
                el => el.textContent.includes('购票信息预填') || el.textContent.includes('去填写')
            );
            return preFillBtn || preFillBanner;
        },
        
        // 点击预填按钮
        clickPreFill: () => {
            const btns = document.querySelectorAll('a, button');
            for (const btn of btns) {
                if (btn.textContent.includes('去填写') || btn.textContent.includes('预填')) {
                    Utils.log('找到预填按钮，点击进入', 'success');
                    btn.click();
                    return true;
                }
            }
            return false;
        },
        
        // 在预填页面选择车次
        selectTrainInPreFill: async () => {
            await Utils.wait(500);
            const trainRows = document.querySelectorAll('tr[datatran], .train-item');
            for (const train of CONFIG.targetTrains) {
                for (const row of trainRows) {
                    if (row.textContent.includes(train)) {
                        const checkbox = row.querySelector('input[type="checkbox"], .pre-fill-check');
                        if (checkbox && !checkbox.checked) {
                            checkbox.click();
                            Utils.log(`预填选择车次: ${train}`, 'success');
                        }
                    }
                }
            }
        }
    };
    
    // ======================== 查票页面模块 ========================
    const QueryPage = {
        // 查找目标车次
        findTargetTrain: () => {
            const rows = document.querySelectorAll('#queryLeftTable tr:not(.datatran)');
            for (const train of CONFIG.targetTrains) {
                for (const row of rows) {
                    if (row.id && row.id.includes(train)) {
                        // 检查是否有票
                        for (const seat of CONFIG.seatPriority) {
                            const seatCell = Array.from(row.querySelectorAll('td')).find(td => {
                                const text = td.textContent;
                                return text.includes('有') || /^\d+$/.test(text.trim());
                            });
                            if (seatCell) {
                                Utils.log(`找到可订车次: ${train}`, 'success');
                                return row;
                            }
                        }
                    }
                }
            }
            return null;
        },
        
        // 点击预订按钮
        clickBook: (row) => {
            const bookBtn = row.querySelector('a.btn72');
            if (bookBtn) {
                Utils.log('点击预订按钮', 'info');
                bookBtn.click();
                return true;
            }
            return false;
        },
        
        // 高速刷票
        startFastQuery: () => {
            let retries = 0;
            const query = () => {
                if (retries >= CONFIG.performance.maxRetries) {
                    Utils.log('达到最大重试次数', 'error');
                    return;
                }
                
                // 点击查询
                const queryBtn = document.getElementById('query_ticket');
                if (queryBtn) queryBtn.click();
                
                retries++;
                setTimeout(() => {
                    const train = QueryPage.findTargetTrain();
                    if (train) {
                        QueryPage.clickBook(train);
                    } else {
                        query();
                    }
                }, CONFIG.performance.queryInterval);
            };
            query();
        }
    };
    
    // ======================== 订单页面模块 ========================
    const OrderPage = {
        // 关闭所有弹窗
        closeAllDialogs: () => {
            const closeBtns = document.querySelectorAll(
                '.dhtmlx_window_active .btn_def, .layui-layer-btn0, ' +
                '.modal-footer .btn-primary, [onclick*="closeWin"], ' +
                'a.btn[onclick*="close"], .dhtmlx_wins .btn_def'
            );
            let closed = 0;
            closeBtns.forEach(btn => {
                if (/确认|确定|知道|关闭|OK/i.test(btn.textContent)) {
                    btn.click();
                    closed++;
                }
            });
            
            // 关闭layui弹窗
            if (typeof layer !== 'undefined') {
                try { layer.closeAll(); } catch(e) {}
            }
            
            return closed;
        },
        
        // 选择乘客
        selectPassengers: () => {
            const passengerList = document.getElementById('normal_passenger_id');
            if (!passengerList) return 0;
            
            const names = Object.keys(CONFIG.passengers);
            let selected = 0;
            
            passengerList.querySelectorAll('li').forEach(li => {
                const label = li.querySelector('label');
                const checkbox = li.querySelector('input[type="checkbox"]');
                
                if (label && checkbox) {
                    const name = label.textContent.trim();
                    if (names.some(p => name.includes(p)) && !checkbox.checked) {
                        checkbox.click();
                        selected++;
                        Utils.log(`选择乘客: ${name}`, 'info');
                    }
                }
            });
            
            return selected;
        },
        
        // 修复票种
        fixTicketTypes: () => {
            const fixed = [];
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            
            rows.forEach((row, idx) => {
                const nameInput = row.querySelector('input[readonly]');
                const ticketSelect = row.querySelector('select[id^="ticketType"]');
                
                if (!nameInput || !ticketSelect) return;
                
                const name = nameInput.value;
                for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
                    if (name.includes(pName)) {
                        if (ticketSelect.value !== pConfig.ticketType) {
                            ticketSelect.value = pConfig.ticketType;
                            Utils.triggerEvent(ticketSelect, 'change');
                            fixed.push(`${pName}: ${pConfig.ticketType === '1' ? '成人票' : '儿童票'}`);
                        }
                        break;
                    }
                }
            });
            
            if (fixed.length) {
                Utils.log(`修复票种: ${fixed.join(', ')}`, 'success');
            }
            return fixed;
        },
        
        // 选择席别
        selectSeatType: (targetSeat) => {
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            rows.forEach(row => {
                const seatSelect = row.querySelector('select[id^="seatType"]');
                if (seatSelect) {
                    for (const opt of seatSelect.options) {
                        if (opt.text.includes(targetSeat)) {
                            seatSelect.value = opt.value;
                            Utils.triggerEvent(seatSelect, 'change');
                            break;
                        }
                    }
                }
            });
        },
        
        // 提交订单
        submitOrder: () => {
            const submitBtn = document.getElementById('submitOrder_id');
            if (submitBtn && !submitBtn.disabled) {
                Utils.log('提交订单', 'success');
                submitBtn.click();
                return true;
            }
            return false;
        },
        
        // 完整订单流程
        processOrder: async () => {
            const startTime = performance.now();
            
            // Step 1: 关闭弹窗
            OrderPage.closeAllDialogs();
            
            // Step 2: 等待乘客列表加载
            await Utils.wait(100);
            
            // Step 3: 选择乘客
            OrderPage.selectPassengers();
            
            // Step 4: 等待乘客信息加载
            await Utils.wait(200);
            
            // Step 5: 关闭可能的弹窗
            OrderPage.closeAllDialogs();
            
            // Step 6: 修复票种
            await Utils.wait(100);
            OrderPage.fixTicketTypes();
            
            // Step 7: 选择席别（优先二等座）
            OrderPage.selectSeatType('二等座');
            
            // Step 8: 再次关闭弹窗
            OrderPage.closeAllDialogs();
            
            const elapsed = Math.round(performance.now() - startTime);
            Utils.log(`订单处理完成，耗时: ${elapsed}ms`, 'success');
            
            // Step 9: 提交订单
            if (CONFIG.performance.submitDelay > 0) {
                await Utils.wait(CONFIG.performance.submitDelay);
            }
            
            return OrderPage.submitOrder();
        }
    };
    
    // ======================== 确认页面模块 ========================
    const ConfirmPage = {
        // 处理排队确认
        handleQueue: () => {
            // 自动点击确认按钮
            const confirmBtn = document.querySelector('#qr_submit_id, .btn-confirm-order');
            if (confirmBtn) {
                confirmBtn.click();
                Utils.log('确认排队', 'success');
            }
        }
    };
    
    // ======================== 主控制器 ========================
    const Controller = {
        // 检测当前页面类型
        detectPage: () => {
            const url = location.href;
            if (url.includes('leftTicket') || url.includes('queryLeftTicket')) {
                return 'query';
            } else if (url.includes('confirmPassenger') || url.includes('initDc')) {
                return 'order';
            } else if (url.includes('queryQueue') || url.includes('queueWait')) {
                return 'queue';
            }
            return 'unknown';
        },
        
        // 启动抢票
        start: async () => {
            Utils.log('=== 抢票脚本 V5 启动 ===', 'success');
            
            const pageType = Controller.detectPage();
            Utils.log(`当前页面类型: ${pageType}`, 'info');
            
            switch (pageType) {
                case 'query':
                    // 检查是否有预填功能
                    if (CONFIG.performance.usePreFill && PreFill.checkPreFillAvailable()) {
                        Utils.log('检测到预填功能可用', 'info');
                        PreFill.clickPreFill();
                    } else {
                        QueryPage.startFastQuery();
                    }
                    break;
                    
                case 'order':
                    await OrderPage.processOrder();
                    break;
                    
                case 'queue':
                    ConfirmPage.handleQueue();
                    break;
                    
                default:
                    Utils.log('未知页面，请在查票或订单页面使用', 'warn');
            }
        },
        
        // 定时启动（用于准点抢票）
        scheduleStart: () => {
            const msToTarget = Utils.getMsToTarget();
            
            if (msToTarget <= 0) {
                Utils.log('已过抢票时间，立即执行', 'warn');
                Controller.start();
                return;
            }
            
            Utils.log(`距离抢票时间还有 ${Math.round(msToTarget/1000)} 秒`, 'info');
            
            // 提前一点启动
            const startDelay = msToTarget - CONFIG.grabTime.preStartMs;
            
            setTimeout(() => {
                Utils.log('抢票开始！', 'success');
                Controller.start();
            }, Math.max(0, startDelay));
        },
        
        // 测试模式（用于过期票测试）
        test: async () => {
            Utils.log('=== 测试模式启动 ===', 'success');
            
            const pageType = Controller.detectPage();
            
            if (pageType === 'order') {
                Utils.log('测试订单页面流程', 'info');
                
                // 不实际提交，只处理乘客和票种
                OrderPage.closeAllDialogs();
                await Utils.wait(100);
                const selected = OrderPage.selectPassengers();
                Utils.log(`选择了 ${selected} 位乘客`, 'info');
                
                await Utils.wait(300);
                OrderPage.closeAllDialogs();
                
                await Utils.wait(100);
                const fixed = OrderPage.fixTicketTypes();
                Utils.log(`修复了 ${fixed.length} 个票种`, 'info');
                
                // 验证结果
                const result = Controller.verify();
                Utils.log(`验证结果: ${result.success ? '通过' : '失败'}`, result.success ? 'success' : 'error');
                
                return result;
            }
            
            return { success: false, message: '请在订单页面测试' };
        },
        
        // 验证订单状态
        verify: () => {
            const result = {
                success: true,
                passengers: [],
                errors: []
            };
            
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            rows.forEach(row => {
                const nameInput = row.querySelector('input[readonly]');
                const ticketSelect = row.querySelector('select[id^="ticketType"]');
                
                if (!nameInput || !ticketSelect) return;
                
                const name = nameInput.value;
                const ticketType = ticketSelect.value;
                const typeName = ticketType === '1' ? '成人票' : ticketType === '2' ? '儿童票' : '其他';
                
                result.passengers.push({ name, ticketType, typeName });
                
                // 检查是否符合预期
                for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
                    if (name.includes(pName)) {
                        if (ticketType !== pConfig.ticketType) {
                            result.success = false;
                            result.errors.push(`${pName} 票种错误: 期望 ${pConfig.ticketType === '1' ? '成人票' : '儿童票'}, 实际 ${typeName}`);
                        }
                        break;
                    }
                }
            });
            
            return result;
        }
    };
    
    // ======================== 监控器 ========================
    const Monitor = {
        // 页面变化监控
        observer: null,
        
        // 启动监控
        start: () => {
            // 监控DOM变化，自动处理弹窗
            Monitor.observer = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    if (mutation.addedNodes.length) {
                        // 检查是否有新弹窗
                        mutation.addedNodes.forEach(node => {
                            if (node.nodeType === 1) {
                                if (node.classList?.contains('dhtmlx_window_active') ||
                                    node.classList?.contains('layui-layer')) {
                                    // 自动关闭弹窗
                                    setTimeout(() => OrderPage.closeAllDialogs(), 50);
                                }
                            }
                        });
                    }
                }
            });
            
            Monitor.observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            Utils.log('弹窗监控已启动', 'info');
        },
        
        // 停止监控
        stop: () => {
            if (Monitor.observer) {
                Monitor.observer.disconnect();
                Monitor.observer = null;
            }
        }
    };
    
    // ======================== 全局暴露 ========================
    window.GrabTicketV5 = {
        start: Controller.start,
        test: Controller.test,
        verify: Controller.verify,
        schedule: Controller.scheduleStart,
        config: CONFIG,
        
        // 快捷命令
        go: Controller.start,
        t: Controller.test,
        s: Controller.scheduleStart
    };
    
    // 自动启动监控
    Monitor.start();
    
    // 提示信息
    console.log('%c╔══════════════════════════════════════════╗', 'color: #4CAF50');
    console.log('%c║     12306 抢票脚本 V5 - 预填优化版        ║', 'color: #4CAF50; font-weight: bold');
    console.log('%c╠══════════════════════════════════════════╣', 'color: #4CAF50');
    console.log('%c║ 命令:                                    ║', 'color: #2196F3');
    console.log('%c║   GrabTicketV5.go()     - 立即执行       ║', 'color: #2196F3');
    console.log('%c║   GrabTicketV5.test()   - 测试模式       ║', 'color: #2196F3');
    console.log('%c║   GrabTicketV5.schedule()- 定时抢票      ║', 'color: #2196F3');
    console.log('%c║   GrabTicketV5.verify() - 验证状态       ║', 'color: #2196F3');
    console.log('%c╚══════════════════════════════════════════╝', 'color: #4CAF50');
    
})();
