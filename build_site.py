"""Build crawlable static pages from the real product catalog. Python 3, Pillow."""
from pathlib import Path
from html import escape
from functools import lru_cache
from PIL import Image
import json, hashlib
from bench_catalog import BENCHES, BENCH_ROUTE, prepare_assets, bench_cards, teaser as bench_teaser, build_benches

ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT/'site.config.json').read_text(encoding='utf-8'))
PRODUCTS=json.loads((ROOT/'products.json').read_text(encoding='utf-8'))
DIRECTIONS=json.loads((ROOT/'directions.json').read_text(encoding='utf-8'))
SERVICES=json.loads((ROOT/'services.json').read_text(encoding='utf-8'))
CSS_VERSION=hashlib.sha256((ROOT/'modern.css').read_bytes()).hexdigest()[:10]
JS_VERSION=hashlib.sha256((ROOT/'modern.js').read_bytes()).hexdigest()[:10]
BENCH_CSS_VERSION=hashlib.sha256((ROOT/'bench-catalog.css').read_bytes()).hexdigest()[:10]
BASE=CONFIG['canonicalBase'].rstrip('/')+'/'
NAME=CONFIG['name']; EMAIL=CONFIG['email']
SLUGS={'bowl-classic':'kostrovaya-chasha','bowl-decor':'chasha-na-figurnyh-oporah','stove':'chugunnaya-pech','castings':'litye-detali-i-zagotovki','grill-ring':'koltso-stoleshnitsa-s-reshetkoy','stand':'litaya-podstavka-pod-chashu','pattern':'modelnaya-osnastka','decor-elephant':'figura-slon','decor-wolf':'figura-volk','decor-panels':'dekorativnye-paneli','mangal-relief':'mangal-s-relefom','gazebo':'besedka-s-ochagom'}
CATEGORIES={
 'fire':{'slug':'kostrovye-chashi','name':'Чаши и мангалы','title':'Костровые чаши, мангалы и комплектующие','text':'Костровые чаши, фигурные опоры, кольца и решётки для места отдыха на участке. В каталоге — примеры исполнения. Размер, материал, состав комплекта и стоимость согласуем под вашу задачу.','icon':'bowl'},
 'stoves':{'slug':'chugunnye-pechi','name':'Чугунные печи','title':'Чугунные печи и литые элементы','text':'Изготовление чугунных печей и отдельных литых деталей по согласованному исполнению. Посмотрите фотографии образцов и расскажите, какое изделие вам нужно.','icon':'stove'},
 'decor':{'slug':'dekor-iz-metalla','name':'Декор и орнаменты','title':'Художественный декор и модели изделий','text':'Орнаментальные панели, художественные элементы и сборные модели фигур. Обсуждаем изготовление в металле по образцу или эскизу. Слон и волк на фотографиях представлены как модели.','icon':'decor'},
 'industry':{'slug':'lityo-na-zakaz','name':'Литьё на заказ','title':'Литьё деталей и модельная оснастка на заказ','text':'Промышленные и художественные отливки по чертежам, эскизам и образцам. Работаем с чугуном, сталью и цветными сплавами. Технологию и возможность изготовления подтверждаем по конкретному заданию.','icon':'casting'},
 'projects':{'slug':'kostrovye-zony','name':'Костровые зоны','title':'Костровые зоны и беседки с очагом','text':'Развиваем сборную беседку с центральным очагом как отдельный проект. Здесь можно познакомиться с концепцией и обсудить будущую комплектацию. Серийный готовый комплект пока не предлагается.','icon':'gazebo'}
}
FUTURE=[
 ('lamp','Уличные фонари','Рассматриваем декоративные опоры и литые элементы светильников. Внешний вид, конструкцию и состав электрической части предстоит согласовать.'),
 ('bench','Чугунные скамейки','Направление для садов, парков и частных территорий: литые боковины и опоры, сочетание с сиденьем и спинкой по проекту.'),
 ('manhole','Люки и крышки','Рассматриваем изготовление по чертежам и назначению. Конструкция, нагрузка, маркировка и требования к испытаниям определяются для конкретного изделия.'),
 ('gazebo','Беседки и костровые зоны','Сборные конструкции с чашей или печью. Компоновку, устойчивость, крепления и условия установки прорабатываем в отдельном проекте.'),
 ('tile','Чугунная плитка','Обсуждаем рельеф, размеры и применение плитки. Основание, крепления и характеристики поверхности определяются под место установки.')
]
FAQ=[
 ('Можно заказать одно изделие?','Укажите нужное количество в заявке. Возможность единичного изготовления или партии, стоимость и срок рассчитываем под конкретное изделие.'),
 ('Почему в каталоге нет фиксированной цены?','На стоимость влияют размер, материал, оснастка, покрытие и комплект поставки. После уточнения задания согласуем цену и срок изготовления.'),
 ('Можно сделать по моему эскизу или фотографии?','Да, начать обсуждение можно с чертежа, эскиза, фотографии или образца. Для расчёта уточним геометрию, материал, количество и требования к результату.'),
 ('Как согласовать доставку?','Сообщите город получения и желаемый способ передачи. Упаковку, перевозку, стоимость и сроки доставки согласуем отдельно при расчёте заказа.'),
 ('Что изображено на фотографиях декора?','Слон и волк — сборные модели для обсуждения металлического исполнения. Фотографии панелей и остальных изделий показывают примеры; комплектность и наличие уточняются по заявке.')
]
PAGES=[]
def e(value):return escape(str(value),quote=True)
def absolute(path=''):return BASE+path.lstrip('/')
def route(p):return 'products/'+SLUGS[p['id']]+'/'
def catroute(key):return 'catalog/'+CATEGORIES[key]['slug']+'/'
def tel(number):return '+'+''.join(c for c in number if c.isdigit())
def icon(name):
    paths={
      'bowl':'<path d="M3 10h26c-1 8-6 11-13 11S4 18 3 10Z"/><path d="M9 21v5m14-5v5M13 6c-3-3 3-3 0-6m6 6c-3-3 3-3 0-6"/>',
      'stove':'<rect x="8" y="6" width="17" height="22" rx="3"/><path d="M13 6V2h7v4M8 20h17M12 10h9v7h-9zm0 14h8M10 28v3m12-3v3"/>',
      'decor':'<path d="m16 2 14 14-14 14L2 16 16 2Z"/><path d="m16 8 8 8-8 8-8-8 8-8Zm0 5v6m-3-3h6"/>',
      'casting':'<path d="M5 10h22v18H5zM9 10V5h14v5M5 16h22M11 16v12m10-12v12M2 28h28"/>',
      'lamp':'<path d="M16 29V13M8 29h16M10 13h12l-2-9h-8l-2 9ZM8 4h16M16 1v3"/>',
      'bench':'<path d="M4 5h24v12H4zM2 21h28M7 21v8m18-8v8M4 11h24M7 17v4m18-4v4"/>',
      'manhole':'<ellipse cx="16" cy="16" rx="14" ry="10"/><ellipse cx="16" cy="16" rx="10" ry="6"/><path d="M8 13h16M7 17h18M12 10v12m8-12v12"/>',
      'gazebo':'<path d="m2 12 14-10 14 10H2Zm4 0v17m20-17v17M4 29h24M11 21h10M12 21v6m8-6v6"/>',
      'tile':'<rect x="3" y="3" width="26" height="26" rx="2"/><path d="m16 6 10 10-10 10L6 16 16 6Zm-5 10h10m-5-5v10"/>'}
    return '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths.get(name,paths['decor'])+'</svg>'
