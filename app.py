# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import requests
import os
import json
import re
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

# Constants for the translation model limits
MAX_INPUT_TOKENS = 1000  # Maximum input tokens for the model (approx 4,000 characters)
CHUNK_OVERLAP = 100      # Overlap between chunks to maintain context

# Regex patterns for Markdown structure detection
HEADING_PATTERN = re.compile(r'^(#+)\s*(.*)$', re.MULTILINE)
CODE_BLOCK_PATTERN = re.compile(r'^(```.*?^```)$', re.DOTALL | re.MULTILINE)

LIST_ITEM_PATTERN = re.compile(r'^(\s*)([-+*]\s+|\d+\.\s+)(.*)$', re.MULTILINE)
BLOCKQUOTE_PATTERN = re.compile(r'^(>\s*.*)$', re.MULTILINE)

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

def split_markdown(text):
    """
    Split long Markdown text into manageable chunks while preserving the structure.
    
    The splitting strategy:
    1. Code blocks are kept intact as single chunks
    2. Heading structures start new chunks to maintain context
    3. Paragraphs are split at empty lines
    4. Chunks are kept under the model's token limit with some buffer
    """
    chunks = []
    
    # First extract all code blocks
    code_blocks = list(CODE_BLOCK_PATTERN.finditer(text))
    
    if code_blocks:
        # Process content between code blocks
        prev_end = 0
        for code_match in code_blocks:
            before_code = text[prev_end:code_match.start()]
            
            # Split and process the content before the code block
            if before_code.strip():
                # Split non-code content by empty lines to get paragraphs
                paragraphs = before_code.split('\n\n')
                current_chunk = []
                
                for para in paragraphs:
                    if not para:
                        continue
                        
                    potential_chunk = current_chunk + [para] if current_chunk else [para]
                    potential_len = len('\n\n'.join(potential_chunk))
                    
                    # Check if it's a heading - start new chunk
                    if HEADING_PATTERN.match(para):
                        if current_chunk:  # If we have existing content, save it
                            chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [para]  # New chunk starts with this heading
                    
                    # Check if potential chunk is within size limit
                    elif potential_len < MAX_INPUT_TOKENS - CHUNK_OVERLAP:
                        current_chunk = potential_chunk
                    
                    else:
                        if current_chunk:
                            chunks.append('\n\n'.join(current_chunk))
                        current_chunk = [para]
                
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
            
            # Add the code block as a single chunk
            chunks.append(code_match.group())
            prev_end = code_match.end()
        
        # Process content after the last code block
        after_code = text[prev_end:]
        if after_code.strip():
            paragraphs = after_code.split('\n\n')
            current_chunk = []
            
            for para in paragraphs:
                if not para:
                    continue
                    
                potential_chunk = current_chunk + [para] if current_chunk else [para]
                potential_len = len('\n\n'.join(potential_chunk))
                
                if HEADING_PATTERN.match(para):
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                
                elif potential_len < MAX_INPUT_TOKENS - CHUNK_OVERLAP:
                    current_chunk = potential_chunk
                
                else:
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
            
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
    
    else:
        # No code blocks, split by paragraphs and headings
        paragraphs = text.split('\n\n')
        current_chunk = []
        
        for para in paragraphs:
            if not para:
                continue
                
            potential_chunk = current_chunk + [para] if current_chunk else [para]
            potential_len = len('\n\n'.join(potential_chunk))
            
            if HEADING_PATTERN.match(para):
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                
            elif potential_len < MAX_INPUT_TOKENS - CHUNK_OVERLAP:
                current_chunk = potential_chunk
                
            else:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
    
    # Clean up and ensure chunks are properly formatted
    clean_chunks = []
    for chunk in chunks:
        stripped = chunk.strip()
        if stripped:
            clean_chunks.append(stripped)
    
    return clean_chunks

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

        # Remove the 10,000 character limit since we now support splitting
        # if len(text) > 10000:
        #     return jsonify({'error': '输入文本过长，请不要超过10,000个字符'}), 413

        valid_codes = set(LANGUAGE_MAP.values())
        if source_lang != 'auto' and source_lang not in valid_codes:
            return jsonify({'error': '无效的源语言代码'}), 400

        if target_lang not in valid_codes:
            return jsonify({'error': '无效的目标语言代码'}), 400

        if not text:
            return jsonify({'translation': ''})

        # Split the Markdown into chunks
        markdown_chunks = split_markdown(text)
        
        # Translate each chunk individually
        translated_chunks = []
        for chunk in markdown_chunks:
            translated_chunk = ark_translate(chunk, source_lang, target_lang)
            
            # Check if translation failed for this chunk
            if any(translated_chunk.startswith(prefix) for prefix in ["错误：", "翻译API错误:", "翻译请求异常:"]):
                return jsonify({'error': translated_chunk}), 500
            
            translated_chunks.append(translated_chunk)
        
        # Merge the translated chunks back together
        translation = '\n\n'.join(translated_chunks)
        
        return jsonify({'translation': translation})
        
    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500

if __name__ == '__main__':
    if not os.getenv('ARK_API_KEY'):
        print("⚠️  严重错误: 请创建translator.env文件并设置ARK_API_KEY环境变量")
        print("   示例格式: ARK_API_KEY=your_api_key_here")
        print(f"   文件应放置于: {BASE_DIR / 'translator.env'}")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
