"""Build the static course site from the maintained Markdown lessons."""
from pathlib import Path
import html, json, re, zipfile
from urllib.parse import quote
import mistune

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'WorkBuddy教程'
PACK_NAME = 'WorkBuddy教程-练习包.zip'
WORKBUDDY_URL = 'https://www.workbuddy.cn'
GITHUB_URL = 'https://github.com/JuneYaooo/medical-teach'

TRACKS = {
    'start': dict(name='入门', codes=['00', '01'], desc='认识工作空间、技能与课程里的核对方法。'),
    'research': dict(name='医学科研线', codes=[f'R{i}' for i in range(1, 9)],
                     desc='从文献与问题出发，完成方案、分析、写作和协作。'),
    'public': dict(name='患者科普线', codes=[f'P{i}' for i in range(1, 10)],
                   desc='从患者问题出发，把同一份证据转成清楚、可核对的内容。',
                   hint='建议顺序：先学 P1、P2，再看科研线 R1、R2 的检索核对方法，然后进入 P3–P9。'),
}
ORDER = [c for t in TRACKS.values() for c in t['codes']]
FOCUS = {
    '00': '两条学习路线怎么选，每课怎么用。', '01': '建立工作空间，导入技能，核对第一条医学论断。',
    'R1': '组织 PICO、检索文献，区分研究结论与外推。', 'R2': '逐条核对论断、摘要与引用，留下证据位置。',
    'R3': '草拟研究方案和 SAP，运行样本量计算。', 'R4': '从数据体检到清洗日志、模型与置信区间。',
    'R5': '对照结果写作，按立场逐条回应审稿意见。', 'R6': '把研究目标、技术路线、周期和资源放在一起核对。',
    'R7': '把组会转写整理成纪要、负责人和进度表。', 'R8': '提炼审稿回复规则，导入技能并检验边界。',
    'P1': '从模拟对标资料里确定受众、定位和内容支柱。', 'P2': '合并患者问法，保留来源，形成可排序的选题库。',
    'P3': '以事实卡为基础写文章，逐句保留来源与限定。', 'P4': '把一个主题拆成 30 秒脚本和分镜。',
    'P5': '生成六页图文与竖版海报，逐页检查版式。', 'P6': '完成口播稿、配音、数字人视频与字幕。',
    'P7': '制作患教单与随访话术，用回授发现歧义。', 'P8': '同一组事实卡生成四类内容，逐句检查一致性。',
    'P9': '把风格和核对规则固化为可复用的技能。'}
# 00 and 01 have no metadata table in their Markdown.
EXTRA_META = {'00': {'产出': '选定自己的学习路线'}, '01': {'难度': '1', '产出': '一份入门核对结果 + 一个可用的证据核对技能'}}
LEVEL = {'1': '入门', '1-2': '基础', '2': '基础', '3': '进阶'}

md = mistune.create_markdown(plugins=['table', 'strikethrough', 'task_lists', 'url'])


def esc(s): return html.escape(str(s), quote=True)
def url(p): return quote(str(p), safe='/')
def track_of(code): return next(k for k, t in TRACKS.items() if code in t['codes'])


def parse_meta(code, text):
    meta = {}
    for key in ['难度', '时长', '前置', '产出']:
        m = re.search(r'^\| ' + key + r' \| (.+?) \|\s*$', text, re.M)
        if m: meta[key] = m.group(1).strip()
    meta.update(EXTRA_META.get(code, {}))
    return meta


def short_prereq(s):
    """Required lessons only, without the explanations in brackets."""
    s = s.split('；建议')[0]
    while re.search(r'（[^（）]*）', s): s = re.sub(r'（[^（）]*）', '', s)
    return re.sub(r'\s*[；、]\s*', ' · ', s).strip()


def link_codes(s, prefix=''):
    """Turn lesson codes in a prerequisite text into links."""
    def rep(m):
        code = '01' if m.group(0) == '01 入门课' else m.group(0)
        l = by_code.get(code)
        return f'<a href="{prefix}{url(l["html"])}">{esc(m.group(0))}</a>' if l else esc(m.group(0))
    out, last = '', 0
    for m in re.finditer(r'01 入门课|(?<![A-Za-z0-9])[RP][1-9](?![0-9])', s):
        out += esc(s[last:m.start()]) + rep(m); last = m.end()
    return out + esc(s[last:])


