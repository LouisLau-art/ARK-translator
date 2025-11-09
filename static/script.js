'use strict';

const DEFAULT_OUTPUT_MESSAGE = '翻译结果将显示在这里...';
const HISTORY_STORAGE_KEY = 'arkTranslatorHistory';
const MAX_HISTORY_ITEMS = 5;

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const outputText = document.getElementById('outputText');
    const sourceLangSelect = document.getElementById('sourceLang');
    const targetLangSelect = document.getElementById('targetLang');
    const swapBtn = document.getElementById('swapBtn');
    const copyBtn = document.getElementById('copyBtn');
    const copyIcon = document.getElementById('copyIcon');
    const clearBtn = document.getElementById('clearBtn');
    const loading = document.getElementById('loading');
    const statusMessage = document.getElementById('statusMessage');
    const charCount = document.getElementById('charCount');
    const autoTranslate = document.getElementById('autoTranslate');
    const collapseBtn = document.getElementById('collapseBtn');
    const inputSection = document.getElementById('inputSection');
    const outputSection = document.getElementById('outputSection');
    const fontSizeSlider = document.getElementById('fontSizeSlider');
    const fontSizeValue = document.getElementById('fontSizeValue');
    const historyList = document.getElementById('historyList');
    const historyDetails = document.getElementById('historyDetails');

    let isCollapsed = false;
    let copyResetTimer = null;

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

    function rerenderMath() {
        if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
            window.MathJax.typesetPromise([outputText]).catch(err => {
                console.error('MathJax typeset error:', err);
            });
        }
    }

    window.rerenderMath = rerenderMath;

    function updateCharCount() {
        charCount.textContent = textInput.value.length;
    }

    function readHistory() {
        try {
            const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
            const parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? parsed : [];
        } catch (error) {
            console.warn('读取历史记录失败:', error);
            return [];
        }
    }

    function writeHistory(items) {
        try {
            localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(items));
        } catch (error) {
            console.warn('写入历史记录失败:', error);
        }
    }

    function resolveLanguageLabel(selectElement, value) {
        const option = Array.from(selectElement.options).find(opt => opt.value === value);
        return option ? option.textContent : value;
    }

    function formatTimestamp(timestamp) {
        try {
            return new Date(timestamp).toLocaleString();
        } catch (error) {
            return '';
        }
    }

    function renderHistory() {
        const history = readHistory();
        historyList.innerHTML = '';

        if (!history.length) {
            historyList.classList.add('empty');
            const emptyMessage = document.createElement('p');
            emptyMessage.className = 'history-empty';
            emptyMessage.textContent = '暂无历史记录';
            historyList.appendChild(emptyMessage);
            return;
        }

        historyList.classList.remove('empty');

        history.forEach((item, index) => {
            const historyItem = document.createElement('article');
            historyItem.className = 'history-item';

            const header = document.createElement('div');
            header.className = 'history-item-header';
            const meta = document.createElement('span');
            meta.className = 'history-meta';
            meta.textContent = `${item.sourceLangLabel} → ${item.targetLangLabel}`;
            const time = document.createElement('time');
            time.className = 'history-time';
            time.dateTime = item.timestamp;
            time.textContent = formatTimestamp(item.timestamp);
            header.appendChild(meta);
            header.appendChild(time);

            const originalBlock = document.createElement('div');
            originalBlock.className = 'history-text-block';
            const originalLabel = document.createElement('span');
            originalLabel.className = 'history-text-label';
            originalLabel.textContent = '原文';
            const originalText = document.createElement('pre');
            originalText.className = 'history-text';
            originalText.textContent = item.originalText;
            originalBlock.appendChild(originalLabel);
            originalBlock.appendChild(originalText);

            const translatedBlock = document.createElement('div');
            translatedBlock.className = 'history-text-block';
            const translatedLabel = document.createElement('span');
            translatedLabel.className = 'history-text-label';
            translatedLabel.textContent = '译文';
            const translatedText = document.createElement('pre');
            translatedText.className = 'history-text';
            translatedText.textContent = item.translatedText;
            translatedBlock.appendChild(translatedLabel);
            translatedBlock.appendChild(translatedText);

            const actions = document.createElement('div');
            actions.className = 'history-actions';
            const reuseButton = document.createElement('button');
            reuseButton.type = 'button';
            reuseButton.className = 'history-reuse';
            reuseButton.dataset.index = String(index);
            reuseButton.textContent = '再次使用';
            actions.appendChild(reuseButton);

            historyItem.appendChild(header);
            historyItem.appendChild(originalBlock);
            historyItem.appendChild(translatedBlock);
            historyItem.appendChild(actions);

            historyList.appendChild(historyItem);
        });

        historyList.querySelectorAll('.history-reuse').forEach(button => {
            button.addEventListener('click', () => {
                const history = readHistory();
                const item = history[Number(button.dataset.index)];
                if (!item) {
                    return;
                }

                if ([...sourceLangSelect.options].some(opt => opt.value === item.sourceLang)) {
                    sourceLangSelect.value = item.sourceLang;
                }
                if ([...targetLangSelect.options].some(opt => opt.value === item.targetLang)) {
                    targetLangSelect.value = item.targetLang;
                }

                textInput.value = item.originalText;
                updateCharCount();
                historyDetails.open = false;

                if (autoTranslate.checked) {
                    debouncedTranslate();
                } else {
                    statusMessage.textContent = '已填充历史记录内容';
                }
            });
        });
    }

    function saveTranslationHistory(originalText, translatedText, sourceLang, targetLang) {
        const history = readHistory();
        const entry = {
            originalText,
            translatedText,
            sourceLang,
            targetLang,
            sourceLangLabel: resolveLanguageLabel(sourceLangSelect, sourceLang),
            targetLangLabel: resolveLanguageLabel(targetLangSelect, targetLang),
            timestamp: new Date().toISOString()
        };

        history.unshift(entry);
        const trimmed = history.slice(0, MAX_HISTORY_ITEMS);
        writeHistory(trimmed);
        renderHistory();
    }

    async function performTranslation() {
        const text = textInput.value.trim();
        if (!text) {
            outputText.innerHTML = DEFAULT_OUTPUT_MESSAGE;
            statusMessage.textContent = '请输入要翻译的文本';
            rerenderMath();
            return;
        }

        if (!autoTranslate.checked) {
            statusMessage.textContent = '自动翻译已关闭';
            return;
        }

        const sourceLang = sourceLangSelect.value;
        const targetLang = targetLangSelect.value;

        if (sourceLang !== 'auto' && sourceLang === targetLang) {
            outputText.textContent = text;
            statusMessage.textContent = '源语言和目标语言相同';
            rerenderMath();
            return;
        }

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
                    text,
                    sourceLang,
                    targetLang
                })
            });

            const result = await response.json();

            if (response.ok) {
                const translation = result.translation || '';
                outputText.innerHTML = translation || DEFAULT_OUTPUT_MESSAGE;
                rerenderMath();
                statusMessage.textContent = `翻译完成 (${text.length} 字符)`;
                if (translation) {
                    saveTranslationHistory(text, translation, sourceLang, targetLang);
                }
            } else {
                const errorMessage = result.error || '翻译失败';
                outputText.textContent = `错误: ${errorMessage}`;
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

    collapseBtn.addEventListener('click', () => {
        isCollapsed = !isCollapsed;
        inputSection.classList.toggle('collapsed', isCollapsed);
        outputSection.classList.toggle('expanded', isCollapsed);
        collapseBtn.textContent = isCollapsed ? '»' : '«';
        collapseBtn.title = isCollapsed ? '展开输入框' : '折叠输入框';
    });

    textInput.addEventListener('input', () => {
        updateCharCount();
        debouncedTranslate();
    });

    textInput.addEventListener('paste', () => {
        setTimeout(updateCharCount, 10);
        debouncedTranslate();
    });

    sourceLangSelect.addEventListener('change', debouncedTranslate);
    targetLangSelect.addEventListener('change', debouncedTranslate);

    swapBtn.addEventListener('click', () => {
        const sourceValue = sourceLangSelect.value;
        const targetValue = targetLangSelect.value;

        if (sourceValue === 'auto') {
            return;
        }

        sourceLangSelect.value = targetValue;
        targetLangSelect.value = sourceValue;

        if (textInput.value.trim()) {
            debouncedTranslate();
        }
    });

    copyBtn.addEventListener('click', () => {
        const text = outputText.innerText || outputText.textContent;
        if (!text || text === DEFAULT_OUTPUT_MESSAGE || text.startsWith('错误:') || text.startsWith('网络错误:')) {
            return;
        }

        navigator.clipboard.writeText(text).then(() => {
            statusMessage.textContent = '已复制到剪贴板';
            if (copyResetTimer) {
                clearTimeout(copyResetTimer);
            }
            copyIcon.textContent = '✔️';
            copyResetTimer = setTimeout(() => {
                copyIcon.textContent = '📋';
                if (statusMessage.textContent === '已复制到剪贴板') {
                    statusMessage.textContent = '准备就绪';
                }
            }, 1500);
        }).catch(error => {
            console.warn('复制失败:', error);
            statusMessage.textContent = '复制失败';
        });
    });

    clearBtn.addEventListener('click', () => {
        textInput.value = '';
        updateCharCount();
        outputText.innerHTML = DEFAULT_OUTPUT_MESSAGE;
        rerenderMath();
        statusMessage.textContent = '已清空输入与输出';
    });

    autoTranslate.addEventListener('change', () => {
        statusMessage.textContent = autoTranslate.checked ? '自动翻译已启用' : '自动翻译已关闭';
        if (autoTranslate.checked && textInput.value.trim()) {
            debouncedTranslate();
        }
    });

    fontSizeSlider.addEventListener('input', () => {
        const size = fontSizeSlider.value;
        fontSizeValue.textContent = `${size}px`;
        document.documentElement.style.setProperty('--editor-font-size', `${size}px`);
    });

    renderHistory();
    updateCharCount();
    document.documentElement.style.setProperty('--editor-font-size', `${fontSizeSlider.value}px`);
});