@lru_cache(maxsize=None)
def size(path):
    if path.endswith('.svg'):return (1000,750)
    with Image.open(ROOT/path) as im:return im.size
def image(path,alt,r='',cls='',priority=False):
    w,h=size(path)
    return f'<img src="{e(r+path)}" alt="{e(alt)}" width="{w}" height="{h}" class="{cls}" '+('fetchpriority="high" loading="eager"' if priority else 'loading="lazy"')+' decoding="async">'
def button(text,request='custom',style='',extra=''):
    return f'<button type="button" class="button {style}" data-request="{e(request)}" {extra}>{e(text)} <span aria-hidden="true">↗</span></button>'
def header(r):
    return f'''<a class="skip" href="#main">Перейти к содержимому</a><header class="site-header"><div class="container header-inner"><a class="brand" href="{r}" aria-label="Центрспецметалл — на главную">{image('assets/csm-logo.png','',r)}<span><strong>ЦЕНТРСПЕЦМЕТАЛЛ</strong><small>Изделия. Литьё. Ваши идеи.</small></span></a><nav class="main-nav" id="main-nav" aria-label="Основная навигация"><a href="{r}catalog/">Каталог</a><a href="{r}production/">Производство</a><a href="{r}blagoustroystvo/">Новые направления</a><a href="{r}contacts/">Контакты</a></nav><div class="header-contact"><a class="phone" href="tel:{tel(CONFIG['phones'][0])}">{e(CONFIG['phones'][0])}</a>{button('Обсудить заказ',style='small')}</div><button class="menu-toggle js-only" id="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Открыть меню">☰</button></div></header>'''
def footer(r):
    cats=''.join(f'<a href="{r}{catroute(key)}">{e(c["name"])}</a>' for key,c in CATEGORIES.items())
    cats+=f'<a href="{r}{BENCH_ROUTE}">Чугунные скамейки</a>'
    return f'''<footer class="site-footer"><div class="container"><div class="footer-main"><div class="footer-about"><a class="brand" href="{r}">{image('assets/csm-logo.png','',r)}<span><strong>ЦЕНТРСПЕЦМЕТАЛЛ</strong><small>Изделия. Литьё. Ваши идеи.</small></span></a><p>Изделия из чугуна, стали и цветных сплавов. От готовой идеи до согласованного заказа.</p></div><nav class="footer-links" aria-label="Каталог в подвале"><strong>Каталог</strong>{cats}</nav><nav class="footer-links" aria-label="О компании"><strong>Полезное</strong><a href="{r}production/">Производственные возможности</a><a href="{r}blagoustroystvo/">Благоустройство и новые идеи</a><a href="{r}delivery/">Заказ и доставка</a><a href="{r}contacts/">Контакты</a><a href="{r}assets/csm-presentation.pdf" target="_blank" rel="noopener">Презентация компании ↗</a></nav><div class="footer-contacts"><a href="tel:{tel(CONFIG['phones'][0])}">{e(CONFIG['phones'][0])}</a><a href="tel:{tel(CONFIG['phones'][1])}">{e(CONFIG['phones'][1])}</a><a class="email" href="mailto:{EMAIL}">{EMAIL}</a><p>Производство — г. {e(CONFIG["city"])}.<br>Расскажите, что хотите изготовить.</p></div></div><div class="footer-bottom"><span>© 2026 ЦЕНТРСПЕЦМЕТАЛЛ</span><span>Цена, срок и комплектация согласуются по заказу.</span><a href="{r}sitemap.xml">Карта сайта</a></div></div></footer><div class="mobile-contact"><a class="button secondary" href="tel:{tel(CONFIG['phones'][0])}">Позвонить</a>{button('Обсудить заказ',style='')}</div>'''