lessons = []
for code in ORDER:
    p = next((SITE / '课程').glob(code + '-*.md'))
    text = p.read_text()
    title = text.splitlines()[0].lstrip('# ')
    display = re.sub(r'^(?:' + re.escape(code) + r'|入门课)[：:\s]*', '', title)
    video = SITE / '录屏' / f'{code}-WorkBuddy实操.mp4'
    vmeta = json.loads(video.with_suffix('.json').read_text())
    lessons.append(dict(code=code, path=p, html=p.with_suffix('.html').name, text=text, title=title,
                        display=display, video=video, chapters=vmeta['chapters'],
                        meta=parse_meta(code, text), track=track_of(code)))
by_code = {l['code']: l for l in lessons}


# ---------- practice pack ----------
def build_pack():
    """Zip the practice workspace. Fixed timestamps keep the file stable between builds."""
    target = SITE / PACK_NAME
    readme = f'''WorkBuddy 医学教程 · 练习包

1. 把整个“家庭血压项目”文件夹放在你方便找到的位置。
2. 打开 WorkBuddy，点击“新建任务”→“选择工作空间”→“打开本地文件夹”，选中“家庭血压项目”。
3. 打开课程网站，从“01 入门课”开始，把每课的提示词复制到 WorkBuddy。

文件夹说明
- 资料/：每课要读取的练习文件（研究数据、审稿意见、事实卡与证据核对技能包等）。
- 成果/：空文件夹，你的练习结果会保存在这里。
- 参考结果/：课程作者实际跑出的结果，用来和你的结果对照。
  跳过某课时，可把对应文件夹复制到“成果/”。例如没做 R4 想直接学 R5，就把“参考结果/数据分析”复制成“成果/数据分析”。
  （P6 的口播视频和音频体积较大，未放入练习包，可在课程网页上直接播放。）

研究数据与审稿、申报及项目背景资料为合成或虚构材料；文献与事实卡的真实来源另行标注。

课程网站：https://juneyaooo.github.io/medical-teach/
'''
    files = [(f, '家庭血压项目/' + str(f.relative_to(SITE))) for f in sorted((SITE / '资料').rglob('*')) if f.is_file()]
    files += [(f, '家庭血压项目/参考结果/' + str(f.relative_to(SITE / '成果'))) for f in sorted((SITE / '成果').rglob('*'))
              if f.is_file() and f.stat().st_size < 2_000_000]
    files = [(f, n) for f, n in files if f.name != '.DS_Store']

    def info(name):
        zi = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = (0o40755 if name.endswith('/') else 0o100644) << 16
        return zi
    with zipfile.ZipFile(target, 'w') as z:
        z.writestr(info('家庭血压项目/开始前请读.txt'), readme)
        z.writestr(info('家庭血压项目/成果/'), '')
        for f, name in files: z.writestr(info(name), f.read_bytes())
    return target.stat().st_size


pack_size = build_pack()
pack_label = f'{pack_size / 1024 / 1024:.1f} MB' if pack_size > 1024 * 1024 else f'{pack_size // 1024} KB'


# ---------- shared pieces ----------
def shell(title, body, prefix='', bodyclass='', code=''):
    data = f' data-code="{code}"' if code else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="医学科研与患者科普 WorkBuddy 实操课程。19 节教程，配套提示词、录屏、截图和练习文件。"><meta name="theme-color" content="#173e32"><title>{esc(title)} · 医学工作流课堂</title><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body class="{bodyclass}"{data}><a class="skip-link" href="#main">跳到正文</a>{body}</body></html>'''


def brand(home):
    return f'<a class="brand" href="{home}"><span class="brand-icon" aria-hidden="true">M</span><span>医学工作流课堂<small>WorkBuddy 实操教程</small></span></a>'


def facts_line(l):
    m, bits = l['meta'], []
    if '时长' in m: bits.append(re.sub(r'（.*?）$', '', m['时长']))
    if '难度' in m: bits.append(LEVEL.get(m['难度'], '难度 ' + m['难度']))
    if '前置' in m: bits.append('前置 ' + short_prereq(m['前置']))
    return ' · '.join(bits)


def pack_button(prefix, cls='secondary'):
    return f'<a class="{cls}" href="{prefix}{url(PACK_NAME)}" download>下载练习包 <span>{pack_label}</span></a>'


# ---------- catalog ----------
def course_card(l, prefix, n=None):
    search = ' '.join([l['code'], l['display'], FOCUS[l['code']], TRACKS[l['track']]['name']])
    num = f'<span class="card-step">{n}</span>' if n else ''
    facts = facts_line(l)
    return (f'<li><a class="course-card" data-code="{l["code"]}" data-course="{esc(search)}" href="{prefix}课程/{url(l["html"])}">'
            f'<span class="course-code">{l["code"]}</span><span class="course-text"><strong>{esc(l["display"])}</strong>'
            f'<span>{FOCUS[l["code"]]}</span>' + (f'<small>{esc(facts)}</small>' if facts else '') +
            f'</span><span class="course-state" aria-hidden="true">{num}</span></a></li>')


def catalog(prefix=''):
    p = prefix
    intro, first = by_code['00'], by_code['01']
    start = f'''<section class="course-group start-group" id="start"><div class="section-heading"><div><span class="eyebrow">第一步</span><h2>先学入门课</h2></div><p>两条路线都从这里开始：学会建工作空间、装技能、核对结果。</p></div>
