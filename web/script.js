/* ============================================
   REDBOOK MONITOR / SENTIMENT ANALYSIS SYSTEM
   ============================================ */

(function() {
    'use strict';

    let currentNotes = [];
    let currentNoteIndex = 0;
    let currentKeyword = '';
    let currentCommentPage = 1;
    let currentComments = [];
    let statsRefreshTimer = null;
    let commentsPerPage = 20; // 默认每页20条,可通过选择器修改
    const STATS_REFRESH_INTERVAL = 10000; // 10秒

    const elements = {
        keywordInput: document.getElementById('keywordInput'),
        keywordDropdown: document.getElementById('keywordDropdown'),
        searchBtn: document.getElementById('searchBtn'),
        noteCard: document.getElementById('noteCard'),
        commentsContainer: document.getElementById('commentsContainer'),
        prevNote: document.getElementById('prevNote'),
        nextNote: document.getElementById('nextNote'),
        totalNotes: document.getElementById('totalNotes'),
        totalComments: document.getElementById('totalComments'),
        crawlTime: document.getElementById('crawlTime'),
        currentKeyword: document.getElementById('currentKeyword'),
        noteIndex: document.getElementById('noteIndex'),
        commentCount: document.getElementById('commentCount'),
        statusMarquee: document.getElementById('statusMarquee'),
        statusMarqueeContent: document.getElementById('statusMarqueeContent'),
        pageSizeSelect: document.getElementById('pageSizeSelect')
    };

    function init() {
        console.log('Redbook Monitor initialized');
        console.log('API Base URL:', window.API_CONFIG.baseURL);
        setupEventListeners();
        updateCrawlTime();
        setInterval(updateCrawlTime, 1000);
        loadStats();
        loadKeywords();
        startStatsRefresh();
    }

    let allKeywords = [];

    async function loadKeywords() {
        try {
            const response = await apiRequest('/api/keywords');
            if (response.data && response.data.length > 0) {
                allKeywords = response.data;
                console.log(`加载了 ${response.data.length} 个关键词`);
            }
        } catch (error) {
            console.error('加载关键词列表失败:', error);
        }
    }

    function renderDropdown(keywords) {
        if (!keywords || keywords.length === 0) {
            elements.keywordDropdown.classList.remove('show');
            return;
        }
        
        elements.keywordDropdown.innerHTML = '';
        keywords.forEach(keyword => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.textContent = keyword;
            item.addEventListener('click', () => selectKeyword(keyword));
            elements.keywordDropdown.appendChild(item);
        });
        elements.keywordDropdown.classList.add('show');
    }

    function selectKeyword(keyword) {
        elements.keywordInput.value = keyword;
        elements.keywordDropdown.classList.remove('show');
        elements.keywordInput.focus();
    }

    function filterKeywords(searchText) {
        if (!searchText) {
            return allKeywords;
        }
        return allKeywords.filter(keyword => 
            keyword.toLowerCase().includes(searchText.toLowerCase())
        );
    }

    async function apiRequest(endpoint, options = {}) {
        const url = `${window.API_CONFIG.baseURL}${endpoint}`;
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API请求失败 [${endpoint}]:`, error);
            throw error;
        }
    }

    async function loadStats() {
        try {
            const stats = await apiRequest('/api/stats');
            elements.totalNotes.textContent = `NOTES: ${stats.total || 0}`;
            elements.totalComments.textContent = `COMMENTS: ${stats.total_comments || 0}`;
        } catch (error) {
            console.error('加载统计数据失败:', error);
        }
    }

    function startStatsRefresh() {
        if (statsRefreshTimer) clearInterval(statsRefreshTimer);
        statsRefreshTimer = setInterval(loadStats, STATS_REFRESH_INTERVAL);
    }

    function setupEventListeners() {
        elements.searchBtn.addEventListener('click', handleSearch);
        
        elements.keywordInput.addEventListener('input', (e) => {
            const filtered = filterKeywords(e.target.value);
            renderDropdown(filtered);
        });
        
        elements.keywordInput.addEventListener('focus', (e) => {
            handleInputFocus(e);
            if (allKeywords.length > 0) {
                const filtered = filterKeywords(e.target.value);
                renderDropdown(filtered);
            }
        });
        
        elements.keywordInput.addEventListener('blur', (e) => {
            handleInputBlur(e);
            setTimeout(() => {
                elements.keywordDropdown.classList.remove('show');
            }, 200);
        });
        
        elements.keywordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                elements.keywordDropdown.classList.remove('show');
                handleSearch();
            }
        });
        
        elements.prevNote.addEventListener('click', () => navigateNote(-1));
        elements.nextNote.addEventListener('click', () => navigateNote(1));
        elements.pageSizeSelect.addEventListener('change', handlePageSizeChange);
        
        document.addEventListener('click', (e) => {
            if (!elements.keywordInput.contains(e.target) && !elements.keywordDropdown.contains(e.target)) {
                elements.keywordDropdown.classList.remove('show');
            }
        });
    }

    function handlePageSizeChange() {
        commentsPerPage = parseInt(elements.pageSizeSelect.value);
        currentCommentPage = 1; // 重置到第一页
        if (currentNotes && currentNotes[currentNoteIndex]) {
            loadComments(currentNotes[currentNoteIndex].note_id);
        }
    }

    function handleInputFocus(e) {
        e.target.style.boxShadow = '0 0 0 2px var(--theme-primary), 0 0 10px rgba(0, 255, 0, 0.2)';
    }

    function handleInputBlur(e) {
        e.target.style.boxShadow = '';
    }

    async function handleSearch() {
        const keyword = elements.keywordInput.value.trim();
        
        if (!keyword) {
            showMarquee('ERROR: KEYWORD_REQUIRED');
            return;
        }

        showMarquee(`LOADING_STATUS: ${keyword}...`);
        
        try {
            const response = await apiRequest(`/api/notes?keyword=${encodeURIComponent(keyword)}&page=1&page_size=100`);
            
            if (!response.data || response.data.length === 0) {
                showMarquee(`NO_DATA: ${keyword}`);
                showNoDataMessage();
                return;
            }

            currentNotes = response.data;
            currentKeyword = keyword;
            currentNoteIndex = 0;

            elements.currentKeyword.textContent = `CURRENT_KEYWORD: ${currentKeyword.toUpperCase()}`;
            displayNote(0);
            loadStats();
            
            const crawlingCount = currentNotes.filter(n => n.is_comment_crawled === 2).length;
            const completedCount = currentNotes.filter(n => n.is_comment_crawled === 1).length;
            showMarquee(`LOADED: ${currentNotes.length} | CRAWLING: ${crawlingCount} | COMPLETED: ${completedCount}`);
            
            setTimeout(() => {
                elements.statusMarquee.style.display = 'none';
            }, 5000);
        } catch (error) {
            showMarquee(`ERROR: API_REQUEST_FAILED`);
            console.error('查看状态失败:', error);
        }
    }

    function showNoDataMessage() {
        elements.noteCard.innerHTML = `
            <div class="note-loading">
                <div class="terminal-line">C:\\REDBOOK\\MONITOR\\> ERROR_404</div>
                <p class="loading-text text-glow">[ NO_DATA_FOUND ]</p>
                <p class="loading-hint">SELECT_KEYWORD_FROM_DROPDOWN_OR_ENTER_MANUALLY</p>
            </div>
        `;
        elements.commentsContainer.innerHTML = `
            <div class="comments-loading">
                <div class="terminal-line">C:\\REDBOOK\\COMMENTS\\> NO_DATA</div>
                <p class="loading-text">[ NO_COMMENTS_AVAILABLE ]</p>
            </div>
        `;
    }

    function showMarquee(message) {
        elements.statusMarqueeContent.innerHTML = `<span>${message}</span>`;
        elements.statusMarquee.style.display = 'block';
    }


    function updateCrawlTime() {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        elements.crawlTime.textContent = `TIME: ${timeStr}`;
    }

    function displayNote(index) {
        if (!currentNotes || !currentNotes[index]) return;

        const note = currentNotes[index];
        currentNoteIndex = index;

        const crawlingIndicator = note.is_comment_crawled === 2 
            ? '<div class="crawling-indicator"><div class="crawling-spinner"></div><span class="crawling-text">CRAWLING<span class="crawling-dots"></span></span></div>'
            : '';

        elements.noteCard.innerHTML = `
            <div class="note-content">
                <div class="note-meta">
                    <h2 class="note-title">${escapeHtml(note.title)}</h2>
                    <div class="note-author">AUTHOR: ${escapeHtml(note.author_name)}</div>
                    <div class="note-stats">
                        <span>❤ LIKES: ${(note.like_count || 0).toLocaleString()}</span>
                        <span>💬 COMMENTS: ${(note.comment_count || 0).toLocaleString()}</span>
                        ${crawlingIndicator}
                    </div>
                </div>
                <div class="note-body">
                    <div class="note-summary">
                        <div class="terminal-line">NOTE_ID: ${note.note_id}</div>
                        <div class="terminal-line">KEYWORD: ${note.keyword || 'N/A'}</div>
                    </div>
                </div>
                <div class="note-timestamp">
                    PUBLISH_TIME: ${note.publish_time || 'N/A'}<br/>
                    UPDATE_TIME: ${formatDateTime(note.update_time)}
                </div>
            </div>
        `;

        elements.noteIndex.textContent = `NOTE_INDEX: ${index + 1}/${currentNotes.length}`;

        elements.prevNote.disabled = index === 0;
        elements.nextNote.disabled = index === currentNotes.length - 1;

        loadComments(note.note_id);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatDateTime(dateStr) {
        if (!dateStr) return 'N/A';
        try {
            const date = new Date(dateStr);
            return date.toLocaleString('zh-CN', { hour12: false });
        } catch {
            return dateStr;
        }
    }

    async function loadComments(noteId) {
        try {
            const response = await apiRequest(`/api/notes/${noteId}/comments?page=${currentCommentPage}&page_size=${commentsPerPage}`);
            
            if (!response.data || response.data.length === 0) {
                elements.commentsContainer.innerHTML = `
                    <div class="comments-loading">
                        <div class="terminal-line">C:\\REDBOOK\\COMMENTS\\> NO_COMMENTS_FOUND</div>
                        <p class="loading-text">[ NO_COMMENTS_DATA ]</p>
                        <p class="loading-hint">THIS_NOTE_HAS_NO_COMMENTS_YET</p>
                    </div>
                `;
                elements.commentCount.textContent = 'COUNT: 0';
                return;
            }

            currentComments = response.data;
            renderCommentsPage(response);
        } catch (error) {
            console.error('加载评论失败:', error);
            elements.commentsContainer.innerHTML = `
                <div class="comments-loading">
                    <div class="terminal-line">C:\\REDBOOK\\COMMENTS\\> ERROR_LOADING</div>
                    <p class="loading-text">[ FAILED_TO_LOAD_COMMENTS ]</p>
                </div>
            `;
        }
    }

    function renderCommentsPage(response) {
        const { data: comments, pagination } = response;
        
        elements.commentCount.textContent = `COUNT: ${pagination.total} | PAGE: ${pagination.page}/${pagination.total_pages}`;

        const commentsHTML = comments.map(comment => `
            <div class="comment-item">
                <div class="comment-header">
                    <span class="comment-user">COMMENT_ID: ${comment.id}</span>
                    <span class="comment-time">${formatDateTime(comment.create_time)}</span>
                </div>
                <div class="comment-content">${escapeHtml(comment.comment_content)}</div>
                <div class="comment-footer">
                    <span>KEYWORD: ${comment.keyword || 'N/A'}</span>
                </div>
            </div>
        `).join('');

        const paginationHTML = pagination.total_pages > 1 ? `
            <div class="comment-pagination">
                <button class="nav-btn" id="prevCommentPage" ${pagination.page === 1 ? 'disabled' : ''}>
                    <span class="material-symbols-outlined">arrow_upward</span>
                    [ PREV_PAGE ]
                </button>
                <button class="nav-btn" id="nextCommentPage" ${pagination.page >= pagination.total_pages ? 'disabled' : ''}>
                    <span class="material-symbols-outlined">arrow_downward</span>
                    [ NEXT_PAGE ]
                </button>
            </div>
        ` : '';

        elements.commentsContainer.innerHTML = `
            <div class="comments-list">${commentsHTML}</div>
            ${paginationHTML}
        `;

        if (pagination.total_pages > 1) {
            const currentNote = currentNotes[currentNoteIndex];
            document.getElementById('prevCommentPage')?.addEventListener('click', () => {
                if (currentCommentPage > 1) {
                    currentCommentPage--;
                    loadComments(currentNote.note_id);
                }
            });
            document.getElementById('nextCommentPage')?.addEventListener('click', () => {
                if (currentCommentPage < pagination.total_pages) {
                    currentCommentPage++;
                    loadComments(currentNote.note_id);
                }
            });
        }
        
        // 更新分页选择器显示
        elements.pageSizeSelect.value = commentsPerPage;
    }

    function navigateNote(direction) {
        if (!currentNotes || currentNotes.length === 0) return;

        const newIndex = currentNoteIndex + direction;
        if (newIndex >= 0 && newIndex < currentNotes.length) {
            currentCommentPage = 1;
            displayNote(newIndex);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