def dialog():
    options=''.join(f'<option value="{e(p["id"])}">{e(p["name"])}</option>' for p in PRODUCTS)
    return f'''<dialog class="request-dialog" id="request-dialog" aria-labelledby="request-title"><button class="dialog-close" type="button" data-close="request-dialog" aria-label="Закрыть заявку">×</button><h2 id="request-title">Обсудим ваше изделие</h2><p>Укажите задачу и контакт для ответа. Сайт подготовит письмо — останется проверить и отправить его из вашей почты.</p><form id="request-form"><div class="form-grid"><label class="full">Что изготовить<select name="product" id="request-product"><option value="custom">Своя задача / изделие по чертежу</option>{options}</select></label><label>Ваше имя<input name="name" id="request-name" autocomplete="name" required maxlength="100" placeholder="Как к вам обращаться"></label><label>Компания<input name="company" id="request-company" autocomplete="organization" maxlength="150" placeholder="Если заказ от организации"></label><label>Телефон<input name="phone" id="request-phone" type="tel" autocomplete="tel" maxlength="50" placeholder="+7 …"></label><label>Электронная почта<input name="email" id="request-email" type="email" autocomplete="email" maxlength="150" placeholder="Для ответа по заказу"></label><label>Количество<input name="quantity" id="request-quantity" maxlength="60" placeholder="Например, 2 шт."></label><label>Материал и размер<input name="material" id="request-material" maxlength="150" placeholder="Если уже определились"></label><label class="full">Опишите задачу<textarea name="message" id="request-message" required maxlength="4000" placeholder="Что нужно изготовить, пожелания, город получения и сроки"></textarea></label></div><p class="form-note">Укажите телефон или почту для ответа. Чертежи и фото прикрепите к письму в своей почте. Эта форма не сохраняет данные на сервере.</p><div class="form-actions"><button class="button" type="submit">Открыть письмо ↗</button><button class="button secondary" id="copy-request" type="button">Скопировать</button><button class="button secondary" id="download-request" type="button">Скачать .txt</button></div><p class="form-status" id="request-status" role="status" aria-live="polite"></p></form></dialog><dialog class="lightbox" id="lightbox" aria-label="Увеличенная фотография"><button type="button" class="dialog-close" data-close="lightbox" aria-label="Закрыть фото">×</button><img id="lightbox-image" alt=""></dialog>'''
def crumbs(r,items):
    result=f'<nav class="container breadcrumbs" aria-label="Хлебные крошки"><a href="{r}">Главная</a>'
    for label,path in items:result+='<span aria-hidden="true">/</span>'+ (f'<a href="{r}{path}">{e(label)}</a>' if path else f'<span aria-current="page">{e(label)}</span>')
    return result+'</nav>'
def page(path,title,description,content,breadcrumbs=None,extra_schema=None,img='assets/catalog/grill-ring.webp',noindex=False):
    if len(description)>175:description=description[:168].rsplit(' ',1)[0].rstrip(',.')+'…'
    r='../'*len(path.strip('/').split('/')) if path else './'
    canonical=absolute(path)
    schema=[{'@type':'Organization','@id':absolute('#organization'),'name':NAME,'url':BASE,'logo':absolute('assets/csm-logo.png'),'email':EMAIL,'telephone':[tel(n) for n in CONFIG['phones']]},{'@type':'WebSite','@id':absolute('#website'),'name':NAME,'url':BASE,'inLanguage':'ru-RU','publisher':{'@id':absolute('#organization')}}]
    schema[0]['address']={'@type':'PostalAddress','addressLocality':CONFIG['city'],'addressRegion':CONFIG['region'],'addressCountry':CONFIG['country']}
    if breadcrumbs:
        entries=[{'@type':'ListItem','position':1,'name':'Главная','item':BASE}]
        for i,(label,link) in enumerate(breadcrumbs,2):entries.append({'@type':'ListItem','position':i,'name':label,'item':absolute(link or path)})
        schema.append({'@type':'BreadcrumbList','itemListElement':entries})
    schema.append({'@type':'WebPage','@id':canonical+'#webpage','url':canonical,'name':title,'description':description,'inLanguage':'ru-RU','isPartOf':{'@id':absolute('#website')}})
    if extra_schema:schema.extend(extra_schema)
    head=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(description)}"><meta name="theme-color" content="#233e32"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-image-preview:large'}"><link rel="canonical" href="{e(canonical)}"><link rel="icon" href="{r}assets/csm-logo.png" type="image/png"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{e(canonical)}"><meta property="og:image" content="{e(absolute(img))}"><meta property="og:image:alt" content="Изделия ЦЕНТРСПЕЦМЕТАЛЛ"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="{r}modern.css?v={CSS_VERSION}"><link rel="stylesheet" href="{r}bench-catalog.css?v={BENCH_CSS_VERSION}"><script src="{r}modern.js?v={JS_VERSION}" defer></script><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':schema},ensure_ascii=False).replace('</','<\\/')}</script></head>'''
    html=head+f'<body data-root="{r}">'+header(r)+(crumbs(r,breadcrumbs) if breadcrumbs else '')+'<main id="main">'+content+'</main>'+footer(r)+dialog()+'</body></html>\n'
    target=ROOT/path/'index.html' if path else ROOT/'index.html'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8')
    if not noindex:PAGES.append(path)