<ol class="start-cards">{course_card(first, p)}{course_card(intro, p)}</ol></section>'''
    tracks = ''
    for key in ['research', 'public']:
        t = TRACKS[key]
        cards = ''.join(course_card(by_code[c], p) for c in t['codes'])
        hint = f'<p class="track-hint">{t["hint"]}</p>' if t.get('hint') else ''
        tracks += f'''<section class="course-group track" id="{key}"><div class="track-head"><div><h3>{t["name"]}</h3><p>{t["desc"]}</p></div><span class="track-progress" data-track="{key}" data-total="{len(t["codes"])}">{len(t["codes"])} 课</span></div>{hint}<ol class="course-list">{cards}</ol></section>'''
    body = f'''<header class="site-header">{brand(p + '课程目录.html')}<nav aria-label="主导航"><a href="#prepare">开始前准备</a><a href="#research">科研线</a><a href="#public">科普线</a><a href="{GITHUB_URL}">GitHub</a></nav></header>
<main id="main" class="home"><section class="hero"><div><p class="eyebrow">医学科研 · 患者科普 · WorkBuddy 实操</p><h1>让医学工作流<br>可复现、可核对。</h1><p class="hero-lead">从一份资料到一个可检查的结果。跟着 WorkBuddy 的真实操作，把文献、数据、写作与患者科普，一步一步做清楚。</p>
<div class="hero-actions"><a class="primary" href="{p}课程/{url(first["html"])}">开始入门课 <span aria-hidden="true">→</span></a>{pack_button(p)}</div>
<p id="resume" class="resume" hidden></p><p class="hero-meta">19 节课程 · 配套讲解录屏 · 可复制提示词 · 参考结果对照</p></div>
<aside class="prepare" id="prepare"><h2>开始前准备</h2><ol>
<li><span>1</span><div><strong>安装 WorkBuddy</strong><p>课程按 WorkBuddy 5.9.0 录制，界面有差异时以<a href="{WORKBUDDY_URL}">官方说明</a>为准。</p></div></li>
<li><span>2</span><div><strong>下载练习包并解压</strong><p>得到一个“家庭血压项目”文件夹，里面有资料、技能包和参考结果。</p></div></li>
<li><span>3</span><div><strong>把文件夹设为工作空间</strong><p>在 WorkBuddy 点“新建任务”→“选择工作空间”→“打开本地文件夹”，选中它。</p></div></li>
<li><span>4</span><div><strong>打开一课，照着做</strong><p>先看讲解录屏，再复制提示词到 WorkBuddy，最后打开结果文件核对。</p></div></li>
</ol></aside></section>
{start}
<div class="catalog-tools"><div><span class="eyebrow">第二步</span><h2>选一条路线</h2><p>两条线可以只学一条；每条线按顺序学，后面的课会用到前面的结果。</p></div><label class="search-label">查找课程<input id="course-search" type="search" placeholder="课程名、编号或关键词" autocomplete="off"></label></div>
<p id="search-empty" hidden>没有匹配的课程，请试试“数据”“科普”或课程编号。</p>
<div class="tracks">{tracks}</div>
<aside class="scope-note"><strong>关于练习素材</strong><p>统计数据、审稿意见和项目资料为教学模拟；医学事实卡附公开来源，来源核对不等于医生审核。录屏带讲解旁白和字幕，完整提示词见各课正文。P6 提供本次口播稿生成的数字人成片、字幕和配音文件。学习进度只保存在你当前使用的浏览器里。</p></aside></main>
<footer class="site-footer"><span>医学工作流课堂 · 按步骤学习，依据结果核对。</span><a href="{GITHUB_URL}">查看 Markdown 与课程文件</a></footer>'''
    return shell('课程目录', body, prefix, 'home-page')


# ---------- lesson pages ----------
def pager_targets(code):
    """Previous / next stay inside the learner's track."""
    track = TRACKS[track_of(code)]['codes']
    i = track.index(code)
    prev = track[i - 1] if i else ('01' if code in ('R1', 'P1') else None)
    if code == '01': return prev, [('选科研线', 'R1'), ('选科普线', 'P1')]
    if i + 1 < len(track): return prev, [('下一课', track[i + 1])]
    if code == 'R8': return prev, [('学完科研线 · 去科普线', 'P1')]
    if code == 'P9': return prev, [('学完科普线 · 去科研线', 'R1')]
    return prev, []


def pager(code):
    prev, nexts = pager_targets(code)
    out = '<nav class="lesson-pager" aria-label="前后课">'
    if prev:
        l = by_code[prev]
        out += f'<a class="prev" href="{url(l["html"])}"><span>← 上一课 · {prev}</span><strong>{esc(l["display"])}</strong></a>'
    else:
        out += '<a class="prev" href="../课程目录.html"><span>← 课程目录</span><strong>查看全部课程</strong></a>'
    for label, c in nexts:
        l = by_code[c]
        out += f'<a class="next" href="{url(l["html"])}"><span>{label} · {c} →</span><strong>{esc(l["display"])}</strong></a>'
    if not nexts:
        out += '<a class="next" href="../课程目录.html"><span>课程目录 →</span><strong>选择另一条学习路线</strong></a>'
    return out + '</nav>'


def sidebar(current):
    out = '<details class="course-nav" open><summary>全部课程</summary><nav aria-label="课程导航">'
    for key, t in TRACKS.items():
        out += f'<p>{t["name"]}</p>'
        for c in t['codes']:
            item = by_code[c]
            cur = ' aria-current="page"' if item is current else ''
            out += f'<a href="{url(item["html"])}" data-code="{c}"{cur}><span>{c}</span>{esc(item["display"])}</a>'
    return out + '</nav></details>'


def overview(l):
    m = l['meta']
    rows = ''
    for key in ['时长', '难度', '前置', '产出']:
        if key not in m: continue
        val = link_codes(m[key], '') if key == '前置' else esc(LEVEL.get(m[key], m[key]) if key == '难度' else m[key])
        rows += f'<div><dt>{key}</dt><dd>{val}</dd></div>'
    if l['code'] == '00':
        how = '读完路线说明后，回到目录先学 01 入门课，再选科研线或科普线。'
    elif l['code'] == '01':
        how = '先看下面的讲解录屏，再按第 1–4 步在 WorkBuddy 里操作，最后对照“自查与练习”检查结果。'
    else:
        how = ('先看讲解录屏了解全过程；再把“实操 1”的提示词复制到 WorkBuddy，完成后打开结果文件核对；最后读“完整方法”，换成自己的课题再做一次。'
               '<br><strong>注意</strong>：AI 每次的结果都不一样。实操 2 起的提示词是作者针对自己那次结果写的追问，里面提到的编号、数字和错误可能和你的结果对不上。'
               '先检查你的结果是否有同类问题，有就参照改写后再发，没有就跳过，不要原样照抄。')
    return (f'<section class="lesson-overview" aria-label="本课概览">' + (f'<dl>{rows}</dl>' if rows else '') +
            f'<p class="how"><strong>怎么学</strong>{how}</p><div class="overview-actions">{pack_button("../")}'
            f'<a class="secondary" href="#recording">看讲解录屏</a></div></section>')


def recording(l):
    chapters = l['chapters']
    out = (f'<section id="recording" class="recording"><h2>实操录屏</h2><p>带旁白和字幕，约 {round(chapters[-1]["end"] / 60) or 1} 分钟。点下面的阶段可以直接跳过去。</p>'
           f'<video id="lesson-video" controls playsinline preload="metadata" aria-label="{l["code"]} WorkBuddy 实操录屏">'
           f'<source src="../录屏/{url(l["video"].name)}" type="video/mp4">'
           f'<track kind="captions" src="../录屏/{url(l["video"].with_suffix(".vtt").name)}" srclang="zh-CN" label="旁白字幕"></video>'
           f'<div class="chapters" aria-label="录屏章节">')
    for ch in chapters:
        s = int(ch['start'])
        out += f'<button type="button" data-seek="{ch["start"]}"><span>{s // 60:02}:{s % 60:02}</span>{esc(ch["title"])}</button>'
    data = json.dumps(chapters, ensure_ascii=False).replace('</', '<' + chr(92) + '/')
    return out + f'</div><script type="application/json" id="video-chapters">{data}</script></section>'


def shots_gallery(rendered):
    """Show the screenshots at the end of a lesson as a grid of thumbnails."""
    head, sep, tail = rendered.partition('>操作画面</h2>')
    if not sep: return rendered
    fig = r'<p><img loading="lazy" decoding="async" src="([^"]+)" alt="([^"]*)" />\s*</p>\s*<p>(.*?)</p>\s*'
    figs = re.findall(fig, tail)
    if not figs: return rendered
    grid = '<p class="shots-note">点击截图查看大图。</p><div class="shots">' + ''.join(
        f'<figure><a href="{src}" target="_blank" rel="noopener"><img loading="lazy" decoding="async" src="{src}" alt="{alt}"></a><figcaption>{cap}</figcaption></figure>'
        for src, alt, cap in figs) + '</div>'
    tail = re.sub(fig, '', tail)
    return head + sep + grid + tail


for l in lessons:
    rendered = md(l['text'])
    rendered = re.sub(r'<img ', '<img loading="lazy" decoding="async" ', rendered)
    sections = []

    def heading(m):
        label = re.sub('<[^>]+>', '', m.group(1)); anchor = 'section-' + str(len(sections) + 1); sections.append((anchor, label))
        return f'<h2 id="{anchor}">{m.group(1)}</h2>'
    rendered = re.sub(r'<h2>(.*?)</h2>', heading, rendered, flags=re.S)
    rendered = shots_gallery(rendered)
    toc = '<details class="page-toc"><summary>本课目录</summary><nav aria-label="本课目录">' + ''.join(f'<a href="#{a}">{t}</a>' for a, t in sections) + '</nav></details>'
    # Title and intro first, then the overview, recording and table of contents, then the lesson body.
    cut = rendered.find('<h2')
    intro, rest = (rendered[:cut], rendered[cut:]) if cut >= 0 else (rendered, '')
    t = TRACKS[l['track']]
    pos = t['codes'].index(l['code']) + 1
    kicker = f'<div class="lesson-kicker"><span>{t["name"]} · 第 {pos} / {len(t["codes"])} 课</span><span class="done-flag" hidden>✓ 已学完</span></div>'
    done = '<div class="mark-done"><button type="button" id="mark-done" aria-pressed="false">标记本课已学完</button><span>进度只保存在当前浏览器里。</span></div>'
    body = (f'<header class="site-header">{brand("../课程目录.html")}<nav aria-label="主导航"><a href="../课程目录.html">课程目录</a>'
            f'<a href="../{url(PACK_NAME)}" download>下载练习包</a><a href="{url(l["path"].name)}" download>下载本课 Markdown</a></nav></header>'
            f'<div class="lesson-layout"><aside class="sidebar">{sidebar(l)}</aside><main id="main" class="lesson">{kicker}'
            f'<article>{intro}{overview(l)}{recording(l)}{toc}{rest}</article>{done}{pager(l["code"])}'
            f'<footer class="lesson-footer">练习素材与结果文件均可通过本课链接打开。医学示范内容请按其来源和使用范围核对。</footer></main></div>')
    (SITE / '课程' / l['html']).write_text(shell(l['title'], body, '../', 'lesson-page', l['code']))

(SITE / '课程目录.html').write_text(catalog())
(ROOT / 'index.html').write_text(catalog('WorkBuddy教程/'))
(ROOT / '.nojekyll').write_text('')
# Machine-readable public navigation, without local paths or production state.
(SITE / 'assets/courses.json').write_text(json.dumps(
    [{'code': l['code'], 'title': l['display'], 'url': '课程/' + l['html']} for l in lessons], ensure_ascii=False, indent=2))
print(f'Built {len(lessons)} lessons, course directory and practice pack ({pack_label})')
