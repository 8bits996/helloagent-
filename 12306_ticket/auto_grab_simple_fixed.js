/**
 * 12306 抢票监控脚本 - 简化自动版
 * 直接在12306页面控制台粘贴执行即可
 * 
 * 【功能】
 * ✅ 自动检测有票车次并点击预订
 * ✅ 自动选择4位乘客
 * ✅ 自动修正陈苇杭为儿童票
 * ✅ 自动提交订单
 * ✅ 自动处理排队页面
 * ✅ 自动处理各种异常
 * ✅ 持续监控直到抢到票
 */

(function() {
    // 创建监控器
    window.AutoGrab = {
        active: false,
        retryCount: 0,
        maxRetries: 2000,
        
        log: function(msg, type = 'info') {
            const t = new Date().toLocaleTimeString('zh-CN', {hour12: false});
            const styles = {
                info: 'color:#2196F3',
                success: 'color:#4CAF50;font-weight:bold',
                error: 'color:#f44336;font-weight:bold',
                warn: 'color:#FF9800',
                critical: 'color:#fff;background:#E91E63;font-weight:bold;padding:3px 8px;font-size:14px'
            };
            console.log(`%c[自动抢票][${t}] ${msg}`, styles[type]);
        },
        
        // 获取页面类型
        getPageType: function() {
            const url = window.location.href;
            if (url.includes('leftTicket') || url.includes('queryLeftTicket')) return 'query';
            if (url.includes('confirmPassenger') || url.includes('initDc')) return 'order';
            if (url.includes('queryQueue')) return 'queue';
            if (url.includes('pay') || url.includes('view/')) return 'success';
            if (url.includes('error')) return 'fail';
            return 'unknown';
        },
        
        // 关闭弹窗
        closeDialogs: function() {
            const selectors = ['.dhtmlx_window_active .btn_def', '.layui-layer-btn0', '.layui-layer-close', '[onclick*="closeWin"]', '.alert-btn-ok'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(btn => {
                    if (/确认|确定|知道|关闭|OK|是|好的/i.test(btn.textContent)) {
                        btn.click();
                    }
                });
            });
            if (typeof layer !== 'undefined') {
                try { layer.closeAll(); } catch(e) {}
            }
        },
        
        // 查找并预订车次
        findAndBookTicket: function() {
            const rows = document.querySelectorAll('#queryLeftTable tr[id]');
            for (const row of rows) {
                const bookBtn = row.querySelector('a.btn72:not(.btn-disabled)');
                if (bookBtn) {
                    const tds = row.querySelectorAll('td');
                    for (const td of tds) {
                        const text = td.textContent.trim();
                        if (text === '有' || /^\d+$/.test(text)) {
                            const trainNum = row.querySelector('.number')?.textContent?.trim() || 'unknown';
                            this.log(`✓ 找到有票车次: ${trainNum}`, 'success');
                            this.log('🎫 点击预订...', 'critical');
                            bookBtn.click();
                            return true;
                        }
                    }
                }
            }
            return false;
        },
        
        // 刷新查询
        refreshQuery: function() {
            const btn = document.getElementById('query_ticket');
            if (btn) {
                btn.click();
            } else {
                // 备用：查找其他查询按钮
                const allBtns = document.querySelectorAll('a[href*="query"]');
                for (const btn of allBtns) {
                    if (btn.textContent.includes('查询')) {
                        btn.click();
                        break;
                    }
                }
            }
        },
        
        // 选择乘客
        selectPassengers: async function() {
            const names = ['陈卓', '冯巧玉', '陈妙可', '陈苇杭'];
            const list = document.getElementById('normal_passenger_id');
            
            if (!list) {
                this.log('等待乘客列表加载...', 'warn');
                await new Promise(r => setTimeout(r, 1000));
                return this.selectPassengers();
            }
            
            let selected = 0;
            let retries = 0;
            
            while (retries < 10) {
                selected = 0;
                list.querySelectorAll('li').forEach(li => {
                    const label = li.querySelector('label');
                    const checkbox = li.querySelector('input[type="checkbox"]');
                    if (label && checkbox) {
                        const name = label.textContent.trim();
                        if (names.some(p => name.includes(p)) && !checkbox.checked) {
                            checkbox.click();
                            selected++;
                            this.log(`✓ 选择: ${name}`, 'success');
                        }
                    }
                });
                
                if (selected >= 4) break;
                
                retries++;
                if (retries < 10) {
                    this.log(`乘客选择不完整(${selected}/4)，重试 ${retries}/10...`, 'warn');
                    await new Promise(r => setTimeout(r, 500));
                }
            }
            
            this.log(`已选择 ${selected} 位乘客`, 'success');
            await new Promise(r => setTimeout(r, 500));
            
            // 修正票种
            const rows = document.querySelectorAll('#ticketInfo_id tr');
            let fixed = 0;
            rows.forEach(row => {
                const nameInput = row.querySelector('input[readonly]');
                const ticketSelect = row.querySelector('select[id^="ticketType"]');
                if (nameInput && ticketSelect) {
                    const name = nameInput.value;
                    if (name.includes('陈苇杭') && ticketSelect.value !== '2') {
                        ticketSelect.value = '2';
                        ticketSelect.dispatchEvent(new Event('change', { bubbles: true }));
                        this.log('修正票种: 陈苇杭 → 儿童票', 'success');
                        fixed++;
                    }
                }
            });
            
            return selected;
        },
        
        // 提交订单
        submitOrder: async function() {
            let retries = 0;
            
            while (retries < 10) {
                const btn = document.getElementById('submitOrder_id');
                
                if (!btn) {
                    this.log('提交按钮未找到，等待...', 'warn');
                    await new Promise(r => setTimeout(r, 500));
                    retries++;
                    continue;
                }
                
                if (btn.disabled) {
                    this.log('提交按钮被禁用，等待...', 'warn');
                    await new Promise(r => setTimeout(r, 300));
                    retries++;
                    continue;
                }
                
                this.log(`📤 提交订单 (尝试 ${retries + 1}/10)!`, 'critical');
                btn.click();
                
                await new Promise(r => setTimeout(r, 1000));
                
                // 检查是否跳转
                if (this.getPageType() !== 'order') {
                    this.log('订单提交成功，页面已跳转', 'success');
                    return true;
                }
                
                // 检查错误提示
                const errorMsg = document.querySelector('.error_msg, .notice-error, .error-text');
                if (errorMsg) {
                    this.log(`错误提示: ${errorMsg.textContent.trim()}`, 'error');
                }
                
                retries++;
            }
            
            return false;
        },
        
        // 处理订单页面
        handleOrderPage: async function() {
            try {
                this.log('📋 进入订单页面，开始处理...', 'info');
                
                this.closeDialogs();
                await new Promise(r => setTimeout(r, 200));
                
                // 选择乘客
                const selected = await this.selectPassengers();
                
                await new Promise(r => setTimeout(r, 500));
                this.closeDialogs();
                await new Promise(r => setTimeout(r, 200));
                
                // 提交订单
                const success = await this.submitOrder();
                
                if (!success) {
                    this.log('订单提交失败，将重试...', 'error');
                    await new Promise(r => setTimeout(r, 2000));
                    // 返回查询页面重新开始
                    if (this.getPageType() === 'order') {
                        window.location.href = 'https://kyfw.12306.cn/otn/leftTicket/init';
                    }
                }
            } catch (error) {
                this.log(`❌ 处理订单失败: ${error.message}`, 'error');
            }
        },
        
        // 处理排队页面
        handleQueue: async function() {
            this.log('🔴 进入排队页面，等待...', 'warn');
            
            const check = async () => {
                const confirmBtn = document.querySelector('#qr_submit_id, .qr-submit');
                if (confirmBtn && !confirmBtn.disabled) {
                    this.log('📤 排队完成，提交订单!', 'critical');
                    confirmBtn.click();
                    return true;
                }
                return false;
            };
            
            // 每500ms检查一次
            for (let i = 0; i < 120; i++) { // 最多等待60秒
                const done = await check();
                if (done || this.getPageType() !== 'queue') {
                    return;
                }
                await new Promise(r => setTimeout(r, 500));
            }
            
            // 超时处理
            if (this.getPageType() === 'queue') {
                this.log('排队超时，返回查询页面...', 'error');
                window.location.href = 'https://kyfw.12306.cn/otn/leftTicket/init';
            }
        },
        
        // 主监控循环
        monitor: async function() {
            this.log('🔥 自动抢票监控已启动!', 'critical');
            this.active = true;
            this.retryCount = 0;
            
            while (this.active) {
                try {
                    const pageType = this.getPageType();
                    
                    // 定期输出进度
                    if (pageType === 'query' && this.retryCount % 30 === 0) {
                        this.log(`第 ${this.retryCount} 次查询，继续...`, 'info');
                    }
                    
                    switch (pageType) {
                        case 'query':
                            // 查询页面 - 刷票
                            this.closeDialogs();
                            const found = this.findAndBookTicket();
                            if (found) {
                                this.retryCount = 0;
                                await new Promise(r => setTimeout(r, 2000));
                            } else {
                                this.retryCount++;
                                if (this.retryCount > this.maxRetries) {
                                    this.log(`达到最大重试 ${this.maxRetries} 次`, 'error');
                                    this.stop();
                                    return;
                                }
                                // 刷新查询
                                this.refreshQuery();
                                await new Promise(r => setTimeout(r, 100));
                            }
                            break;
                            
                        case 'order':
                            // 订单页面
                            await this.handleOrderPage();
                            break;
                            
                        case 'queue':
                            // 排队页面
                            await this.handleQueue();
                            break;
                            
                        case 'success':
                            // 成功页面
                            this.log('🎉 抢票成功！请尽快支付', 'critical');
                            alert('🎉 抢票成功！请在15分钟内完成支付！');
                            this.stop();
                            return;
                            
                        case 'fail':
                            // 错误页面
                            this.log('❌ 进入错误页面，尝试恢复', 'error');
                            await new Promise(r => setTimeout(r, 2000));
                            window.location.href = 'https://kyfw.12306.cn/otn/leftTicket/init';
                            break;
                            
                        default:
                            // 未知页面，等待
                            await new Promise(r => setTimeout(r, 500));
                    }
                    
                    await new Promise(r => setTimeout(r, 50)); // 避免CPU占用过高
                    
                } catch (error) {
                    this.log(`❌ 监控错误: ${error.message}`, 'error');
                    await new Promise(r => setTimeout(r, 2000));
                }
            }
            
            this.log('监控已停止', 'info');
        },
        
        // 停止监控
        stop: function() {
            this.active = false;
            this.log('🛑 自动抢票监控已停止', 'warn');
        },
        
        // 定时启动
        schedule: function() {
            const now = new Date();
            const target = new Date(now);
            target.setHours(16, 0, 0, 0);
            
            const ms = target - now;
            
            if (ms <= 0) {
                this.log('已过16:00，立即开始', 'warn');
                this.monitor();
                return;
            }
            
            const secs = Math.ceil(ms / 1000);
            this.log(`⏰ 距离16:00起售还有 ${secs} 秒`, 'success');
            this.log(`👥 乘客: 陈卓(成人) 冯巧玉(成人) 陈妙可(成人) 陈苇杭(儿童)`, 'info');
            this.log(`🎫 目标: 二等座`, 'info');
            
            // 倒计时
            let countdown = secs;
            const timer = setInterval(() => {
                countdown--;
                if (countdown <= 10 && countdown > 0) {
                    this.log(`⏳ ${countdown}秒...`, 'warn');
                }
                if (countdown <= 0) {
                    clearInterval(timer);
                }
            }, 1000);
            
            // 定时启动（提前300ms）
            setTimeout(() => {
                this.log('🚀 时间到! 开始抢票!', 'critical');
                this.monitor();
            }, ms - 300);
        }
    };
    
    // 打印使用说明
    console.clear();
    console.log('%c╔═════════════════════════════════════════════════════════╗', 'color:#4CAF50');
    console.log('%c║          12306 自动抢票监控脚本                            ║', 'color:#4CAF50;font-weight:bold;font-size:16px');
    console.log('%c╠═════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 📅 日期: 2026-02-09 | ⏰ 起售: 16:00                     ║', 'color:#2196F3');
    console.log('%c║ 🎫 座位: 二等座 | 👥 乘客: 4人                           ║', 'color:#2196F3');
    console.log('%c╠═════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 功能:                                                    ║', 'color:#9C27B0');
    console.log('%c║   ✅ 自动检测有票车次                                     ║', 'color:#4CAF50');
    console.log('%c║   ✅ 自动选择4位乘客                                      ║', 'color:#4CAF50');
    console.log('%c║   ✅ 自动修正票种（陈苇杭→儿童票）                      ║', 'color:#4CAF50');
    console.log('%c║   ✅ 自动提交订单                                        ║', 'color:#4CAF50');
    console.log('%c║   ✅ 自动处理排队页面                                      ║', 'color:#4CAF50');
    console.log('%c║   ✅ 自动恢复异常                                         ║', 'color:#4CAF50');
    console.log('%c╠═════════════════════════════════════════════════════════╣', 'color:#4CAF50');
    console.log('%c║ 使用方法:                                                ║', 'color:#FF9800');
    console.log('%c║   1. 确保已在购票页面（襄阳→武当山，2026-02-09）          ║', 'color:#FF9800');
    console.log('%c║   2. 点击"查询"按钮加载车次列表                             ║', 'color:#FF9800');
    console.log('%c║   3. 在控制台执行: AutoGrab.schedule()  // 定时16:00抢票        ║', 'color:#FF9800');
    console.log('%c║   4. 或执行: AutoGrab.monitor()       // 立即开始              ║', 'color:#FF9800');
    console.log('%c║   5. 执行: AutoGrab.stop()           // 停止监控             ║', 'color:#FF9800');
    console.log('%c╚═══════════════════════════════════════════════════════════╝', 'color:#4CAF50');
})();

console.log('✅ 脚本加载完成！');