def card(p,r):
    status='model' if p.get('imageCaption') and p['category']=='decor' else ('project' if p['category']=='projects' else '')
    cap=f'<p class="model-caption">{e(p["imageCaption"])}</p>' if p.get('imageCaption') else ''
    return f'''<article class="product-card" data-product-id="{e(p['id'])}" data-search="{e((p['name']+' '+p['categoryLabel']+' '+p['description']).lower())}"><a class="product-media" href="{r}{route(p)}" aria-label="{e(p['name'])}">{image(p['image'],p.get('imageAlt',p['name']),r)}<span class="product-status {status}">{e(p['tag'])}</span></a><div class="product-body"><p class="product-category">{e(p['categoryLabel'])}</p><h3><a href="{r}{route(p)}">{e(p['name'])}</a></h3><p>{e(p['subtitle'])}</p>{cap}<div class="card-foot"><span>{'Проект в разработке' if p['category']=='projects' else 'Стоимость по запросу'}</span><a href="{r}{route(p)}">Подробнее <span aria-hidden="true">↗</span></a></div></div></article>'''
def cards(items,r):return '<div class="product-grid" id="product-grid">'+''.join(card(p,r) for p in items)+'</div>'
def faq(items=FAQ):return '<div class="faq">'+''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in items)+'</div>'
def contact_banner():return f'<div class="container"><section class="contact-banner"><div><h2>Есть идея? Давайте обсудим.</h2><p>Пришлите эскиз, фото или описание. Уточним материал, размер, комплектацию и подготовим расчёт.</p></div>{button("Рассказать о задаче")}</section></div>'
def heading(title,text,eyebrow=''):
    return f'<div class="container page-heading">'+(f'<p class="eyebrow"><i class="dot"></i>{e(eyebrow)}</p>' if eyebrow else '')+f'<h1>{e(title)}</h1><p>{e(text)}</p></div>'
