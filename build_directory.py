"""Regenerate directory.html from the embedded manuscript metadata in index.html."""

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
source = (ROOT / "index.html").read_text(encoding="utf-8")
match = re.search(r'<script type="application/json" id="d">(.*?)</script>', source, re.S)
if not match:
    raise SystemExit("Cannot find manuscript metadata in index.html")
data = json.loads(match.group(1))
categories = data["dims"]["big"]
entries = [
    {"id": i, "title": item[0], "category": item[3], "words": item[6], "summary": item[10]}
    for i, item in enumerate(data["items"])
]
payload = json.dumps({"categories": categories, "entries": entries}, ensure_ascii=False, separators=(",", ":"))
payload = payload.replace("<", "\\u003c")

template = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="鹏基石材视频文稿目录，按主题浏览全部文稿。">
<title>文稿目录 · 鹏基石材</title>
<style>
:root{--bg:#f4f5f7;--panel:#fff;--line:#e5e7eb;--tx:#1f2328;--muted:#66717d;--accent:#2b5cd9}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.65 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
a{color:inherit;text-decoration:none}
button,input{font:inherit}
.wrap{max-width:1120px;margin:auto;padding:0 26px 80px}
header{position:sticky;top:0;z-index:2;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}
header .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:12px;padding-bottom:12px}
.brand{font-weight:700;font-size:17px}
.brand span{color:var(--accent)}
.back{padding:7px 12px;border:1px solid var(--line);border-radius:8px;color:var(--muted);font-size:13px;white-space:nowrap}
.back:hover{color:var(--accent);border-color:var(--accent)}
.hero{padding:44px 0 24px}
.eyebrow{color:var(--accent);font-size:12px;font-weight:700;letter-spacing:.1em}
h1{font-size:32px;line-height:1.25;margin:8px 0}
.intro{color:var(--muted);margin:0 0 22px}
.search{display:block;width:100%;max-width:520px;padding:12px 15px;border:1px solid #d6dce4;border-radius:10px;background:#fff;outline:none}
.search:focus{border-color:var(--accent);box-shadow:0 0 0 3px #eaf0ff}
.quick{display:flex;flex-wrap:wrap;gap:8px;margin:25px 0 0}
.quick a{display:inline-flex;gap:8px;align-items:center;background:#fff;border:1px solid var(--line);padding:7px 12px;border-radius:99px;font-size:13px}
.quick a:hover{color:var(--accent);border-color:var(--accent)}
.quick small{color:#87919c;font-size:12px}
.section{scroll-margin-top:82px;margin-top:28px}
.section-head{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}
.section h2{font-size:21px;margin:0}
.section-head span{font-size:13px;color:var(--muted)}
.entries{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.entry{display:flex;gap:12px;min-width:0;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:15px 16px;transition:border-color .15s,box-shadow .15s}
.entry:hover,.entry:focus-visible{border-color:#91a8ec;box-shadow:0 3px 16px rgba(30,50,90,.07);outline:none}
.num{flex:none;color:#9aa4af;font-size:12px;font-variant-numeric:tabular-nums;min-width:25px;padding-top:3px}
.entry-body{min-width:0}
.entry-title{font-weight:650;line-height:1.5}
.entry-meta{font-size:12px;color:#8b95a1;margin-top:4px}
.entry-summary{font-size:13px;color:var(--muted);margin-top:7px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.empty{padding:55px 0;color:var(--muted);text-align:center}
footer{margin-top:42px;color:#8b95a1;font-size:12px;text-align:center}
@media(max-width:700px){.wrap{padding-left:16px;padding-right:16px}.hero{padding-top:28px}h1{font-size:27px}.entries{grid-template-columns:1fr}.section{scroll-margin-top:74px}.entry{padding:14px}.quick{gap:7px}.quick a{padding:6px 10px}}
</style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="index.html">鹏基石材 <span>· 文稿库</span></a><a class="back" href="index.html">查看全部文稿 →</a></div></header>
<main class="wrap">
  <div class="hero">
    <div class="eyebrow">PENGJI STONE · CONTENT INDEX</div>
    <h1>文稿目录</h1>
    <p class="intro">按主题浏览 <strong id="shown">__COUNT__</strong> 篇视频文稿，点击标题直接阅读。</p>
    <input id="search" class="search" type="search" placeholder="搜索文稿标题或摘要" aria-label="搜索目录" autocomplete="off">
    <nav class="quick" id="quick" aria-label="跳转主题"></nav>
  </div>
  <div id="catalog"></div>
  <footer>鹏基石材 · 视频文稿库</footer>
</main>
<script type="application/json" id="catalogData">__DATA__</script>
<script>
"use strict";
const {categories,entries}=JSON.parse(document.getElementById("catalogData").textContent);
const escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const input=document.getElementById("search");
function render(){
  const term=input.value.trim().toLocaleLowerCase();
  const matched=entries.filter(e=>!term||(e.title+" "+e.summary+" "+categories[e.category]).toLocaleLowerCase().includes(term));
  document.getElementById("shown").textContent=matched.length;
  let nav="",html="";
  categories.forEach((category,i)=>{
    const group=matched.filter(e=>e.category===i);
    if(!group.length)return;
    nav+='<a href="#category-'+i+'">'+escapeHTML(category)+' <small>'+group.length+'</small></a>';
    html+='<section class="section" id="category-'+i+'"><div class="section-head"><h2>'+escapeHTML(category)+'</h2><span>'+group.length+' 篇</span></div><div class="entries">';
    group.forEach((e,k)=>{
      html+='<a class="entry" href="index.html?article='+e.id+'" aria-label="阅读 '+escapeHTML(e.title)+'"><span class="num">'+String(k+1).padStart(2,"0")+'</span><span class="entry-body"><span class="entry-title">'+escapeHTML(e.title)+'</span><span class="entry-meta">'+Number(e.words).toLocaleString("zh-CN")+' 字</span>'+(e.summary?'<span class="entry-summary">'+escapeHTML(e.summary)+'</span>':'')+'</span></a>';
    });
    html+='</div></section>';
  });
  document.getElementById("quick").innerHTML=nav;
  document.getElementById("catalog").innerHTML=html||'<div class="empty">没有找到相关文稿，请换一个关键词。</div>';
}
input.addEventListener("input",render);
render();
</script>
</body>
</html>
'''

(ROOT / "directory.html").write_text(
    template.replace("__COUNT__", str(len(entries))).replace("__DATA__", payload), encoding="utf-8"
)
print(f"Generated directory.html with {len(entries)} manuscripts in {len(categories)} categories")
