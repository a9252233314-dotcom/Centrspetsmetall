"""Publish the original B01 study with shared catalog navigation and metadata."""
from pathlib import Path
from html import escape
import hashlib,json,re
from analytics import with_metrika

def build_stove_page(site,product):
    root=site['ROOT'];path=site['route'](product);url=site['absolute'](path)
    html=(root/'stove.template.html').read_text(encoding='utf-8')
    css=hashlib.sha256((root/'stove-viewer.js').read_bytes()).hexdigest()[:10]
    desc=product['description'];title='Банная чугунная печь Б01 с каменкой и сеткой — проект ЦЕНТРСПЕЦМЕТАЛЛ'
    meta=f'<meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{escape(desc,quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{site["absolute"](product["image"])}"><link rel="icon" href="../../assets/csm-logo.png"><meta name="robots" content="index,follow,max-image-preview:large">'
    schema={'@context':'https://schema.org','@type':'CreativeWork','name':product['name'],'description':desc,'url':url,'image':site['absolute'](product['image']),'inLanguage':'ru-RU','creator':{'@type':'Organization','name':site['NAME'],'url':site['BASE']}}
    html=html.replace('<title>Б01 — чугунная банная печь · проект ЦСМ</title>',f'<title>{title}</title>'+meta+'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>')
    html=html.replace('<html lang="ru"><meta','<html lang="ru"><head><meta',1).replace('</style>','</style></head><body>',1)
    html=re.sub(r'<header>.*?</header>','''<header><a class="wordmark" href="../../" style="text-decoration:none"><span>ЦСМ</span>ЦЕНТРСПЕЦМЕТАЛЛ</a><nav aria-label="Навигация" style="display:flex;gap:20px;flex-wrap:wrap;font-size:12px"><a href="../../catalog/chugunnye-pechi/">Все печи</a><a href="../../catalog/">Каталог</a><a href="../../contacts/">Контакты</a></nav></header>''',html,count=1)
    html=html.replace('<h1>Одна основа.<br><span>Три исполнения.</span></h1>','<h1>Банная печь Б01.<br><span>Три исполнения.</span></h1>')
    html=html.replace('src="output/basket.png"','src="../../assets/stoves/b01/basket.webp"')
    html=html.replace('href="output/csm-b01.glb"','href="../../assets/stoves/b01/csm-b01.glb"')
    html=html.replace('<a class="secondary-link" href="output/csm-b01.blend" download>Исходная сцена Blender</a>','<a class="secondary-link" href="mailto:'+site['EMAIL']+'?subject=Банная%20печь%20Б01">Обсудить проект по почте</a><br><a class="secondary-link" href="tel:+79263910655">+7 (926) 391-06-55 · Роберт</a>')
    html=html.replace('В GLB сохранено исполнение с корзиной. В Blender доступны все три варианта. Используйте кнопки для сравнения.','В GLB сохранено исполнение с корзиной. Для сравнения вариантов используйте кнопки выше. Изготовление обсуждается после разработки конструкции.')
    html=html.replace('Б01 — собственный компоновочный эскиз ЦЕНТРСПЕЦМЕТАЛЛ. Референс направления: банные печи «Техно Лит». Фотографии и названия чужих моделей в визуализациях не используются.','Б01 — собственный компоновочный эскиз ЦЕНТРСПЕЦМЕТАЛЛ. Производство — Тула. Обсуждаем разработку банных печей и литых деталей по согласованному заданию.')
    html=html.replace('<script id="geometry" type="application/json">__GEOMETRY__</script><script src="viewer.js"></script></html>',f'<script id="geometry" type="application/json" data-src="../../assets/stoves/b01/geometry.json"></script><script src="../../stove-viewer.js?v={css}"></script></body></html>')
    html=html.replace('ЦЕНТРСПЕЦМЕТАЛЛ',site['NAME']).replace('ЦСМ</span>','ТЛМ</span>')
    html=html.replace('<span>ТЛМ</span>', '<img src="../../assets/tlm-logo.svg" width="48" height="51" alt="" style="object-fit:contain;flex-shrink:0">')
    html=html.replace('assets/csm-logo.png','assets/tlm-logo.svg')
    html=html.replace('.wordmark{font-size:16px;', '.wordmark{display:flex;align-items:center;gap:12px;max-width:400px;font-size:15px;')
    html=html.replace('МЕТАЛЛ Производство', 'МЕТАЛЛ. Производство')
    html=html.replace('</footer>', '<a href="../../requisites/" style="display:block;margin-bottom:20px;font-size:12px">Реквизиты ООО «Сфералит» ↗</a></footer>')
    target=root/path/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(with_metrika(html),encoding='utf-8');site['PAGES'].append(path)