def item_list(items):return {'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'url':absolute(route(p)),'name':p['name']} for i,p in enumerate(items,1)]}
def home():
    r='./'; featured=[next(p for p in PRODUCTS if p['id']==i) for i in ['bowl-classic','bowl-decor','stove','grill-ring','mangal-relief','decor-panels']]
    rail=''.join(f'<a href="{r}{catroute(k)}"><span class="category-icon">{icon(CATEGORIES[k]["icon"])}</span><span><strong>{e(CATEGORIES[k]["name"])}</strong><small>{txt}</small></span></a>' for k,txt in [('fire','Для пространства вокруг огня'),('stoves','Печи и литые элементы'),('decor','Орнаменты и модели'),('industry','По чертежу или образцу')])
    content=f'''<section class="container hero" id="home"><div class="hero-grid"><div class="hero-copy"><div class="eyebrow"><i class="dot"></i>Литейное производство · {e(CONFIG["city"])}</div><h1>Изделия из чугуна<br>и металла.<br><span>Под вашу задачу.</span></h1><p>Костровые чаши, печи, художественный декор и литьё по вашим чертежам. Выберите изделие — обсудим изготовление.</p><div class="hero-actions"><a class="button" href="{r}catalog/">Смотреть каталог <span aria-hidden="true">↗</span></a>{button('Своя идея',style='secondary')}</div><div class="hero-points"><span>По эскизам и образцам</span><span>Чугун, сталь, цветные сплавы</span></div></div><a class="hero-visual" href="{r}products/koltso-stoleshnitsa-s-reshetkoy/"><div class="visual-top"><span>Изделия для вашего пространства</span><span class="round-label">Под заказ</span></div>{image('assets/catalog/grill-ring.webp','Чаша с кольцом-столешницей и решёткой на фигурных опорах',r,priority=True)}<div class="visual-bottom"><div><strong>Огонь собирает своих</strong><small>Чаши и комплектующие для места отдыха</small></div><span class="round-arrow" aria-hidden="true">↗</span></div></a></div></section><div class="container"><nav class="category-rail" aria-label="Направления каталога">{rail}</nav></div><section class="container section" id="catalog"><div class="section-heading"><div><p class="eyebrow">Каталог изделий</p><h2>Вещи с характером.<br>Сделанные из металла.</h2></div><a class="text-link" href="{r}catalog/">Весь каталог · 12 позиций <span aria-hidden="true">↗</span></a></div>{cards(featured,r)}</section><div class="container" id="decor">{directions_home(r)}</div><section class="container section" id="capabilities"><div class="production-grid"><figure class="production-photo">{image('assets/foundry-pour.webp','Заливка металла в форму — фотография из презентации производства',r)}<figcaption>За изделиями — реальные производственные возможности.</figcaption></figure><div class="production-copy"><p class="eyebrow">Производство ЦЕНТРСПЕЦМЕТАЛЛ</p><h2>От вашей идеи<br>до отливки.</h2><p>Промышленные детали, художественные элементы и модельная оснастка. Подбираем сплав, формовку и обработку под конкретное изделие.</p>{service_links(r)}<a class="text-link" href="{r}production/">Узнать о производстве <span aria-hidden="true">↗</span></a></div></div></section><section class="process-section" id="process"><div class="container"><div class="section-heading"><div><p class="eyebrow">Как заказать</p><h2>Начинаем с простого<br>разговора.</h2></div><p>Не обязательно сразу иметь готовый чертёж. Расскажите, что вы хотите получить.</p></div>{process_steps()}</div></section><section class="container section"><div class="faq-grid"><div><p class="eyebrow">Перед заказом</p><h2>Ответы<br>на ваши вопросы.</h2><p>Если задача нестандартная — обсудим детали лично.</p></div>{faq()}</div></section>{contact_banner()}'''
    content=content.replace('Весь каталог · 12 позиций',f'Весь каталог · {len(PRODUCTS)+len(BENCHES)} позиций').replace('<div class="container" id="decor">',bench_teaser(r)+'<div class="container" id="decor">')
    page('','Литьё и чугунные изделия в Туле — ЦЕНТРСПЕЦМЕТАЛЛ','Литейное производство в Туле: костровые чаши, чугунные печи, декор, проекты скамеек и литьё по чертежам. Каталог изделий и расчёт заказа.',content,extra_schema=[item_list(featured)])
def process_steps():
    steps=[('Расскажите о задаче','Выберите изделие или пришлите эскиз, фото, чертёж. Укажите количество и город получения.'),('Уточним детали','Согласуем материал, размер, оснастку, покрытие и состав комплекта.'),('Подготовим расчёт','Обсудим стоимость, срок изготовления, оплату и передачу продукции.'),('Выполним заказ','Изготовление и передача изделий — по согласованным условиям и документации.')]
    return '<div class="process-grid">'+''.join(f'<article class="process-step"><div class="step-index">0{i}<span aria-hidden="true">↗</span></div><h3>{name}</h3><p>{text}</p></article>' for i,(name,text) in enumerate(steps,1))+'</div>'
def catalog_pages():
    for key in [None]+list(CATEGORIES):
        c=CATEGORIES.get(key);path=catroute(key) if key else 'catalog/';r='../'*len(path.strip('/').split('/'))
        title=c['title'] if c else 'Каталог изделий из чугуна и металла'
        text=c['text'] if c else 'Чаши и мангалы, чугунные печи, художественный декор и литьё на заказ. Посмотрите фотографии, выберите пример исполнения и обсудите с нами изготовление.'
        items=[p for p in PRODUCTS if not key or p['category']==key]
        links=f'<a href="{r}catalog/" class="{"active" if not key else ""}">Все изделия</a>'+''.join(f'<a href="{r}{catroute(k)}" class="{"active" if key==k else ""}">{v["name"]}</a>' for k,v in CATEGORIES.items())
        links+=f'<a href="{r}{BENCH_ROUTE}">Чугунные скамейки</a>'
        count=len(items)+(len(BENCHES) if key is None else 0)
        grid=cards(items,r)
        if key is None:grid=grid[:-6]+bench_cards(r)+'</div>'
        tools=f'<div class="catalog-tools"><nav class="filter-list" aria-label="Категории каталога">{links}</nav><label class="catalog-search js-only"><span aria-hidden="true">⌕</span><input id="catalog-search" type="search" aria-label="Поиск по каталогу" placeholder="Найти изделие"></label></div><p class="result-count" id="result-count" role="status">{count} позиций</p>'
        content=heading(title,text,'Каталог')+f'<section class="container" style="padding-bottom:65px">{tools}{grid}<div class="empty-state" id="empty-state" hidden><h2>По вашему запросу ничего не найдено</h2><p>Попробуйте другое название или опишите нам свою задачу.</p>{button("Обсудить изготовление")}</div></section>'+contact_banner()
        bc=[('Каталог',None)] if not c else [('Каталог','catalog/'),(c['name'],None)]
        listing=item_list(items)
        if key is None:
            listing['itemListElement'] += [{'@type':'ListItem','position':len(items)+i,'name':b['type']+' «'+b['name']+'»','url':absolute('products/'+b['slug']+'/')} for i,b in enumerate(BENCHES,1)]
        page(path,title+' — ЦЕНТРСПЕЦМЕТАЛЛ',text,content,bc,[{'@type':'CollectionPage','name':title,'url':absolute(path),'mainEntity':listing}])
def product_pages():
    for p in PRODUCTS:
        path=route(p);r='../../';category=CATEGORIES[p['category']]
        thumbs=''.join(f'<button type="button" data-gallery-src="{e(r+photo)}" aria-label="Фото {i}" aria-pressed="{str(i==1).lower()}">{image(photo,'',r)}</button>' for i,photo in enumerate(p['gallery'],1))
        features=''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in p['features'])
        cap=f'<p class="product-caption">{e(p["imageCaption"])}</p>' if p.get('imageCaption') else ''
        project=f'<p><a class="text-link" href="{e(p["projectUrl"])}" target="_blank" rel="noopener">Отдельный сайт проекта ↗</a></p>' if p.get('projectUrl') else ''
        related=[q for q in PRODUCTS if q['category']==p['category'] and q['id']!=p['id']][:3]
        if len(related)<2:related=[q for q in PRODUCTS if q['id']!=p['id']][:3]
        model='model' if p.get('imageCaption') else ''
        content=f'''<section class="container product-layout"><div><div class="product-stage"><button type="button" id="product-zoom" aria-label="Увеличить фото">{image(p['image'],p.get('imageAlt',p['name']),r,cls='product-main-image',priority=True)}</button><span class="stage-zoom">Нажмите, чтобы увеличить</span></div><div class="gallery-thumbnails" aria-label="Фотографии изделия">{thumbs}</div><p class="photo-note">{'Первый снимок — каталожная обработка. Исходные фото доступны в галерее.' if p.get('catalogPhoto') else 'Изображения показывают пример исполнения или проектную геометрию.'}</p></div><div class="product-copy"><span class="status-pill {model}">{e(p['tag'])}</span><h1>{e(p['name'])}</h1>{cap}<p>{e(p['description'])}</p><dl class="features">{features}</dl><div class="quote-box"><strong>{'Обсудить проект' if p['category']=='projects' else 'Рассчитаем ваш заказ'}</strong><p>Размер, комплектация и стоимость — по согласованию.</p>{button('Обсудить изготовление',p['id'])}</div><p class="product-fine">{e(p['note'])}</p>{project}</div></section><section class="container related"><div class="section-heading"><div><p class="eyebrow">Ещё в каталоге</p><h2>Посмотрите также</h2></div><a class="text-link" href="{r}{catroute(p['category'])}">Весь раздел ↗</a></div>{cards(related,r)}</section><div class="section">{contact_banner()}</div>'''
        # No fabricated Offer, review, rating, stock status or price.
        kind='CreativeWork' if p['id'] in ('decor-elephant','decor-wolf','pattern','gazebo') else ('Service' if p['id']=='castings' else 'Product')
        entity={'@type':kind,'name':p['name'],'description':p['description'],'image':[absolute(x) for x in p['gallery']],'url':absolute(path)}
        if kind=='Product':entity['brand']={'@type':'Brand','name':NAME}
        if kind=='Service':entity['provider']={'@id':absolute('#organization')}
        page(path,p['name']+' на заказ — ЦЕНТРСПЕЦМЕТАЛЛ',p['description'][:220],content,[('Каталог','catalog/'),(category['name'],catroute(p['category'])),(p['name'],None)],[entity],p['image'])
