'use strict';

// ---------- learning progress (kept in this browser only) ----------
const STORE = 'medical-teach:progress:v1';
function loadProgress() {
  try {
    const s = JSON.parse(localStorage.getItem(STORE));
    if (s && Array.isArray(s.done)) return s;
  } catch {}
  return { done: [], last: null };
}
function saveProgress(s) {
  try { localStorage.setItem(STORE, JSON.stringify(s)); } catch {}
}
const progress = loadProgress();
function paintDone() {
  document.querySelectorAll('[data-code]').forEach(el => {
    if (el === document.body) return;
    el.classList.toggle('is-done', progress.done.includes(el.dataset.code));
  });
  document.querySelectorAll('.track-progress').forEach(el => {
    const total = Number(el.dataset.total);
    const n = [...document.querySelectorAll(`#${el.dataset.track} [data-code]`)].filter(a => a.classList.contains('is-done')).length;
    el.textContent = n ? `已学完 ${n} / ${total}` : `${total} 课`;
  });
}

// Lesson page: remember the last lesson and offer a "done" toggle.
const lessonCode = document.body.dataset.code;
if (lessonCode) {
  progress.last = lessonCode;
  saveProgress(progress);
  const button = document.querySelector('#mark-done');
  const flag = document.querySelector('.done-flag');
  const render = () => {
    const done = progress.done.includes(lessonCode);
    button.textContent = done ? '✓ 已学完（点击取消）' : '标记本课已学完';
    button.setAttribute('aria-pressed', String(done));
    button.classList.toggle('is-done', done);
    flag.hidden = !done;
    paintDone();
  };
  button.addEventListener('click', () => {
    progress.done = progress.done.includes(lessonCode)
      ? progress.done.filter(c => c !== lessonCode)
      : [...progress.done, lessonCode];
    saveProgress(progress);
    render();
  });
  render();
} else {
  paintDone();
}

// Home page: "continue where you left off".
const resume = document.querySelector('#resume');
if (resume && progress.last) {
  const card = document.querySelector(`.course-card[data-code="${progress.last}"]`);
  if (card) {
    const link = document.createElement('a');
    link.href = card.getAttribute('href');
    link.textContent = `继续学习：${progress.last} ${card.querySelector('strong').textContent} →`;
    resume.append(link);
    resume.hidden = false;
  }
}

// ---------- course search ----------
const search = document.querySelector('#course-search');
if (search) {
  search.addEventListener('input', () => {
    const q = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    document.querySelectorAll('[data-course]').forEach(row => {
      const hide = !row.dataset.course.toLocaleLowerCase().includes(q);
      row.parentElement.hidden = hide;
      if (!hide) shown++;
    });
    document.querySelectorAll('.course-group').forEach(group => {
      group.hidden = ![...group.querySelectorAll('[data-course]')].some(row => !row.parentElement.hidden);
    });
    document.querySelector('#search-empty').hidden = shown > 0;
  });
}

// ---------- lesson layout: open the outline on wide screens, fold the course list on phones ----------
const narrow = window.matchMedia('(max-width: 720px)').matches;
const courseNav = document.querySelector('.course-nav');
if (courseNav && narrow) courseNav.open = false;
const toc = document.querySelector('.page-toc');
if (toc && !narrow) toc.open = true;

// ---------- video chapters ----------
const video = document.querySelector('#lesson-video');
if (video) {
  const chapters = JSON.parse(document.querySelector('#video-chapters').textContent);
  const track = video.addTextTrack('chapters', '操作章节', 'zh-CN');
  track.mode = 'hidden';
  chapters.forEach(c => track.addCue(new VTTCue(c.start, Math.max(c.start + .001, c.end - .05), c.title)));
  document.querySelectorAll('[data-seek]').forEach(button => button.addEventListener('click', () => {
    const start = Number(button.dataset.seek);
    const play = () => { video.currentTime = start; video.play().catch(() => {}); };
    if (video.readyState >= 1) play(); else video.addEventListener('loadedmetadata', play, { once: true });
  }));
}

// ---------- copy buttons on prompts ----------
document.querySelectorAll('article pre').forEach(pre => {
  const code = pre.querySelector('code');
  if (!code) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-button';
  button.textContent = '复制';
  button.setAttribute('aria-label', '复制这段提示词或代码');
  button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(code.textContent); button.textContent = '已复制'; }
    catch { button.textContent = '请选中文本复制'; }
    setTimeout(() => button.textContent = '复制', 2000);
  });
  pre.append(button);
});
