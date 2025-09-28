from flask import Flask, render_template, request, jsonify
import requests
import os
import json
from dotenv import load_dotenv
import markdown

# 加载.env文件
load_dotenv('translator.env')

app = Flask(__name__)

def ark_translate(text, source_lang, target_lang):
    """
    翻译函数
    """
    url = "https://ark.cn-beijing.volces.com/api/v3/responses"
    
    # 检查API密钥
    api_key = os.getenv('ARK_API_KEY')
    if not api_key:
        return "错误：请设置ARK_API_KEY环境变量"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "doubao-seed-translation-250915",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text,
                        "translation_options": {
                            "source_language": source_lang,
                            "target_language": target_lang
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # 解析响应
        if "output" in result and len(result["output"]) > 0:
            output_item = result["output"][0]
            if "content" in output_item and len(output_item["content"]) > 0:
                content_item = output_item["content"][0]
                if "text" in content_item:
                    translated_text = content_item["text"]
                    html_translation = markdown.markdown(translated_text, extensions=['fenced_code'])
                    return html_translation
        
        return "无法解析翻译结果"
            
    except Exception as e:
        return f"翻译错误: {str(e)}"

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARK豆包翻译器 - 暗黑模式</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --background: #121212;
                --container-bg: #1e1e1e;
                --text-color: #e0e0e0;
                --border-color: #333;
                --primary-color: #667eea;
                --secondary-color: #764ba2;
                --input-bg: #2d2d2d;
                --output-bg: #252525;
                --button-bg: #333;
                --button-hover: #444;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'PingFang SC', 'Noto Sans SC', 'Maple Mono NF CN', sans-serif;
                background: var(--background);
                color: var(--text-color);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }

            .container {
                flex: 1;
                display: flex;
                flex-direction: column;
                max-width: 100%;
                margin: 0;
                background: var(--container-bg);
                overflow: hidden;
            }

            .translation-area {
                display: flex;
                flex: 1;
                min-height: 0; /* 允许容器收缩 */
            }

            .input-section, .output-section {
                flex: 1;
                padding: 20px;
                display: flex;
                flex-direction: column;
            }

            .input-section {
                border-right: 1px solid var(--border-color);
            }

            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border-color);
            }

            .language-selector {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .lang-label {
                font-weight: 600;
                color: var(--text-color);
            }

            select {
                padding: 8px 12px;
                border: 1px solid var(--border-color);
                border-radius: 6px;
                background: var(--input-bg);
                color: var(--text-color);
                font-size: 14px;
                min-width: 120px;
            }

            .swap-btn {
                background: var(--button-bg);
                color: white;
                border: none;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                cursor: pointer;
                font-size: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }

            .swap-btn:hover {
                background: var(--button-hover);
                transform: rotate(180deg);
            }

            .text-area, .output-text {
                flex: 1;
                min-height: 0;
                padding: 15px;
                border: 2px solid var(--border-color);
                border-radius: 8px;
                font-size: 16px;
                line-height: 1.6;
                resize: none;
                font-family: inherit;
                background: var(--input-bg);
                color: var(--text-color);
                /* 💥 确保添加这一行 💥 */
                /* white-space: pre-wrap; */
            }

            .output-text {
                background: var(--output-bg);
                overflow-y: auto;  /* 添加垂直滚动条 */
                /* 如果上一条规则被覆盖，这里也添加 */
                /* white-space: pre-wrap; */
            }

            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: var(--primary-color);
            }

            .loading-spinner {
                border: 3px solid #333;
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .status-bar {
                background: var(--container-bg);
                padding: 15px 30px;
                border-top: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 14px;
                color: var(--text-color);
            }

            .auto-translate {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .switch {
                position: relative;
                display: inline-block;
                width: 50px;
                height: 24px;
            }

            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }

            .slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: var(--button-bg);
                transition: .4s;
                border-radius: 24px;
            }

            .slider:before {
                position: absolute;
                content: "";
                height: 16px;
                width: 16px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }

            input:checked + .slider {
                background-color: var(--primary-color);
            }

            input:checked + .slider:before {
                transform: translateX(26px);
            }

            .char-count {
                color: #999;
                font-size: 12px;
                margin-top: 5px;
            }

            /* Markdown 渲染样式 */
            .output-text h1, .output-text h2, .output-text h3 {
                color: var(--primary-color);
                margin-top: 15px;
                margin-bottom: 8px;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 4px;
            }

            .output-text p {
                margin-bottom: 10px;
            }

            .output-text a {
                color: #4CAF50; /* 绿色链接 */
            }

            .output-text ul, .output-text ol {
                margin-left: 20px;
                padding-left: 10px;
            }

            .output-text code {
                background: #3a3a3a; /* 代码背景 */
                padding: 2px 4px;
                border-radius: 4px;
                font-size: 90%;
                color: #ffcc66; /* 代码高亮色 */
                font-family: 'Consolas', 'Monaco', monospace;
            }

            .output-text pre {
                background: #000;
                padding: 10px;
                border-radius: 6px;
                overflow-x: auto;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            .output-text pre code {
                background: none;
                padding: 0;
                color: #d4d4d4;
                font-size: 100%;
            }
        </style>
    </head>
    <body>
        <div class="container">
            
            <div class="translation-area">
                <div class="input-section">
                    <div class="section-header">
                        <div class="language-selector">
                            <span class="lang-label">源语言:</span>
                            <select id="sourceLang">
                                <option value="auto">自动检测</option>
                                <option value="zh">中文</option>
                                <option value="en">英文</option>
                            </select>
                        </div>
                        <button type="button" id="swapBtn" class="swap-btn" title="交换语言">⇄</button>
                    </div>
                    <textarea 
                        id="textInput" 
                        class="text-area" 
                        placeholder="请输入要翻译的文本...&#10;&#10;提示：输入文本后会自动翻译，无需点击按钮"
                        autofocus
                    ></textarea>
                    <div class="char-count">
                        <span id="charCount">0</span> 字符
                    </div>
                </div>
                
                <div class="output-section">
                    <div class="section-header">
                        <div class="language-selector">
                            <span class="lang-label">目标语言:</span>
                            <select id="targetLang">
                                <option value="en">英文</option>
                                <option value="zh" selected>中文</option>
                            </select>
                        </div>
                        <button type="button" id="copyBtn" class="swap-btn" title="复制翻译结果">📋</button>
                    </div>
                    <div id="outputText" class="output-text">
                        翻译结果将显示在这里...
                    </div>
                </div>
            </div>
            
            <div id="loading" class="loading">
                <div class="loading-spinner"></div>
                <div>翻译中...</div>
            </div>
            
            <div class="status-bar">
                <div class="auto-translate">
                    <label>
                        <span>自动翻译</span>
                        <div class="switch">
                            <input type="checkbox" id="autoTranslate" checked>
                            <span class="slider"></span>
                        </div>
                    </label>
                </div>
                <div id="statusMessage">准备就绪</div>
            </div>
        </div>

        <script>
            // 防抖函数
            function debounce(func, wait) {
                let timeout;
                return function executedFunction(...args) {
                    const later = () => {
                        clearTimeout(timeout);
                        func(...args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            }

            // 更新字符计数
            function updateCharCount() {
                const text = textInput.value;
                charCount.textContent = text.length;
            }

            // 翻译函数
            async function performTranslation() {
                const text = textInput.value.trim();
                if (!text) {
                    outputText.innerHTML = "翻译结果将显示在这里...";
                    statusMessage.textContent = "请输入要翻译的文本";
                    return;
                }

                if (!autoTranslate.checked) {
                    statusMessage.textContent = "自动翻译已关闭";
                    return;
                }

                const sourceLang = sourceLangSelect.value;
                const targetLang = targetLangSelect.value;

                // 显示加载状态
                loading.style.display = 'block';
                outputText.textContent = '';
                statusMessage.textContent = '翻译中...';

                try {
                    const response = await fetch('/translate', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({ 
                            text: text, 
                            sourceLang: sourceLang, 
                            targetLang: targetLang 
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        outputText.innerHTML = result.translation;
                        statusMessage.textContent = `翻译完成 (${text.length} 字符)`;
                    } else {
                        outputText.textContent = `错误: ${result.error}`;
                        statusMessage.textContent = '翻译失败';
                    }
                    
                } catch (error) {
                    outputText.textContent = `网络错误: ${error.message}`;
                    statusMessage.textContent = '连接失败';
                } finally {
                    loading.style.display = 'none';
                }
            }

            const debouncedTranslate = debounce(performTranslation, 500);

            // 元素引用
            const textInput = document.getElementById('textInput');
            const outputText = document.getElementById('outputText');
            const sourceLangSelect = document.getElementById('sourceLang');
            const targetLangSelect = document.getElementById('targetLang');
            const swapBtn = document.getElementById('swapBtn');
            const copyBtn = document.getElementById('copyBtn');
            const loading = document.getElementById('loading');
            const statusMessage = document.getElementById('statusMessage');
            const charCount = document.getElementById('charCount');
            const autoTranslate = document.getElementById('autoTranslate');

            // 事件监听器
            textInput.addEventListener('input', function() {
                updateCharCount();
                debouncedTranslate();
            });

            textInput.addEventListener('paste', function() {
                setTimeout(updateCharCount, 10);
            });

            sourceLangSelect.addEventListener('change', debouncedTranslate);
            targetLangSelect.addEventListener('change', debouncedTranslate);

            swapBtn.addEventListener('click', function() {
                const sourceLang = sourceLangSelect.value;
                const targetLang = targetLangSelect.value;
                
                if (targetLang !== 'auto') {
                    const temp = sourceLang;
                    sourceLangSelect.value = targetLang === 'auto' ? 'zh' : targetLang;
                    targetLangSelect.value = temp === 'auto' ? 'zh' : temp;
                    
                    if (textInput.value.trim()) {
                        debouncedTranslate();
                    }
                }
            });

            copyBtn.addEventListener('click', function() {
                // 获取纯文本内容（去掉HTML标签）
                const text = outputText.innerText || outputText.textContent;  // 使用 innerText 获取可见文本
                if (text && text !== '翻译结果将显示在这里...' && !text.startsWith('错误:') && !text.startsWith('网络错误:')) {
                    navigator.clipboard.writeText(text).then(() => {
                        statusMessage.textContent = '已复制到剪贴板';
                        setTimeout(() => {
                            if (textInput.value.trim()) {
                                statusMessage.textContent = '准备就绪';
                            }
                        }, 2000);
                    });
                }
            });

            autoTranslate.addEventListener('change', function() {
                statusMessage.textContent = autoTranslate.checked ? '自动翻译已启用' : '自动翻译已关闭';
                if (autoTranslate.checked && textInput.value.trim()) {
                    debouncedTranslate();
                }
            });

            // 初始化字符计数
            updateCharCount();
        </script>
    </body>
    </html>
    '''

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('sourceLang', 'auto')
        target_lang = data.get('targetLang', 'zh')
        
        if not text:
            return jsonify({'error': '请输入要翻译的文本'}), 400
        
        # 自动检测语言
        if source_lang == 'auto':
            # 简单中文检测
            if any('\u4e00' <= char <= '\u9fff' for char in text):
                source_lang = 'zh'
            else:
                source_lang = 'en'
        
        translation = ark_translate(text, source_lang, target_lang)
        
        # 检查翻译结果是否包含API错误信息
        if translation.startswith("错误：") or translation.startswith("翻译错误:"):
            return jsonify({'error': translation}), 500
            
        return jsonify({'translation': translation})
        
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

if __name__ == '__main__':
    # 检查环境变量
    api_key = os.getenv('ARK_API_KEY')
    if api_key:
        print(f"✅ API Key已加载: {api_key[:10]}...")
    else:
        print("⚠️  警告: 请设置ARK_API_KEY环境变量")
    
    app.run(debug=True, host='127.0.0.1', port=5000)