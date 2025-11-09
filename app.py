# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import requests
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / 'translator.env')

app = Flask(__name__)

LANGUAGE_MAP = {
    "中文（简体）": "zh",
    "中文（繁体）": "zh-Hant",
    "英语": "en",
    "日语": "ja",
    "韩语": "ko",
    "德语": "de",
    "法语": "fr",
    "西班牙语": "es",
    "意大利语": "it",
    "葡萄牙语": "pt",
    "俄语": "ru",
    "泰语": "th",
    "越南语": "vi",
    "阿拉伯语": "ar",
    "捷克语": "cs",
    "丹麦语": "da",
    "芬兰语": "fi",
    "克罗地亚语": "hr",
    "匈牙利语": "hu",
    "印尼语": "id",
    "马来语": "ms",
    "挪威布克莫尔语": "nb",
    "荷兰语": "nl",
    "波兰语": "pl",
    "罗马尼亚语": "ro",
    "瑞典语": "sv",
    "土耳其语": "tr",
    "乌克兰语": "uk"
}

def ark_translate(text, source_lang, target_lang):
    """
    调用豆包翻译模型API的函数
    - 当 source_lang 为 'auto' 时，不传递 source_language 参数，以使用模型的自动检测功能。
    """
    url = "https://ark.cn-beijing.volces.com/api/v3/responses"
    
    api_key = os.getenv('ARK_API_KEY')
    if not api_key:
        return "错误：请创建translator.env文件并设置ARK_API_KEY环境变量"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    translation_options = {
        "target_language": target_lang
    }
    if source_lang and source_lang != 'auto':
        translation_options["source_language"] = source_lang

    data = {
        "model": "doubao-seed-translation-250915",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text,
                        "translation_options": translation_options
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "output" in result and result.get("output"):
            content_item = result["output"][0].get("content", [])[0]
            if "text" in content_item:
                return content_item["text"]
        
        return f"无法解析翻译结果，API响应: {json.dumps(result)}"
            
    except requests.exceptions.HTTPError as http_err:
        resp = http_err.response
        status_code = resp.status_code if resp else None
        error_message = None

        if resp is not None:
            try:
                error_payload = resp.json()
                error_message = error_payload.get('error', {}).get('message')
            except (json.JSONDecodeError, ValueError, AttributeError):
                error_message = resp.text

        friendly_message = "翻译服务返回错误，请稍后重试。"
        if status_code == 401:
            friendly_message = "认证失败，请检查API密钥配置。"
        elif status_code == 429:
            friendly_message = "请求过于频繁，请稍后再试。"
        elif status_code == 400:
            friendly_message = "请求参数不合法，请检查语言设置。"
        elif status_code == 403:
            friendly_message = "没有权限访问翻译服务，请确认账户权限。"

        detail_part = f" - 详细信息: {error_message}" if error_message else ""
        return f"翻译API错误: {status_code or '未知状态码'} - {friendly_message}{detail_part}"
    except requests.exceptions.Timeout:
        return "翻译请求异常: 请求超时，请稍后再试。"
    except requests.exceptions.RequestException as req_err:
        return f"翻译请求异常: 网络错误，请检查连接。详见: {str(req_err)}"
    except Exception as e:
        return f"翻译请求异常: {str(e)}"

@app.route('/')
def index():
    """
    渲染主页，这里不再返回字符串，而是渲染一个HTML文件。
    """
    return render_template('index.html', languages=LANGUAGE_MAP)

@app.route('/translate', methods=['POST'])
def translate():
    """
    处理翻译请求的API路由。
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('sourceLang', 'auto')
        target_lang = data.get('targetLang', 'zh')

        if len(text) > 10000:
            return jsonify({'error': '输入文本过长，请不要超过10,000个字符'}), 413

        valid_codes = set(LANGUAGE_MAP.values())
        if source_lang != 'auto' and source_lang not in valid_codes:
            return jsonify({'error': '无效的源语言代码'}), 400

        if target_lang not in valid_codes:
            return jsonify({'error': '无效的目标语言代码'}), 400

        if not text:
            return jsonify({'translation': ''})

        translation = ark_translate(text, source_lang, target_lang)
        
        if any(translation.startswith(prefix) for prefix in ["错误：", "翻译错误:", "翻译请求异常:", "翻译API错误:"]):
            return jsonify({'error': translation}), 500
            
        return jsonify({'translation': translation})
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

if __name__ == '__main__':
    if not os.getenv('ARK_API_KEY'):
        print("⚠️  严重错误: 请创建translator.env文件并设置ARK_API_KEY环境变量")
        print("   示例格式: ARK_API_KEY=your_api_key_here")
        print(f"   文件应放置于: {BASE_DIR / 'translator.env'}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
