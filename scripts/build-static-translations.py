#!/usr/bin/env python3
import argparse, html, json, shutil, tempfile, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SKIP={'script','style','code','pre','svg','math','noscript'}
LOCALES={'pt-BR':'pt-br','es':'es','zh-CN':'zh-cn','ja':'ja'}
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=False); self.out=[]; self.text=[]; self.skip=0; self.feed(s); self.close()
 def handle_starttag(self,t,a):
  self.out.append(self.get_starttag_text()); self.skip+=1 if t.lower() in SKIP else 0
 def handle_startendtag(self,t,a): self.out.append(self.get_starttag_text())
 def handle_endtag(self,t):
  self.out.append('</'+t+'>'); self.skip=max(0,self.skip-(1 if t.lower() in SKIP else 0))
 def handle_data(self,d):
  if self.skip or not d.strip() or len(d.strip())<2: self.out.append(d)
  else:
   i=len(self.text); self.text.append(d); self.out.append('\x00I18N'+str(i)+'\x00')
 def handle_entityref(self,n): self.out.append('&'+n+';')
 def handle_charref(self,n): self.out.append('&#'+n+';')
 def handle_comment(self,d): self.out.append('<!--'+d+'-->')
 def handle_decl(self,d): self.out.append('<!'+d+'>')
 def render(self,vals):
  s=''.join(self.out)
  for i,v in enumerate(vals): s=s.replace('\x00I18N'+str(i)+'\x00',html.escape(v,quote=False))
  return s
class Translate:
 def __init__(self,c): self.c=c
 def batch(self,items,lang):
  q=[('client','gtx'),('sl','en'),('tl',lang),('dt','t')]+[('q',x) for x in items]
  req=Request('https://translate.googleapis.com/translate_a/single?'+urlencode(q),headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
  for n in range(3):
   try:
    with urlopen(req,timeout=25) as f: data=json.loads(f.read().decode())
    groups=data[0]; groups=[groups] if len(items)==1 else groups
    vals=[''.join(x[0] for x in g if isinstance(x,list) and x and x[0]) for g in groups[:len(items)]]
    if len(vals)==len(items) and all(vals): return vals
   except Exception:
    if n==2: return items
    time.sleep(n+1)
  return items
 def run(self,items,lang):
  out=[None]*len(items); todo=[]; pos=[]
  for i,s in enumerate(items):
   k=lang+'|'+s
   if k in self.c: out[i]=self.c[k]
   else: todo.append(s); pos.append((i,k))
  for off in range(0,len(todo),10):
   batch=todo[off:off+10]; vals=self.batch(batch,lang)
   for j,(i,k) in enumerate(pos[off:off+10]):
    out[i]=vals[j]
    if vals[j]!=batch[j]: self.c[k]=vals[j]
  return out

def main():
 p=argparse.ArgumentParser(); p.add_argument('site_dir',type=Path); a=p.parse_args(); root=a.site_dir.resolve()
 cachefile=root.parent/'.translation-cache.json'
 try: cache=json.loads(cachefile.read_text())
 except Exception: cache={}
 tr=Translate(cache); files=list(root.rglob('*.html'))
 for lang,folder in LOCALES.items():
  with tempfile.TemporaryDirectory() as td:
   stage=Path(td)/folder; shutil.copytree(root,stage,ignore=shutil.ignore_patterns(*LOCALES.values(),'.git','node_modules','dist'))
   for src in files:
    rel=src.relative_to(root)
    if 'admin' in rel.parts: continue
    dst=stage/rel
    if not dst.exists(): continue
    page=Page(src.read_text(encoding='utf-8')); vals=tr.run(page.text,lang.split('-')[0]); result=page.render(vals)
    result=result.replace('<html lang="en-US">','<html lang="'+lang+'" data-static-locale="'+folder+'">',1)
    dst.write_text(result,encoding='utf-8')
   target=root/folder
   if target.exists(): shutil.rmtree(target)
   shutil.copytree(stage,target)
  print('Created',lang,'static pages')
 cachefile.write_text(json.dumps(tr.c,ensure_ascii=False,separators=(',',':')))
if __name__=='__main__': main()
