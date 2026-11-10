from pathlib import Path
from bs4 import BeautifulSoup
import re,json
root=Path(__file__).parent
source=root/'source.html'
if not source.exists(): source.write_text((root/'index.html').read_text())
original=BeautifulSoup(source.read_text(),'html.parser')
ids=['home','about','services','experience','insights','team','contact']
base='https://www.hadleyconsulting.global'
urls={k:'/' if k=='home' else '/'+k+'/' for k in ids}
for key in ids:
 s=BeautifulSoup(source.read_text(),'html.parser')
 for section in s.select('body > .page'):
  if section.get('id')!=key:section.decompose()
  else:
   section['class']=['page','active'];section.name='main';section['tabindex']='-1'
 for a in s.select('a[onclick]'):
  m=re.search(r"go\('([^']+)'\)",a['onclick'])
  if m:a['href']=urls[m[1]];del a['onclick']
 for im in s.select('img[src]'):
  if im['src'].startswith('assets/'):im['src']='/'+im['src']
 for a in s.select('.nav-links a,.mobile-menu a'):
  if a.get('href')==urls[key]:a['aria-current']='page'
 burger=s.select_one('.nav-burger')
 if burger:burger['role']='button';burger['tabindex']='0';burger['aria-label']='Toggle navigation';burger['aria-controls']='mobileMenu';burger['aria-expanded']='false'
 for script in s.body.find_all('script'):
  js=script.string or ''
  start=js.find('window.addEventListener("scroll"')
  if start>=0:
   js=js[start:];js=js.replace('document.getElementById("mobileMenu").classList.toggle("open");','const open = document.getElementById("mobileMenu").classList.toggle("open"); document.getElementById("burger").setAttribute("aria-expanded", String(open));')
   js+='\ndocument.getElementById("burger").addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();toggleMobile();}});\n'
   script.string=js
 title=s.title.get_text() if key=='home' else key.title()+' | Hadley Consulting'
 s.title.string=title
 content=s.select_one('main');para=content.find('p');desc=para.get_text(' ',strip=True) if para else s.find('meta',attrs={'name':'description'})['content']
 desc=desc[:200]
 s.find('link',rel='canonical')['href']=base+urls[key]
 for attr,name,value in [('name','description',desc),('property','og:url',base+urls[key]),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc)]:
  s.find('meta',attrs={attr:name})['content']=value
 h=content.find('h1')
 if h is None:
  h=content.find(['h2','h3'])
  if h:h.name='h1'
 schema=s.new_tag('script',type='application/ld+json');schema.string=json.dumps({'@context':'https://schema.org','@type':'ContactPage' if key=='contact' else 'AboutPage' if key in ['about','team'] else 'WebPage','@id':base+urls[key]+'#webpage','url':base+urls[key],'name':title,'description':desc,'isPartOf':{'@id':base+'/#website'},'about':{'@id':base+'/#organization'}});s.head.append(schema)
 path=root/('index.html' if key=='home' else key+'/index.html');path.parent.mkdir(exist_ok=True);path.write_text(str(s))
 assert content.get_text(' ',strip=True)==original.find(id=key).get_text(' ',strip=True),key+' copy changed'
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+base+urls[k]+'</loc></url>' for k in ids)+'</urlset>\n')
print('Generated 7 pages; all page text matches source exactly.')