def information_pages():
    r='../'
    production=heading('Производство начинается с вашей задачи.','Отливки по чертежам, эскизам и образцам: промышленные детали, художественные элементы и модельная оснастка.','Литейное производство в Туле')
    production+=f'''<section class="container"><div class="production-grid"><figure class="production-photo">{image('assets/foundry-pour.webp','Заливка металла в форму — из презентации компании',r,priority=True)}<figcaption>Фотография из презентации производства</figcaption></figure><div class="production-copy"><h2>Чугун, сталь<br>и цветные сплавы.</h2><p>Производственные возможности позволяют рассматривать промышленные и художественные отливки. Сплав и технологию выбираем с учётом геометрии, назначения и требований к изделию.</p>{service_links(r)}{button('Отправить задачу на расчёт')}</div></div><div class="equipment-list"><article><h3>Плавильное оборудование</h3><p>Дуговая и индукционные печи, газовые печи. Оборудование подбирается под материал и конкретный заказ.</p></article><article><h3>Формовка</h3><p>Технологии ПГС, ЖСС и ХТС, бегуны и смесители ХТС. В составе оборудования — машина литья под давлением.</p></article><article><h3>Отжиг и подготовка поверхности</h3><p>Печи отжига, пескоструйная и дробеструйная обработка, галтовка.</p></article><article><h3>Окраска</h3><p>Обычная и порошковая покраска. Тип покрытия и требования к поверхности согласуются под назначение изделия.</p></article></div><div class="documents"><a class="document-link" href="{r}assets/csm-presentation.pdf" target="_blank" rel="noopener">Презентация компании · PDF ↗</a><a class="document-link" href="{r}assets/csm-capabilities.docx" download>Оборудование и возможности · DOCX ↓</a></div></section><section class="container section article-copy"><h2>Как рассмотреть ваш заказ</h2><p>Для начала достаточно описания задачи и имеющихся материалов. Если есть чертежи, укажите марку сплава, размеры, количество и требования к поверхности. Если есть только образец или фотография, обсудим, какие данные нужны для расчёта.</p><p>Возможность изготовления, стоимость, оснастка и сроки подтверждаются после рассмотрения конкретного задания.</p></section>{contact_banner()}'''
    page('production/','Литейное производство в Туле — ЦЕНТРСПЕЦМЕТАЛЛ','Литьё в Туле из чугуна, стали и цветных сплавов. Модельная оснастка, формовка и обработка поверхности. Возможности производства и запрос расчёта.',production,[('Производство',None)],img='assets/foundry-pour.webp')
    future=heading('Новые идеи для городской среды.','Уличные фонари, чугунные скамейки, люки, беседки и плитка — направления, которые мы хотим развивать на основе возможностей литейки.','Благоустройство · в проработке')
    future+='<section class="container"><div class="future-grid">'+''.join(direction_card(d,r) for d in DIRECTIONS)+'</div></section>'
    future+=f'<section class="container section"><div class="text-columns"><div><h2>Начать с конкретной идеи</h2><p>Обсуждаем будущие изделия с заказчиками и партнёрами. Для начала пригодятся фотография, эскиз или описание места установки, желаемые габариты и количество.</p>{button("Обсудить новое изделие","custom",extra="data-message=\"Интересует изготовление изделия для благоустройства.\"")}</div><div><h2>Что предстоит согласовать</h2><p>Геометрию, сплав, оснастку, соединения, покрытие, установку и применимые требования. Представленные направления пока не являются каталогом готовых серийных товаров.</p><p>Для беседки с центральным очагом уже есть отдельный проект.</p><a class="text-link" href="https://a9252233314-dotcom.github.io/Kostrovaya_zona/" target="_blank" rel="noopener">Посмотреть костровую зону ↗</a></div></div></section>'+contact_banner()
    page('blagoustroystvo/','Благоустройство: фонари, скамейки и новые направления — ЦЕНТРСПЕЦМЕТАЛЛ','Развиваем направления изделий для благоустройства: уличные фонари, чугунные скамейки, люки, беседки и плитка. Обсуждение проектов и разработка.',future,[('Новые направления',None)])
    delivery=heading('От первого вопроса до согласованного заказа.','Как подготовить запрос, согласовать изготовление и обсудить передачу продукции.','Заказ и доставка')
    delivery+=f'<section class="container">{process_steps()}</section><section class="container section article-copy"><h2>Что указать в заявке</h2><ul><li>Название изделия или описание задачи.</li><li>Чертёж, фотографию, эскиз или образец, если есть.</li><li>Желаемые размеры, материал, количество и покрытие.</li><li>Город получения и желаемые сроки.</li><li>Контакт для обратной связи.</li></ul><h2>Стоимость и оплата</h2><p>Цена зависит от исполнения, материала, оснастки, количества и комплекта поставки. Условия оплаты и срок изготовления согласуются до начала работ. Фиксированные цены и наличие готовых изделий на сайте не заявлены.</p><h2>Передача и доставка</h2><p>Сообщите город и предпочтительный способ получения. Упаковка, перевозка, стоимость и сроки доставки согласуются отдельно под габариты и особенности заказа. Информация о конкретной отгрузке подтверждается при согласовании условий.</p><h2>Как отправить исходные материалы</h2><p>Форма на сайте подготавливает письмо. Проверьте его в своей почтовой программе, прикрепите чертежи или фото и отправьте. Можно также написать напрямую на <a class="text-link" href="mailto:{EMAIL}">{EMAIL}</a> или позвонить.</p></section>'+contact_banner()
    page('delivery/','Как заказать изготовление и согласовать доставку — ЦЕНТРСПЕЦМЕТАЛЛ','Подготовка заявки, расчёт стоимости, согласование изготовления, оплаты и доставки изделий из чугуна и металла.',delivery,[('Заказ и доставка',None)])
    contacts=heading('Начнём с вашей задачи.','Производство находится в Туле. Выберите удобный способ связи: обсудим изделие, исходные материалы и следующий шаг.','Контакты')
    contacts+=f'<section class="container contact-grid"><div class="contact-card"><h2>Связаться с производством</h2><a href="tel:{tel(CONFIG["phones"][0])}">{e(CONFIG["phones"][0])}</a><a href="tel:{tel(CONFIG["phones"][1])}">{e(CONFIG["phones"][1])}</a><a class="email" href="mailto:{EMAIL}">{EMAIL}</a><p>Для расчёта укажите изделие, размеры, материал и количество. Документы и фотографии можно прикрепить к письму.</p>{button("Подготовить заявку")}</div><div class="article-copy"><h2 style="margin-top:0">Что можно обсудить</h2><ul><li>Костровые чаши, опоры, кольца и решётки.</li><li>Печи, мангалы и литые элементы.</li><li>Художественный декор и орнаменты.</li><li>Промышленное литьё и модельную оснастку.</li><li>Будущие изделия для благоустройства.</li></ul><p>Условия передачи и доставки согласуем по вашему городу и конкретному заказу.</p><div class="documents"><a class="document-link" href="{r}assets/csm-presentation.pdf" target="_blank" rel="noopener">Презентация · PDF ↗</a></div></div></section><section class="container section"><div class="faq-grid"><div><h2>Перед обращением</h2><p>Несколько ответов, которые помогут подготовить задачу.</p></div>{faq(FAQ[:3])}</div></section>'
    page('contacts/','Контакты литейного производства в Туле — ЦЕНТРСПЕЦМЕТАЛЛ','ЦЕНТРСПЕЦМЕТАЛЛ, Тула: телефоны и электронная почта. Запрос на изготовление чугунных изделий, художественного и промышленного литья.',contacts,[('Контакты',None)])
