"""Build the static course site from the maintained Markdown lessons."""
from pathlib import Path
import html, json, re
from urllib.parse import quote
import mistune
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'WorkBuddy教程'
ORDER=['00','01']+[f'R{i}' for i in range(1,9)]+[f'P{i}' for i in range(1,10)]
GROUPS=[('start','从这里开始','认识工作空间、技能与课程里的核对方法。',ORDER[:2]),('research','医学科研线','从文献与问题出发，完成方案、分析、写作和协作。',ORDER[2:10]),('public','患者科普线','从患者问题出发，把同一份证据转成清楚、可核对的内容。',ORDER[10:])]
FOCUS={
'00':'了解完整路线，选择你的第一项练习。','01':'建立工作空间，导入技能，核对第一条医学论断。',
'R1':'组织 PICO、检索文献，区分研究结论与外推。','R2':'逐条核对论断、摘要与引用，留下证据位置。','R3':'草拟研究方案和 SAP，运行样本量计算。','R4':'从数据体检到清洗日志、模型与置信区间。','R5':'对照结果写作，按立场逐条回应审稿意见。','R6':'把研究目标、技术路线、周期和资源放在一起核对。','R7':'把组会转写整理成纪要、负责人和进度表。','R8':'提炼审稿回复规则，导入技能并检验边界。',
'P1':'从模拟对标资料里确定受众、定位和内容支柱。','P2':'合并患者问法，保留来源，形成可排序的选题库。','P3':'以事实卡为基础写文章，逐句保留来源与限定。','P4':'把一个主题拆成 30 秒脚本和分镜。','P5':'生成六页图文与竖版海报，逐页检查版式。','P6':'检查口播稿、形象参考、语音试听和字幕。','P7':'制作患教单与随访话术，用回授发现歧义。','P8':'同一组事实卡生成四类内容，逐句检查一致性。','P9':'把风格和核对规则固化为可复用的技能。'}
md=mistune.create_markdown(plugins=['table','strikethrough','task_lists','url'])
lessons=[]
for code in ORDER:
 p=next((SITE/'课程').glob(code+'-*.md'))
 text=p.read_text();title=text.splitlines()[0].lstrip('# ')
 display=re.sub(r'^(?:'+re.escape(code)+r'|入门课)\s*','',title)
 video=SITE/'录屏'/f'{code}-WorkBuddy实操.mp4'
 meta=json.loads(video.with_suffix('.json').read_text())
 lessons.append(dict(code=code,path=p,text=text,title=title,display=display,video=video,meta=meta))

def esc(s):return html.escape(str(s),quote=True)
def url(p):return quote(str(p),safe='/')
def shell(title,body,prefix='',bodyclass=''):
 return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="医学科研与患者科普 WorkBuddy 实操课程。19 节教程，配套提示词、录屏、截图和练习文件。"><meta name="theme-color" content="#173e32"><title>{esc(title)} · 医学工作流课堂</title><link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body class="{bodyclass}"><a class="skip-link" href="#main">跳到正文</a>{body}</body></html>'''
def brand(home):return f'<a class="brand" href="{home}"><span class="brand-icon" aria-hidden="true">M</span><span>医学工作流课堂<small>WorkBuddy 实操教程</small></span></a>'
def course_link(l,prefix=''):return prefix+'课程/'+url(l['path'].with_suffix('.html').name)
def catalog(prefix=''):
 rows=[]
 for gid,name,desc,codes in GROUPS:
  cards=[]
  for l in lessons:
   if l['code'] not in codes:continue
   cards.append(f'''<a class="course-row" data-course="{esc(l['code']+' '+l['display']+' '+FOCUS[l['code']])}" href="{course_link(l,prefix)}"><span class="course-code">{l['code']}</span><span class="course-text"><strong>{esc(l['display'])}</strong><span>{FOCUS[l['code']]}</span></span><span class="course-arrow" aria-hidden="true">↗</span></a>''')
  rows.append(f'<section class="course-group" id="{gid}"><div class="section-heading"><div><span class="eyebrow">{len(codes):02} LESSONS</span><h2>{name}</h2></div><p>{desc}</p></div><div class="course-list">'+''.join(cards)+'</div></section>')
 first=next(l for l in lessons if l['code']=='01')
 body=f'''<header class="site-header">{brand(prefix+'课程目录.html')}<nav aria-label="主导航"><a href="#research">科研线</a><a href="#public">科普线</a><a href="https://github.com/JuneYaooo/medical-teach">GitHub ↗</a></nav></header>
