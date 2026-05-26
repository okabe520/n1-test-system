// Exam state
let totalQuestions = 0;
let currentIndex = 0;
let answeredCount = 0;
let answers = {};
let bookmarks = new Set();
let timeLeft = EXAM_TOTAL_TIME;
let timerInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.question-card');
    totalQuestions = cards.length;
    if (totalQuestions === 0) return;

    document.getElementById('progress').textContent = `0/${totalQuestions}`;
    showQuestion(0);
    startTimer();
    initSheetClicks();
});

function loadFromLS() {
    const saved = localStorage.getItem('n1_exam_state');
    if (saved) {
        try {
            const s = JSON.parse(saved);
            answers = s.answers || {};
            bookmarks = new Set(s.bookmarks || []);
            currentIndex = s.currentIndex || 0;
            timeLeft = s.timeLeft;
            answeredCount = Object.keys(answers).length;
            document.querySelectorAll('.question-card').forEach(card => {
                const qid = card.dataset.id;
                if (answers[qid] !== undefined) {
                    const radio = document.querySelector(`input[name="q-${qid}"][value="${answers[qid]}"]`);
                    if (radio) radio.checked = true;
                }
                if (bookmarks.has(qid)) {
                    const bm = card.querySelector('.q-bookmark');
                    if (bm) bm.classList.add('bookmarked');
                }
            });
        } catch(e) {}
    }
}

function saveToLS() {
    localStorage.setItem('n1_exam_state', JSON.stringify({
        answers, bookmarks: [...bookmarks], currentIndex, timeLeft
    }));
}

function showQuestion(idx) {
    document.querySelectorAll('.question-card').forEach(c => c.style.display = 'none');
    const card = document.getElementById(`q-${document.querySelectorAll('.question-card')[idx]?.dataset.id}`);
    if (card) {
        card.style.display = 'block';
        currentIndex = idx;
        updateSheetHighlight();
        saveToLS();
    }
}

function selectAnswer(qid, value) {
    if (answers[qid] === undefined) answeredCount++;
    answers[qid] = value;
    document.getElementById('progress').textContent = `${answeredCount}/${totalQuestions}`;
    updateSheetCell(qid);
    saveToLS();
    // Auto-advance after short delay
    setTimeout(() => {
        if (currentIndex < totalQuestions - 1) {
            // Check if current question id matches
            const nextCards = document.querySelectorAll('.question-card');
            const currentCard = nextCards[currentIndex];
            if (currentCard && currentCard.dataset.id == qid) {
                showQuestion(currentIndex + 1);
            }
        }
    }, 400);
}

function toggleBookmark(el, qid) {
    if (bookmarks.has(qid)) {
        bookmarks.delete(qid);
        el.classList.remove('bookmarked');
    } else {
        bookmarks.add(qid);
        el.classList.add('bookmarked');
    }
    saveToLS();
}

function initSheetClicks() {
    document.querySelectorAll('.sheet-cell').forEach(cell => {
        cell.addEventListener('click', () => {
            const qid = cell.dataset.id;
            const cards = Array.from(document.querySelectorAll('.question-card'));
            const idx = cards.findIndex(c => c.dataset.id === qid);
            if (idx >= 0) showQuestion(idx);
        });
    });
}

function updateSheetCell(qid) {
    const cell = document.getElementById(`cell-${qid}`);
    if (cell) cell.classList.add('answered');
}

function updateSheetHighlight() {
    document.querySelectorAll('.sheet-cell').forEach(c => c.classList.remove('current'));
    const cards = document.querySelectorAll('.question-card');
    if (cards[currentIndex]) {
        const cell = document.getElementById(`cell-${cards[currentIndex].dataset.id}`);
        if (cell) cell.classList.add('current');
    }
}

function startTimer() {
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimerDisplay();
        saveToLS();
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert('時間です！自動的に提出します。');
            submitExam();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const m = Math.floor(timeLeft / 60);
    const s = timeLeft % 60;
    const display = document.getElementById('timer');
    if (display) {
        display.textContent = `${m}:${String(s).padStart(2, '0')}`;
        if (timeLeft < 300) display.classList.add('warning');
    }
}

function submitExam() {
    if (!confirm('試験を提出しますか？未回答の問題も自動提出されます。')) return;
    clearInterval(timerInterval);
    localStorage.removeItem('n1_exam_state');

    const total = document.querySelectorAll('.question-card').length;
    const answered = Object.keys(answers).length;
    const unanswered = total - answered;
    // Mark unanswered as -1
    document.querySelectorAll('.question-card').forEach(c => {
        const qid = c.dataset.id;
        if (answers[qid] === undefined) answers[qid] = -1;
    });

    const duration = EXAM_TOTAL_TIME - timeLeft;

    document.querySelector('.exam-body').innerHTML = '<div class="loading">採点中...</div>';

    fetch('/api/submit-exam', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({answers, duration}),
    })
    .then(r => r.json())
    .then(data => {
        // Store result and redirect
        sessionStorage.setItem('n1_result', JSON.stringify({
            score: data.score, total: data.total, correct: data.correct,
            duration, details: data.details,
        }));
        window.location.href = '/result/latest';
    })
    .catch(err => {
        document.querySelector('.exam-body').innerHTML = '<div class="error">エラーが発生しました。もう一度お試しください。</div>';
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' || e.key === 'a') {
        if (currentIndex > 0) showQuestion(currentIndex - 1);
    } else if (e.key === 'ArrowRight' || e.key === 'd') {
        if (currentIndex < totalQuestions - 1) showQuestion(currentIndex + 1);
    } else if (e.key >= '1' && e.key <= '4') {
        const cards = document.querySelectorAll('.question-card');
        const card = cards[currentIndex];
        if (card) {
            const qid = card.dataset.id;
            const val = parseInt(e.key) - 1;
            selectAnswer(qid, val);
            const radio = document.querySelector(`input[name="q-${qid}"][value="${val}"]`);
            if (radio) radio.checked = true;
        }
    }
});

// Initialize from saved state
loadFromLS();
updateSheetHighlight();
// Restore answered cells
Object.keys(answers).forEach(qid => updateSheetCell(qid));
