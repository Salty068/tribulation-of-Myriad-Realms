// State management
let chapters = [];
let currentChapter = null;

// DOM Elements
const homePage = document.getElementById('homePage');
const chaptersListPage = document.getElementById('chaptersListPage');
const readerPage = document.getElementById('readerPage');
const homeBtn = document.getElementById('homeBtn');
const chaptersBtn = document.getElementById('chaptersBtn');
const startReadingBtn = document.getElementById('startReadingBtn');
const continueReadingBtn = document.getElementById('continueReadingBtn');
const chaptersList = document.getElementById('chaptersList');
const chapterTitle = document.getElementById('chapterTitle');
const chapterContent = document.getElementById('chapterContent');
const chapterSelector = document.getElementById('chapterSelector');
const prevChapterBtn = document.getElementById('prevChapterBtn');
const nextChapterBtn = document.getElementById('nextChapterBtn');
const prevChapterBtnBottom = document.getElementById('prevChapterBtnBottom');
const nextChapterBtnBottom = document.getElementById('nextChapterBtnBottom');
const chapterCount = document.getElementById('chapterCount');
const themeToggle = document.getElementById('themeToggle');

// Initialize
async function init() {
    await loadChapters();
    setupEventListeners();
    checkLastRead();
    initializeTheme();
}

// Theme management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    themeToggle.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
}

// Load chapters from en_chapters folder
async function loadChapters() {
    try {
        // Fetch the chapter list from GitHub or local
        const response = await fetch('en_chapters/');
        
        // If we're on GitHub Pages, use a different approach
        // This will be populated by our build script
        if (typeof CHAPTER_LIST !== 'undefined') {
            chapters = CHAPTER_LIST.map(filename => ({
                filename: filename,
                number: parseInt(filename.match(/ch_(\d+)\.txt/)[1])
            })).sort((a, b) => a.number - b.number);
        } else {
            // For local development, we'll manually create a chapter list
            // This will be replaced by the build process
            chapters = await fetchLocalChapters();
        }
        
        chapterCount.textContent = chapters.length;
        renderChaptersList();
        populateChapterSelector();
    } catch (error) {
        console.error('Error loading chapters:', error);
        chapterContent.innerHTML = '<p class="loading">Error loading chapters. Make sure en_chapters folder exists.</p>';
    }
}

// Fetch local chapters (for development)
async function fetchLocalChapters() {
    const localChapters = [];
    // Try to load chapters 1-1000
    for (let i = 1; i <= 1000; i++) {
        const filename = `ch_${i}.txt`;
        try {
            const response = await fetch(`en_chapters/${filename}`, { method: 'HEAD' });
            if (response.ok) {
                localChapters.push({
                    filename: filename,
                    number: i
                });
            }
        } catch (error) {
            // File doesn't exist, continue
            if (i > 10 && localChapters.length === 0) {
                break; // Stop if we haven't found any chapters after 10 tries
            }
        }
    }
    return localChapters;
}

// Render chapters list
function renderChaptersList() {
    chaptersList.innerHTML = '';
    chapters.forEach(chapter => {
        const item = document.createElement('div');
        item.className = 'chapter-item';
        item.innerHTML = `
            <span>Chapter ${chapter.number}</span>
            <span class="chapter-number">${chapter.filename}</span>
        `;
        item.onclick = () => loadChapter(chapter.number);
        chaptersList.appendChild(item);
    });
}

// Populate chapter selector
function populateChapterSelector() {
    chapterSelector.innerHTML = '';
    chapters.forEach(chapter => {
        const option = document.createElement('option');
        option.value = chapter.number;
        option.textContent = `Chapter ${chapter.number}`;
        chapterSelector.appendChild(option);
    });
}

