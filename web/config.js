/**
 * API配置文件
 * 用于管理后端服务地址,方便nginx反向代理配置
 */

const API_CONFIG = {
    // 开发环境: 直接访问后端服务
    development: {
        baseURL: 'http://localhost:8000',
        timeout: 30000
    },
    
    // 生产环境: 通过nginx反向代理
    // nginx配置示例:
    // location /api/ {
    //     proxy_pass http://localhost:8000/api/;
    // }
    production: {
        baseURL: '',  // 空字符串表示使用相对路径,通过nginx代理
        timeout: 30000
    }
};

// 根据当前环境选择配置
// 可以通过URL参数或其他方式判断环境
const ENV = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'development' 
    : 'production';

const API_BASE_URL = API_CONFIG[ENV].baseURL;
const API_TIMEOUT = API_CONFIG[ENV].timeout;

// 导出配置
window.API_CONFIG = {
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    env: ENV
};

console.log(`[API_CONFIG] Environment: ${ENV}, BaseURL: ${API_BASE_URL || '(relative path)'}`);