<main id="main" class="home"><section class="hero"><div><p class="eyebrow">MEDICINE · RESEARCH · COMMUNICATION</p><h1>让医学工作流<br>可复现、可核对。</h1><p class="hero-lead">从一份资料到一个可检查的结果。跟着 WorkBuddy 的真实操作，把文献、数据、写作与患者科普，一步一步做清楚。</p><a class="primary" href="{course_link(first,prefix)}">开始入门课 <span aria-hidden="true">→</span></a><p class="hero-meta">19 节课程 · 19 段实操录屏 · 84 张操作截图</p></div><aside class="learning-note"><p class="eyebrow">每一课，都走完整条路径</p><ol><li><span>01</span><div><strong>准备资料</strong><p>下载练习文件，确认来源与适用范围。</p></div></li><li><span>02</span><div><strong>跟着操作</strong><p>复制提示词，对照截图和实操片段。</p></div></li><li><span>03</span><div><strong>打开结果</strong><p>查看真实文件，核对数字、出处与表述。</p></div></li><li><span>04</span><div><strong>修改与复用</strong><p>把发现的问题带回流程，再做一次。</p></div></li></ol></aside></section>
<div class="catalog-tools"><div><p class="eyebrow">COURSE DIRECTORY</p><h2>选一条路线，开始练习</h2></div><label class="search-label">查找课程<input id="course-search" type="search" placeholder="课程名、编号或关键词" autocomplete="off"></label></div>
<p id="search-empty" hidden>没有匹配的课程，请试试“数据”“科普”或课程编号。</p>{''.join(rows)}
<aside class="scope-note"><strong>关于练习素材</strong><p>统计数据、审稿意见和项目资料为教学模拟；医学事实卡附公开来源，来源核对不等于医生审核。录屏是无旁白的实操节选，完整提示词见各课正文。P6 的已有形象样片与本课新稿试听分别标明。</p></aside></main><footer class="site-footer"><span>医学工作流课堂 · 按步骤学习，依据结果核对。</span><a href="https://github.com/JuneYaooo/medical-teach">查看 Markdown 与课程文件 ↗</a></footer>'''
 return shell('课程目录',body,prefix,'home-page')

for i,l in enumerate(lessons):
 rendered=md(l['text'])
 rendered=re.sub(r'<img ', '<img loading="lazy" decoding="async" ',rendered)
 # Stable section anchors and a compact, keyboard-accessible table of contents.
 sections=[]
 def heading(m):
  label=re.sub('<[^>]+>','',m.group(1));anchor='section-'+str(len(sections)+1);sections.append((anchor,label))
  return f'<h2 id="{anchor}">{m.group(1)}</h2>'
 rendered=re.sub(r'<h2>(.*?)</h2>',heading,rendered,flags=re.S)
 toc='<details class="page-toc"><summary>本课目录</summary><nav aria-label="本课目录">'+''.join(f'<a href="#{a}">{t}</a>' for a,t in sections)+'</nav></details>'
 sidebar='<details class="course-nav" open><summary>全部课程</summary><nav aria-label="课程导航">'
 for _,gname,_,codes in GROUPS:
  sidebar+=f'<p>{gname}</p>'
  for item in lessons:
   if item['code'] in codes:
    sidebar+=f'<a href="{url(item["path"].with_suffix(".html").name)}"'+(' aria-current="page"' if item==l else '')+f'><span>{item["code"]}</span>{esc(item["display"])}</a>'
 sidebar+='</nav></details>'
 chapters=l['meta']['chapters']
 video=f'<section id="recording" class="recording"><p class="eyebrow">WATCH THE WORKFLOW</p><h2>实操录屏</h2><p>按下面的操作阶段跳转；完整输入和核对方法保留在正文中。</p><video id="lesson-video" controls playsinline preload="metadata" aria-label="{l["code"]} WorkBuddy 实操录屏"><source src="../录屏/{url(l["video"].name)}" type="video/mp4"></video><div class="chapters" aria-label="录屏章节">'
 for ch in chapters:
  start=ch['start'];video+=f'<button type="button" data-seek="{start}"><span>{int(start)//60:02}:{int(start)%60:02}</span>{esc(ch["title"])}</button>'
 video+='</div><script type="application/json" id="video-chapters">'+json.dumps(chapters,ensure_ascii=False).replace('</', '<' + chr(92) + '/')+'</script></section>'
 prev=lessons[i-1] if i else None;nxt=lessons[i+1] if i+1<len(lessons) else None
 pager='<nav class="lesson-pager" aria-label="前后课">'
 for item,label in [(prev,'上一课'),(nxt,'下一课')]:
  if item:pager+=f'<a href="{url(item["path"].with_suffix(".html").name)}"><span>{label} · {item["code"]}</span><strong>{esc(item["display"])}</strong></a>'
  else:pager+='<a href="../课程目录.html"><span>课程目录</span><strong>选择另一条学习路线</strong></a>'
 pager+='</nav>'
 body=f'<header class="site-header">{brand("../课程目录.html")}<nav aria-label="主导航"><a href="../课程目录.html">课程目录</a><a href="#recording">看录屏</a><a href="{url(l["path"].name)}" download>下载 Markdown</a></nav></header><div class="lesson-layout"><aside class="sidebar">{sidebar}</aside><main id="main" class="lesson"><div class="lesson-kicker"><span>LESSON {l["code"]}</span><span>{i+1} / 19</span></div>{toc}<article>{rendered}</article>{video}{pager}<footer class="lesson-footer">练习素材与结果文件均可通过本课链接打开。医学示范内容请按其来源和使用范围核对。</footer></main></div>'
 l['path'].with_suffix('.html').write_text(shell(l['title'],body,'../','lesson-page'))
(SITE/'课程目录.html').write_text(catalog())
(ROOT/'index.html').write_text(catalog('WorkBuddy教程/'))
(ROOT/'.nojekyll').write_text('')
# Machine-readable public navigation, without local paths or production state.
(SITE/'assets/courses.json').write_text(json.dumps([{'code':l['code'],'title':l['display'],'url':'课程/'+l['path'].with_suffix('.html').name} for l in lessons],ensure_ascii=False,indent=2))
print(f'Built {len(lessons)} lessons and course directory')