// Load a specific chapter
async function loadChapter(chapterNum) {
    try {
        currentChapter = chapterNum;
        const chapter = chapters.find(c => c.number === chapterNum);
        
        if (!chapter) {
            chapterContent.innerHTML = '<p class="loading">Chapter not found.</p>';
            return;
        }

        chapterTitle.textContent = `Chapter ${chapterNum}`;
        chapterContent.innerHTML = '<p class="loading">Loading chapter...</p>';
        
        showPage('reader');
        window.scrollTo(0, 0);

        const response = await fetch(`en_chapters/${chapter.filename}`);
        const text = await response.text();
        
        // Format the chapter content
        const paragraphs = text.split('\n').filter(p => p.trim()).map(p => `<p>${p.trim()}</p>`).join('');
        chapterContent.innerHTML = paragraphs;

        // Update selector
        chapterSelector.value = chapterNum;

        // Update navigation buttons
        updateNavigationButtons();

        // Save last read chapter
        localStorage.setItem('lastReadChapter', chapterNum);
    } catch (error) {
        console.error('Error loading chapter:', error);
        chapterContent.innerHTML = '<p class="loading">Error loading chapter content.</p>';
    }
}

// Update navigation buttons
function updateNavigationButtons() {
    const currentIndex = chapters.findIndex(c => c.number === currentChapter);
    
    prevChapterBtn.disabled = currentIndex <= 0;
    prevChapterBtnBottom.disabled = currentIndex <= 0;
    nextChapterBtn.disabled = currentIndex >= chapters.length - 1;
    nextChapterBtnBottom.disabled = currentIndex >= chapters.length - 1;
}

// Navigate to previous chapter
function prevChapter() {
    const currentIndex = chapters.findIndex(c => c.number === currentChapter);
    if (currentIndex > 0) {
        loadChapter(chapters[currentIndex - 1].number);
    }
}

// Navigate to next chapter
function nextChapter() {
    const currentIndex = chapters.findIndex(c => c.number === currentChapter);
    if (currentIndex < chapters.length - 1) {
        loadChapter(chapters[currentIndex + 1].number);
    }
}

// Show specific page
function showPage(pageName) {
    homePage.classList.remove('active');
    chaptersListPage.classList.remove('active');
    readerPage.classList.remove('active');

    switch(pageName) {
        case 'home':
            homePage.classList.add('active');
            break;
        case 'chapters':
            chaptersListPage.classList.add('active');
            break;
        case 'reader':
            readerPage.classList.add('active');
            break;
    }
}

// Check for last read chapter
function checkLastRead() {
    const lastRead = localStorage.getItem('lastReadChapter');
    if (lastRead && chapters.length > 0) {
        continueReadingBtn.style.display = 'inline-block';
        continueReadingBtn.onclick = () => loadChapter(parseInt(lastRead));
    }
}

// Setup event listeners
function setupEventListeners() {
    homeBtn.onclick = () => showPage('home');
    chaptersBtn.onclick = () => showPage('chapters');
    startReadingBtn.onclick = () => {
        if (chapters.length > 0) {
            loadChapter(chapters[0].number);
        }
    };
    
    themeToggle.onclick = toggleTheme;
    
    prevChapterBtn.onclick = prevChapter;
    nextChapterBtn.onclick = nextChapter;
    prevChapterBtnBottom.onclick = prevChapter;
    nextChapterBtnBottom.onclick = nextChapter;
    
    chapterSelector.onchange = (e) => {
        loadChapter(parseInt(e.target.value));
    };

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (readerPage.classList.contains('active')) {
            if (e.key === 'ArrowLeft') {
                prevChapter();
            } else if (e.key === 'ArrowRight') {
                nextChapter();
            }
        }
    });
    
    // Auto-hide navbar on scroll for mobile
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    const scrollThreshold = 5; // Minimum scroll distance to trigger
    
    window.addEventListener('scroll', () => {
        // Only on mobile devices
        if (window.innerWidth <= 768) {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (Math.abs(scrollTop - lastScrollTop) < scrollThreshold) {
                return; // Don't do anything if scroll is too small
            }
            
            if (scrollTop > lastScrollTop && scrollTop > 50) {
                // Scrolling down & past threshold
                navbar.classList.add('hidden');
            } else {
                // Scrolling up
                navbar.classList.remove('hidden');
            }
            
            lastScrollTop = scrollTop;
        } else {
            // Always show on desktop
            navbar.classList.remove('hidden');
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
