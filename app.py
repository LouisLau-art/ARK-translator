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
        try:
            error_details = response.json()
            return f"翻译API错误: {http_err} - {error_details.get('error', {}).get('message', '未知错误')}"
        except json.JSONDecodeError:
            return f"翻译API错误: {http_err} - 响应内容不是有效的JSON"
    except Exception as e:
        return f"翻译请求异常: {str(e)}"

@app.route('/')
def index():
    """
    渲染主页，这里不再返回字符串，而是渲染一个HTML文件。
    """
    return render_template('index.html')

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