def sitemap():
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml+='\n'.join(f'<url><loc>{e(absolute(path))}</loc><lastmod>{CONFIG["updated"]}</lastmod></url>' for path in PAGES)
    (ROOT/'sitemap.xml').write_text(xml+'\n</urlset>\n',encoding='utf-8')
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+absolute('sitemap.xml')+'\n',encoding='utf-8')
    (ROOT/'site-manifest.json').write_text(json.dumps({'canonicalBase':BASE,'pages':PAGES,'productRoutes':{p['id']:route(p) for p in PRODUCTS},'benchProjectRoutes':{b['id']:'products/'+b['slug']+'/' for b in BENCHES}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def not_found():
    # Use absolute canonical links on 404, which may be requested at any nesting depth.
    content='<section class="container not-found"><p class="eyebrow">Страница не найдена</p><h1>404</h1><p>Возможно, адрес изменился. Вернитесь в каталог или расскажите нам, какое изделие вы ищете.</p><a class="button" href="'+absolute('catalog/')+'">Перейти в каталог ↗</a></section>'
    html='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Страница не найдена — ЦЕНТРСПЕЦМЕТАЛЛ</title><meta name="robots" content="noindex,follow"><link rel="stylesheet" href="'+absolute('modern.css')+'"></head><body>'+content+'</body></html>\n'
    (ROOT/'404.html').write_text(html,encoding='utf-8')

def direction_route(d):
    return 'blagoustroystvo/'+d['slug']+'/'

def direction_card(d,r):
    return f'<a class="future-card" href="{r}{direction_route(d)}"><span class="category-icon">{icon(d["icon"])}</span><h2>{e(d["name"])}</h2><p>{e(d["summary"])}</p><span class="round-label">Проработка направления</span><span class="future-open">Подробнее о направлении <span aria-hidden="true">↗</span></span></a>'

def directions_home(r):
    links=''.join(f'<a class="direction-choice" href="{r}{direction_route(d)}"><span class="category-icon">{icon(d["icon"])}</span><h3>{e(d["name"])}</h3><p>{e(d["short"])}</p><span class="choice-open">Подробнее <span aria-hidden="true">↗</span></span></a>' for d in DIRECTIONS)
    return f'<section class="direction-section direction-home"><div class="direction-intro"><div><p class="eyebrow"><i class="dot"></i>Новые направления · в проработке</p><h2>Изделия для благоустройства</h2><p>Выберите, что хотите изготовить. Откройте направление, посмотрите детали и расскажите о вашем проекте.</p></div></div><nav class="direction-choices" aria-label="Выбрать изделие для благоустройства">{links}</nav><div class="direction-next"><p>Изготовление рассматривается по вашему эскизу или техническому заданию.</p><a class="button light" href="{r}blagoustroystvo/">Все направления <span aria-hidden="true">↗</span></a></div></section>'

def direction_pages():
    r='../../'
    for d in DIRECTIONS:
        if d['slug']=='chugunnye-skameyki':continue # Dedicated project collection below.
        options=''.join(f'<li>{e(item)}</li>' for item in d['options'])
        requirements=''.join(f'<li>{e(item)}</li>' for item in d['requirements'])
        message='Интересует направление «'+d['name']+'». Хочу обсудить изготовление по своему проекту.'
        request=button('Обсудить '+d['name'].lower(),'custom',extra='data-message="'+e(message)+'"')
        project=f'<p><a class="text-link" href="{e(d["projectUrl"])}" target="_blank" rel="noopener">Открыть проект костровой зоны ↗</a></p>' if d.get('projectUrl') else ''
        other=''.join(f'<a class="text-link" href="{r}{direction_route(other)}">{e(other["name"])} ↗</a>' for other in DIRECTIONS if other['slug']!=d['slug'])
        content=heading(d['name'],d['summary'],'Новое направление · в проработке')
        content+=f'<section class="container direction-detail"><div class="article-copy"><h2>Что можно проработать</h2><ul>{options}</ul><h2>Что прислать для обсуждения</h2><ul>{requirements}</ul>{project}</div><aside class="direction-request"><span class="category-icon">{icon(d["icon"])}</span><h2>Обсудим ваш проект</h2><p>Можно начать с фотографии, эскиза или описания. Уточним, что нужно для расчёта.</p>{request}<p class="direction-disclosure">{e(d['note'])}</p></aside></section><section class="container section"><div class="section-heading"><h2>Другие направления</h2></div><nav class="other-directions" aria-label="Другие направления">{other}</nav></section>'
        page(direction_route(d),d['name']+' — обсуждение изготовления в Туле | ЦЕНТРСПЕЦМЕТАЛЛ',d['summary'],content,[('Новые направления','blagoustroystvo/'),(d['name'],None)])


def service_route(service):
    return 'production/'+service['slug']+'/'

def service_links(r):
    return '<ul class="service-lines service-links">'+''.join(f'<li><a href="{r}{service_route(service)}"><span class="service-label">{e(service["label"])}</span><span aria-hidden="true">↗</span></a></li>' for service in SERVICES)+'</ul>'

def service_pages():
    r='../../'
    for service in SERVICES:
        path=service_route(service)
        highlights=''.join(f'<li>{e(item)}</li>' for item in service['highlights'])
        requirements=''.join(f'<li>{e(item)}</li>' for item in service['requirements'])
        request=button('Запросить расчёт','custom',extra='data-message="'+e(service['requestText'])+'"')
        article=''
        for section in service['sections']:
            article+='<section class="service-chapter"><h2>'+e(section['heading'])+'</h2>'
            article+=''.join('<p>'+e(paragraph)+'</p>' for paragraph in section['paragraphs'])
            if section.get('items'):article+='<ul>'+''.join('<li>'+e(item)+'</li>' for item in section['items'])+'</ul>'
            article+='</section>'
        examples=[next(p for p in PRODUCTS if p['id']==key) for key in service['examples']]
        related=''.join(f'<a class="service-related-card" href="{r}{service_route(other)}"><strong>{e(other["label"])}</strong><span>{e(other["short"])}</span><i aria-hidden="true">↗</i></a>' for other in SERVICES if other['slug']!=service['slug'])
        content=heading(service['title'],service['intro'],'Услуги литейного производства · Тула')
        content+=f'<section class="container service-hero"><figure class="service-illustration {e(service["imageFit"])}">{image(service["image"],service["imageAlt"],r,priority=True)}<figcaption>{e(service["imageCaption"])}</figcaption></figure><div class="service-overview"><h2>Что обсудим по вашему заказу</h2><ul>{highlights}</ul>{request}<p>Стоимость и срок — после рассмотрения исходных данных.</p></div></section>'
        content+=f'<section class="container section service-content"><div class="article-copy">{article}</div><aside class="service-brief"><p class="eyebrow">Подготовка запроса</p><h2>Что прислать для расчёта</h2><ul>{requirements}</ul><p>Если каких-то данных нет, начнём с того, что у вас уже есть.</p>{request}<a class="service-phone" href="tel:{tel(CONFIG["phones"][0])}">{e(CONFIG["phones"][0])}</a></aside></section>'
        content+=f'<section class="container"><div class="section-heading"><div><p class="eyebrow">Примеры и исходные материалы</p><h2>Посмотрите также в каталоге</h2></div><a class="text-link" href="{r}catalog/">Весь каталог ↗</a></div>{cards(examples,r)}</section>'
        content+=f'<section class="container section"><div class="faq-grid"><div><p class="eyebrow">Перед обращением</p><h2>Вопросы по услуге</h2><p>Состав работ уточняем под конкретное изделие.</p></div>{faq(service["faq"])}</div></section>'
        content+=f'<section class="container service-other"><div class="section-heading"><h2>Другие услуги производства</h2></div><nav class="service-related" aria-label="Другие услуги">{related}</nav></section><div class="section">{contact_banner()}</div>'
        schema={'@type':'Service','@id':absolute(path)+'#service','name':service['label'],'serviceType':service['label'],'url':absolute(path),'description':service['description'],'provider':{'@id':absolute('#organization')},'image':absolute(service['image'])}
        page(path,service['title']+' — ЦЕНТРСПЕЦМЕТАЛЛ',service['description'],content,[('Производство','production/'),(service['label'],None)],[schema],service['image'])

if __name__=='__main__':
    prepare_assets()
    home();catalog_pages();product_pages();information_pages();direction_pages();service_pages();build_benches(globals());sitemap();not_found()
    print(json.dumps({'pages':len(PAGES),'products':len(PRODUCTS),'benchProjects':len(BENCHES),'canonicalBase':BASE,'javascriptRequiredForContent':False},ensure_ascii=False))
