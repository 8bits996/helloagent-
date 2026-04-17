/**
 * 12306 终极抢票脚本 V6 - 最终优化版
 * 
 * 【重要发现】
 * 1. 预填功能限制：预填页面无法修改票种（陈妙可默认儿童票）
 * 2. 必须在订单确认页面修改票种为成人票
 * 3. 建议：11:45前使用预填功能预选车次和乘客，开售后自动触发购票流程
 * 
 * 【优化策略】
 * - 方式A: 使用预填功能（推荐）- 提前完成信息填写，开售时快速提交
 * - 方式B: 传统脚本方式 - 在查票页面刷票，进入订单页面后自动处理
 * 
 * 【已测试验证】
 * ✅ 乘客选择正确
 * ✅ 票种修复功能正常（陈妙可 儿童票→成人票）
 * ✅ 弹窗自动关闭
 * ✅ 提交订单流程
 */

(function() {
    'use strict';
    
    // ======================== 配置区 ========================
    const CONFIG = {
        // 目标车次（优先级从高到低）
        targetTrains: ['G1156', 'G3830', 'G1136'],
        
        // 目标座位类型（优先级从高到低）  
        seatPriority: ['二等座', '无座', '一等座'],
        
        // 乘客配置（票种：1=成人票, 2=儿童票）
        // ⚠️ 关键：陈妙可已满14岁，必须使用成人票
        passengers: {
            '陈卓': { ticketType: '1', typeName: '成人票', priority: 1 },
            '冯巧玉': { ticketType: '1', typeName: '成人票', priority: 2 },
            '陈苇杭': { ticketType: '2', typeName: '儿童票', priority: 3 },
            '陈妙可': { ticketType: '1', typeName: '成人票', priority: 4 }  // 已满14岁
        },
        
        // 抢票时间配置（广州站 11:45 起售）
        grabTime: {
            hour: 11,
            minute: 45,
            second: 0,
            preStartMs: 300  // 提前300ms开始
        },
        
        // 性能配置
        performance: {
            queryInterval: 80,       // 查询间隔(ms)，更激进
            maxRetries: 100,         // 最大重试次数
            submitDelay: 0,          // 提交延迟(ms)
            dialogCloseDelay: 30,    // 弹窗关闭延迟(ms)
            passengerSelectDelay: 50 // 乘客选择后延迟(ms)
        }
    };
    
    // ======================== 日志模块 ========================
    const Logger = {
        log: (msg, type = 'info') => {
            const styles = {
                info: 'color: #2196F3; font-size: 12px',
                success: 'color: #4CAF50; font-weight: bold; font-size: 14px',
                error: 'color: #f44336; font-weight: bold',
                warn: 'color: #FF9800',
                critical: 'color: #fff; background: #f44336; font-weight: bold; padding: 2px 6px'
            };
            const time = new Date().toLocaleTimeString() + '.' + String(Date.now() % 1000).padStart(3, '0');
            console.log(`%c[V6] ${time} - ${msg}`, styles[type]);
        }
    };
    
    // ======================== 工具函数 ========================
    const Utils = {
        wait: ms => new Promise(r => setTimeout(r, ms)),
        
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
        
        trigger: (el, type) => {
            el.dispatchEvent(new Event(type, { bubbles: true }));
        },
        
        getMsToTarget: () => {
            const now = new Date();
            const target = new Date(now);
            target.setHours(CONFIG.grabTime.hour, CONFIG.grabTime.minute, CONFIG.grabTime.second, 0);
            return target - now;
        }
    };
    
    // ======================== 弹窗处理模块 ========================
    const DialogHandler = {
        // 关闭所有弹窗（极速版）
        closeAll: () => {
            let closed = 0;
            
            // 常见弹窗按钮选择器
            const selectors = [
                '.dhtmlx_window_active .btn_def',
                '.dhtmlx_wins .btn_def',
                '.layui-layer-btn0',
                '.layui-layer-close',
                '.modal-footer .btn-primary',
                '[onclick*="closeWin"]',
                '.alert-btn-ok'
            ];
            
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(btn => {
                    if (/确认|确定|知道|关闭|OK|是/i.test(btn.textContent)) {
                        btn.click();
                        closed++;
                    }
                });
            });
            
            // 关闭layui弹窗
            if (typeof layer !== 'undefined') {
                try { layer.closeAll(); closed++; } catch(e) {}
            }
            
            return closed;
        },
        
        // 监控新弹窗并自动关闭
        startMonitor: () => {
            const observer = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) {
                            const isDialog = node.classList?.contains('dhtmlx_window_active') ||
                                           node.classList?.contains('layui-layer') ||
                                           node.classList?.contains('modal');
                            if (isDialog) {
                                setTimeout(() => DialogHandler.closeAll(), CONFIG.performance.dialogCloseDelay);
                            }
                        }
                    });
                }
            });
            
            observer.observe(document.body, { childList: true, subtree: true });
            Logger.log('弹窗监控已启动', 'info');
            return observer;
        }
    };
    
    // ======================== 订单页面处理模块 ========================
    const OrderHandler = {
        // 选择乘客
        selectPassengers: () => {
            const passengerList = document.getElementById('normal_passenger_id');
            if (!passengerList) {
                Logger.log('未找到乘客列表', 'error');
                return 0;
            }
            
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
                    }
                }
            });
            
            Logger.log(`选择了 ${selected} 位乘客`, selected > 0 ? 'success' : 'warn');
            return selected;
        },
        
        // 修复票种（关键功能！）
        fixTicketTypes: () => {
            const fixed = [];
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            
            rows.forEach(row => {
                const nameInput = row.querySelector('input[readonly]');
                const ticketSelect = row.querySelector('select[id^="ticketType"]');
                
                if (!nameInput || !ticketSelect) return;
                
                const name = nameInput.value;
                for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
                    if (name.includes(pName)) {
                        const expectedType = pConfig.ticketType;
                        if (ticketSelect.value !== expectedType) {
                            const oldType = ticketSelect.value === '1' ? '成人票' : '儿童票';
                            ticketSelect.value = expectedType;
                            Utils.trigger(ticketSelect, 'change');
                            fixed.push(`${pName}: ${oldType} → ${pConfig.typeName}`);
                            Logger.log(`修复票种: ${pName} → ${pConfig.typeName}`, 'success');
                        }
                        break;
                    }
                }
            });
            
            return fixed;
        },
        
        // 验证乘客和票种
        verify: () => {
            const result = { success: true, passengers: [], errors: [] };
            
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            rows.forEach(row => {
                const nameInput = row.querySelector('input[readonly]');
                const ticketSelect = row.querySelector('select[id^="ticketType"]');
                
                if (!nameInput || !ticketSelect) return;
                
                const name = nameInput.value;
                const ticketType = ticketSelect.value;
                const typeName = ticketType === '1' ? '成人票' : ticketType === '2' ? '儿童票' : '其他';
                
                result.passengers.push({ name, ticketType, typeName });
                
                for (const [pName, pConfig] of Object.entries(CONFIG.passengers)) {
                    if (name.includes(pName)) {
                        if (ticketType !== pConfig.ticketType) {
                            result.success = false;
                            result.errors.push(`${pName}: 期望${pConfig.typeName}, 实际${typeName}`);
                        }
                        break;
                    }
                }
            });
            
            return result;
        },
        
        // 提交订单
        submit: () => {
            const submitBtn = document.getElementById('submitOrder_id');
            if (submitBtn && !submitBtn.disabled) {
                Logger.log('提交订单!', 'critical');
                submitBtn.click();
                return true;
            }
            Logger.log('提交按钮不可用', 'error');
            return false;
        },
        
        // 完整订单处理流程
        process: async (autoSubmit = false) => {
            const startTime = performance.now();
            Logger.log('开始处理订单页面...', 'info');
            
            // Step 1: 关闭可能存在的弹窗
            DialogHandler.closeAll();
            
            // Step 2: 等待页面加载
            await Utils.wait(100);
            
            // Step 3: 选择乘客
            const selected = OrderHandler.selectPassengers();
            
            // Step 4: 等待乘客信息加载
            await Utils.wait(CONFIG.performance.passengerSelectDelay * selected);
            
            // Step 5: 再次关闭弹窗（选择乘客后可能出现提示）
            DialogHandler.closeAll();
            await Utils.wait(100);
            
            // Step 6: 修复票种（关键！）
            const fixed = OrderHandler.fixTicketTypes();
            
            // Step 7: 验证
            const verifyResult = OrderHandler.verify();
            
            const elapsed = Math.round(performance.now() - startTime);
            
            if (verifyResult.success) {
                Logger.log(`✓ 订单处理完成，耗时: ${elapsed}ms`, 'success');
                Logger.log(`  乘客: ${verifyResult.passengers.map(p => `${p.name}(${p.typeName})`).join(', ')}`, 'info');
            } else {
                Logger.log(`✗ 验证失败: ${verifyResult.errors.join('; ')}`, 'error');
            }
            
            // Step 8: 提交订单
            if (autoSubmit && verifyResult.success) {
                if (CONFIG.performance.submitDelay > 0) {
                    await Utils.wait(CONFIG.performance.submitDelay);
                }
                return OrderHandler.submit();
            }
            
            return verifyResult;
        }
    };
    
    // ======================== 预填功能模块 ========================
    const PreFillHandler = {
        // 检测是否在预填相关页面
        isPreFillPage: () => {
            return location.href.includes('prefill');
        },
        
        // 点击"按预填信息购票"按钮
        clickPreFillBuy: () => {
            const btns = document.querySelectorAll('a, button');
            for (const btn of btns) {
                if (btn.textContent.includes('按预填信息购票')) {
                    Logger.log('点击"按预填信息购票"', 'success');
                    btn.click();
                    return true;
                }
            }
            return false;
        }
    };
    
    // ======================== 查票页面模块 ========================
    const QueryHandler = {
        // 查找有票的目标车次
        findAvailableTrain: () => {
            const rows = document.querySelectorAll('#queryLeftTable tr');
            
            for (const train of CONFIG.targetTrains) {
                for (const row of rows) {
                    if (!row.id || !row.id.includes(train)) continue;
                    
                    // 检查是否有票
                    const cells = row.querySelectorAll('td');
                    for (const cell of cells) {
                        const text = cell.textContent.trim();
                        if (text === '有' || /^\d+$/.test(text)) {
                            Logger.log(`找到有票车次: ${train}`, 'success');
                            return row;
                        }
                    }
                }
            }
            return null;
        },
        
        // 点击预订
        clickBook: (row) => {
            const bookBtn = row.querySelector('a.btn72, a[onclick*="reserve"]');
            if (bookBtn) {
                Logger.log('点击预订按钮', 'info');
                bookBtn.click();
                return true;
            }
            return false;
        },
        
        // 高速刷票循环
        startFastQuery: () => {
            let retries = 0;
            
            const query = () => {
                if (retries >= CONFIG.performance.maxRetries) {
                    Logger.log('达到最大重试次数', 'error');
                    return;
                }
                
                // 查找目标车次
                const train = QueryHandler.findAvailableTrain();
                if (train) {
                    QueryHandler.clickBook(train);
                    return;
                }
                
                // 刷新查询
                const queryBtn = document.getElementById('query_ticket');
                if (queryBtn) queryBtn.click();
                
                retries++;
                setTimeout(query, CONFIG.performance.queryInterval);
            };
            
            Logger.log('开始高速刷票...', 'info');
            query();
        }
    };
    
    // ======================== 主控制器 ========================
    const Controller = {
        // 检测页面类型
        detectPage: () => {
            const url = location.href;
            if (url.includes('prefill_order')) return 'prefill_order';
            if (url.includes('prefill')) return 'prefill';
            if (url.includes('leftTicket') || url.includes('queryLeftTicket')) return 'query';
            if (url.includes('confirmPassenger') || url.includes('initDc')) return 'order';
            if (url.includes('queryQueue')) return 'queue';
            return 'unknown';
        },
        
        // 启动
        start: async (autoSubmit = false) => {
            Logger.log('=== 抢票脚本 V6 启动 ===', 'critical');
            
            const pageType = Controller.detectPage();
            Logger.log(`当前页面: ${pageType}`, 'info');
            
            switch (pageType) {
                case 'prefill_order':
                    // 预填订单页面 - 等待开售后点击购票按钮
                    Logger.log('预填订单页面 - 等待开售时点击"按预填信息购票"', 'info');
                    PreFillHandler.clickPreFillBuy();
                    break;
                    
                case 'prefill':
                    Logger.log('预填页面 - 请完成预填设置后等待开售', 'info');
                    break;
                    
                case 'query':
                    // 传统方式 - 刷票
                    QueryHandler.startFastQuery();
                    break;
                    
                case 'order':
                    // 订单页面 - 处理乘客和票种
                    await OrderHandler.process(autoSubmit);
                    break;
                    
                case 'queue':
                    // 排队页面
                    const confirmBtn = document.querySelector('#qr_submit_id');
                    if (confirmBtn) confirmBtn.click();
                    break;
                    
                default:
                    Logger.log('未知页面类型', 'warn');
            }
        },
        
        // 测试模式（不提交）
        test: async () => {
            Logger.log('=== 测试模式 ===', 'info');
            
            if (Controller.detectPage() === 'order') {
                const result = await OrderHandler.process(false);
                return result;
            }
            
            return { success: false, message: '请在订单页面测试' };
        },
        
        // 定时启动
        schedule: () => {
            const msToTarget = Utils.getMsToTarget();
            
            if (msToTarget <= 0) {
                Logger.log('已过目标时间，立即执行', 'warn');
                Controller.start(true);
                return;
            }
            
            const seconds = Math.round(msToTarget / 1000);
            Logger.log(`距离 ${CONFIG.grabTime.hour}:${String(CONFIG.grabTime.minute).padStart(2,'0')} 还有 ${seconds} 秒`, 'info');
            
            setTimeout(() => {
                Logger.log('🚀 开始抢票!', 'critical');
                Controller.start(true);
            }, Math.max(0, msToTarget - CONFIG.grabTime.preStartMs));
        }
    };
    
    // ======================== 全局暴露 ========================
    window.GrabV6 = {
        start: () => Controller.start(true),    // 启动并自动提交
        test: Controller.test,                   // 测试模式
        schedule: Controller.schedule,           // 定时启动
        verify: OrderHandler.verify,             // 验证状态
        fix: OrderHandler.fixTicketTypes,        // 手动修复票种
        config: CONFIG,
        
        // 快捷命令
        go: () => Controller.start(true),
        t: Controller.test,
        s: Controller.schedule,
        v: OrderHandler.verify
    };
    
    // 启动弹窗监控
    DialogHandler.startMonitor();
    
    // 打印使用说明
    console.log('%c╔═══════════════════════════════════════════════════════════════╗', 'color: #4CAF50');
    console.log('%c║           12306 抢票脚本 V6 - 最终优化版                       ║', 'color: #4CAF50; font-weight: bold');
    console.log('%c╠═══════════════════════════════════════════════════════════════╣', 'color: #4CAF50');
    console.log('%c║ 快捷命令:                                                      ║', 'color: #2196F3');
    console.log('%c║   GrabV6.go()       - 立即执行（自动提交）                     ║', 'color: #2196F3');
    console.log('%c║   GrabV6.test()     - 测试模式（不提交）                       ║', 'color: #2196F3');
    console.log('%c║   GrabV6.schedule() - 定时 11:45 执行                          ║', 'color: #2196F3');
    console.log('%c║   GrabV6.verify()   - 验证当前订单状态                         ║', 'color: #2196F3');
    console.log('%c║   GrabV6.fix()      - 手动修复票种                             ║', 'color: #2196F3');
    console.log('%c╠═══════════════════════════════════════════════════════════════╣', 'color: #4CAF50');
    console.log('%c║ 乘客配置:                                                      ║', 'color: #FF9800');
    console.log('%c║   陈卓 - 成人票 | 冯巧玉 - 成人票                              ║', 'color: #FF9800');
    console.log('%c║   陈苇杭 - 儿童票 | 陈妙可 - 成人票 ⚠️(已满14岁)               ║', 'color: #FF9800');
    console.log('%c╚═══════════════════════════════════════════════════════════════╝', 'color: #4CAF50');
    
})();
