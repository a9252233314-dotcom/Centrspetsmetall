"""Static lamp collection, using one source mesh for images and drawings."""
from pathlib import Path
from html import escape
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFilter
from lamp_geometry import mesh
from bench_catalog import project,face_color

ROOT=Path(__file__).resolve().parent
LAMPS=json.loads((ROOT/'lamps.json').read_text(encoding='utf-8'))
LAMP_ROUTE='blagoustroystvo/ulichnye-fonari/'
COLORS={'iron':'#33453d','metal':'#656f69','light':'#e8eddb'}
DISCLOSURE='Проектная визуализация. Изготовление, конструкция и светотехника согласуются с производством.'
def e(v):return escape(str(v),quote=True)
def route(b):return 'products/'+b['slug']+'/'
def asset(b,suffix):return 'assets/lamps/'+b['id']+'-'+suffix
def asset_url(b,suffix):
    path=asset(b,suffix);f=ROOT/path
    return path+('?v='+hashlib.sha256(f.read_bytes()).hexdigest()[:10] if f.exists() else '')
def hero_asset(b,head=False):
    suffix='head-render.webp' if head else 'render.webp';manifest=ROOT/'assets/lamps/render-manifest.json'
    info=json.loads(manifest.read_text(encoding='utf-8')).get(b['id'],{}) if manifest.exists() else {}
    geom=ROOT/asset(b,'geometry.json')
    if (ROOT/asset(b,suffix)).exists() and geom.exists() and info.get('geometry_sha256')==hashlib.sha256(geom.read_bytes()).hexdigest():return asset_url(b,suffix)
    return asset_url(b,'head.webp' if head else 'view.webp')

def raster(b,faces,suffix='view',w=900,h=1200):
    ps=[([project(v,-.58,.12) for v in f['v']],f) for f in faces]
    pts=[v for vs,f in ps for v in vs];xmin=min(v[0] for v in pts);xmax=max(v[0] for v in pts);ymin=min(v[1] for v in pts);ymax=max(v[1] for v in pts)
    scale=min((w-150)/(xmax-xmin),(h-150)/(ymax-ymin));cx=w/2-(xmin+xmax)*scale/2;cy=h/2-(ymin+ymax)*scale/2
    aa=2;im=Image.new('RGB',(w*aa,h*aa),'#eeeee7');d=ImageDraw.Draw(im)
    for vs,f in sorted(ps,key=lambda v:sum(t[2] for t in v[0])/len(v[0])):
        d.polygon([(round((v[0]*scale+cx)*aa),round((v[1]*scale+cy)*aa)) for v in vs],fill=face_color(f,COLORS))
    im=im.resize((w,h),Image.Resampling.LANCZOS);im.save(ROOT/asset(b,suffix+'.webp'),quality=92)
    if suffix=='view':im.save(ROOT/asset(b,'social.jpg'),quality=92)

STYLE='<style>text{font-family:Arial,sans-serif;fill:#233e32}.small{font-size:17px;fill:#65756a}.label{font-size:22px;font-weight:bold}.measure{fill:none;stroke:#789283;stroke-width:1.3}</style>'
def sheet_start(title,b):
    return ['<rect width="1400" height="990" fill="white"/>',STYLE,'<text x="55" y="52" font-size="20" font-weight="bold">Тульская литейная мануфактура</text>',f'<text x="55" y="96" font-size="32" font-weight="bold">{e(title)}</text>',f'<text x="1345" y="52" text-anchor="end" class="small">{e(b["code"])} · ЭСКИЗ ДЛЯ СОГЛАСОВАНИЯ</text>']
def write_svg(b,suffix,body):
    (ROOT/asset(b,suffix)).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="990" viewBox="0 0 1400 990"><title>'+e(b['name'])+' — '+e(suffix)+'</title>'+''.join(body)+'</svg>',encoding='utf-8')
def ortho(body,faces,box,proj,title,dimension=None):
    x,y,w,h=box;ps=[([proj(v) for v in f['v']],f) for f in faces]
    pts=[v for vs,f in ps for v in vs];xmin=min(v[0] for v in pts);xmax=max(v[0] for v in pts);ymin=min(v[1] for v in pts);ymax=max(v[1] for v in pts)
    sc=min((w-120)/max(1,xmax-xmin),(h-85)/max(1,ymax-ymin));ox=x+w/2-(xmin+xmax)*sc/2;oy=y+45+(h-85)/2-(ymin+ymax)*sc/2
    body.append(f'<text x="{x}" y="{y+20}" class="label">{e(title)}</text>')
    for vs,f in sorted(ps,key=lambda a:sum(v[2] for v in a[0])/len(a[0])):
        color='#f1eed6' if f['m']=='light' else '#dce5df' if f['m']=='iron' else '#b4c2b8'
        xy=' '.join(f'{ox+v[0]*sc:.2f},{oy+v[1]*sc:.2f}' for v in vs)
        body.append(f'<polygon points="{xy}" fill="{color}" stroke="#435d4c" stroke-width=".7"/>')
    if dimension:
        x1=ox+xmin*sc;x2=ox+xmax*sc;y1=oy+ymin*sc;y2=oy+ymax*sc
        body.append(f'<path class="measure" d="M{x1} {y2+4}v22M{x2} {y2+4}v22M{x1} {y2+18}H{x2}"/><text x="{(x1+x2)/2}" y="{y2+40}" class="small" text-anchor="middle">{round(xmax-xmin)} мм</text>')
        if dimension!='top':body.append(f'<path class="measure" d="M{x2+4} {y1}h30M{x2+4} {y2}h30M{x2+24} {y1}V{y2}"/><text x="{x2+36}" y="{(y1+y2)/2}" class="small">{round(ymax-ymin)} мм</text>')
def drawing(b,faces):
    body=sheet_start(b['type']+' «'+b['name']+'» · Габаритный эскиз',b)
    ortho(body,faces,(55,135,420,665),lambda v:(v[0],-v[2],-v[1]),'Спереди','front')
    ortho(body,faces,(510,135,400,665),lambda v:(v[1],-v[2],v[0]),'Сбоку','side')
    ortho(body,faces,(950,135,395,340),lambda v:(v[0],v[1],v[2]),'Сверху','top')
    body.extend(['<text x="950" y="555" class="label">Базовый эскиз</text>',f'<text x="950" y="594" class="small">Высота: {b["height"]} мм</text>','<text x="950" y="629" class="small">Стойка — сталь.</text>','<text x="950" y="659" class="small">Цоколь и верхние детали — литьё.</text>','<text x="950" y="704" class="small">Световой блок показан условно.</text>','<text x="950" y="734" class="small">Светотехника подбирается отдельно.</text>','<path d="M55 855H1345" stroke="#cbd6ce"/>','<text x="55" y="893" class="small">Предварительная компоновка, не рабочий чертёж. Размеры в мм, масштаб условный.</text>','<text x="55" y="926" class="small">Фундамент, сечения, крепёж, электромонтаж и характеристики освещения требуют разработки и проверки.</text>','<text x="55" y="960" class="small">Тула · Тульская литейная мануфактура · csm-factory@bk.ru</text>'])
    write_svg(b,'drawing.svg',body)
def assembly_drawing(b,faces):
    body=sheet_start('Как собирается фонарь «'+b['name']+'»',b)
    ortho(body,faces,(55,145,500,650),lambda v:(v[0],-v[2],-v[1]),'Общая компоновка')
    head=[f for f in faces if f['s']=='head'];ortho(body,head,(620,145,725,400),lambda v:(v[0],-v[2],-v[1]),'Верхний узел · увеличено')
    entries=[('01 · Основание и стойка','Стальной фланец опирается на подготовленное основание.','Фундамент и анкеры назначаются под место установки.'),('02 · Декоративный цоколь','Литой кожух окружает нижнюю часть стальной стойки.','Кожух не заменяет несущий ствол и фланцевое соединение.'),('03 · Верхний узел','Переходник соединяет стойку с рамкой или кронштейном.','Посадки, отверстия, крепёж и доступ для обслуживания — в проекте.')]
    for i,(title,line1,line2) in enumerate(entries):
        y=580+i*92;body.extend([f'<text x="620" y="{y}" class="label">{e(title)}</text>',f'<text x="620" y="{y+30}" class="small">{e(line1)}</text>',f'<text x="620" y="{y+57}" class="small">{e(line2)}</text>'])
    body.extend(['<path d="M55 871H1345" stroke="#cbd6ce"/>','<text x="55" y="909" class="small">Световой блок и проводка: подбор, кабельные проходы, подключения и защита разрабатываются отдельно.</text>','<text x="55" y="940" class="small">Это конструктивная схема для обсуждения. Электромонтажная схема и расчёт опоры в материал не входят.</text>'])
    write_svg(b,'assembly.svg',body)
def prepare_assets():
    (ROOT/'assets/lamps').mkdir(exist_ok=True)
    for b in LAMPS:
        faces=mesh(b);data={'id':b['id'],'height':3000,'faces':faces}
        (ROOT/asset(b,'geometry.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        if b.get('finCount'):
            for n in [12,20]:(ROOT/asset(b,f'geometry-{n}.json')).write_text(json.dumps({'id':b['id'],'height':3000,'faces':mesh(b,fin_count=n)},separators=(',',':')),encoding='utf-8')
        raster(b,faces);raster(b,[f for f in faces if f['s']=='head'],'head',1200,900)
        drawing(b,faces);assembly_drawing(b,faces)
        if 'render.webp' in hero_asset(b):
            with Image.open(ROOT/asset(b,'render.webp')) as im:im.convert('RGB').save(ROOT/asset(b,'social.jpg'),quality=92)

def lamp_cards(r):
    out=[]
    for b in LAMPS:
        title=b['type']+' «'+b['name']+'»'
        out.append(f'''<article class="product-card bench-card lamp-card" data-product-id="lamp-{b['id']}" data-search="{e((title+' уличные фонари парковое освещение литой цоколь '+b['description']).lower())}"><a class="product-media" href="{r}{route(b)}"><img src="{r}{hero_asset(b)}" width="900" height="1200" loading="lazy" alt="{e(title)} — проектный рендер"><span class="product-status model">Проектная модель</span></a><div class="product-body"><p class="product-category">{e(b['code'])} · Литьё и сталь</p><h3><a href="{r}{route(b)}">{e(title)}</a></h3><p>{e(b['features'][0])}</p><p class="bench-card-size">Базовая высота: 3 м · Эскиз</p><div class="card-foot"><span>Расчёт по проекту</span><a href="{r}{route(b)}">Модель и эскиз ↗</a></div></div></article>''')
    return ''.join(out)
def teaser(r):
    return f'''<section class="container section lamp-teaser"><div class="section-heading"><div><p class="eyebrow">Новая проектная коллекция</p><h2>Фонари.<br>Свой силуэт.</h2></div><a class="text-link" href="{r}{LAMP_ROUTE}">Все фонари · 3 ↗</a></div><p class="bench-section-lead">Геометричная рамка, плавная дуга и параметрический плафон. Сравните собственные формы в 3D и обсудите литые детали или комплект.</p><div class="product-grid bench-grid">{lamp_cards(r)}</div><p class="bench-disclosure">{DISCLOSURE}</p></section>'''

def build_lamps(api):
    page=api['page'];button=api['button'];faq=api['faq'];banner=api['contact_banner'];absolute=api['absolute'];r='../../'
    collection=f'''<section class="container bench-collection-hero lamp-collection-hero"><div><p class="eyebrow"><i class="dot"></i>Литьё и свет · Проектная коллекция</p><h1>Фонари,<br>у которых есть<br>свой характер.</h1><p>Три собственные формы для аллеи, двора и входной группы. Рассмотрите геометрию, сравните верхние узлы и выберите, с чего начать ваш проект.</p><a class="button" href="#models">Выбрать фонарь ↓</a></div><a class="bench-collection-art lamp-hero-art" href="{r}{route(LAMPS[2])}"><img src="{r}{hero_asset(LAMPS[2],True)}" width="1200" height="900" fetchpriority="high" alt="Ореол — параметрический плафон с литыми рёбрами"><span>ЦСМ ФН-03 · Ореол ↗</span></a></section><section class="container section" id="models"><div class="section-heading"><div><p class="eyebrow">Свои формы, общий подход</p><h2>Выберите силуэт.</h2></div><p>Рендеры, 3D, размеры<br>и схемы компоновки.</p></div><div class="product-grid bench-grid">{lamp_cards(r)}</div><p class="bench-disclosure">{DISCLOSURE}</p></section><section class="bench-supply-band"><div class="container text-columns"><div><p class="eyebrow">Для архитекторов и партнёров</p><h2>Литые детали.<br>Или фонарь в сборе.</h2><p>Можно начать с цоколя, кронштейна и деталей плафона. Комплект со стальной стойкой и световым блоком обсуждаем отдельно: определяем состав работ, комплектующие и ответственность за сборку.</p>{button('Обсудить фонари','custom',extra='data-message="Интересуют уличные фонари или литые детали. Модель: ____. Количество: ____. Место установки: ____."')}</div><div><h2>Сначала — задача освещения.</h2><ol><li>Уточняем территорию, назначение, высоту и количество.</li><li>Согласуем форму и состав литых деталей.</li><li>Прорабатываем опору, основание, светотехнику и обслуживание.</li><li>После проверки проекта согласуем изготовление и стоимость.</li></ol><p class="bench-disclosure">Визуализация не задаёт мощность, световой поток, степень защиты и класс электробезопасности. Эти параметры подтверждаются для выбранного исполнения.</p></div></div></section><section class="container section article-copy"><h2>Уличные и парковые фонари с литыми деталями в Туле</h2><p>Тульская литейная мануфактура развивает коллекцию фонарей на основе возможностей литейного производства в Туле. Предлагаем обсудить декоративные цоколи, кронштейны, корпуса и рёбра плафонов по собственным эскизам или заданию заказчика. На странице представлены проекты, которые требуют технологической проработки перед изготовлением.</p><p>Для расчёта пришлите выбранную форму, количество, желаемую высоту и описание территории. При наличии приложите план расстановки опор и требования к освещению. Для архитектурных бюро и сборочных производств отдельно рассматриваем партии литых деталей.</p><h3>Что входит в разработку</h3><p>Геометрия отливок и оснастки, сопряжение со стальной стойкой, фланцевое крепление, доступ к обслуживанию и условия эксплуатации. Световой блок подбирается под задачу; светораспределение и электрическая часть согласуются отдельно.</p></section>'''+banner()
    schema={'@type':'CollectionPage','name':'Уличные фонари — проектная коллекция','url':absolute(LAMP_ROUTE),'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':b['type']+' «'+b['name']+'»','url':absolute(route(b))} for i,b in enumerate(LAMPS,1)]}}
    page(LAMP_ROUTE,'Уличные и парковые фонари в Туле — проекты | Тульская литейная мануфактура','Собственные проекты уличных фонарей: литые цоколи, кронштейны и параметрические плафоны. 3D, габаритные эскизы и обсуждение изготовления в Туле.',collection,[('Каталог','catalog/'),('Уличные фонари',None)],[schema],asset(LAMPS[2],'social.jpg'))
    for b in LAMPS:
        title=b['type']+' «'+b['name']+'»';message='Прошу рассмотреть изготовление: '+title+' ('+b['code']+'). Высота: 3000 мм. Количество: ____. Город: ____.'
        request=button('Рассчитать изготовление','custom',extra='id="lamp-request" data-message="'+e(message)+'"')
        height_buttons=''.join(f'<button type="button" data-lamp-height="{n}" aria-pressed="{str(n==3000).lower()}">{format(n/1000,"g").replace(".",",")} м</button>' for n in [2400,3000,3600])
        fin_buttons=''
        if b.get('finCount'):
            buttons=''.join(f'<button type="button" data-lamp-fins="{n}" data-geometry="{r}{asset_url(b,"geometry.json" if n==16 else f"geometry-{n}.json")}" aria-pressed="{str(n==16).lower()}">{n}</button>' for n in [12,16,20])
            fin_buttons=f'<div class="bench-option"><span>Рёбер плафона</span><div class="bench-lengths" role="group" aria-label="Количество рёбер">{buttons}</div></div>'
        views=''.join(f'<button type="button" data-lamp-view="{key}" aria-pressed="{str(key=="render").lower()}">{label}</button>' for key,label in [('render','Рендер 3 м'),('perspective','3D'),('head','Плафон 3D'),('head-render','Плафон · рендер'),('front','Спереди'),('base','Цоколь'),('assembly','Сборка')])
        swatches=''.join(f'<button type="button" data-lamp-color="{color}" style="--swatch:{color}" aria-label="{label}" aria-pressed="{str(i==0).lower()}"></button>' for i,(color,label) in enumerate([('#33453d','Лесной зелёный'),('#313437','Графитовый'),('#776951','Тёплый бронзовый')]))
        parts=''.join(f'<tr><td>{e(name)}</td><td'+(' id="lamp-fin-quantity"' if name=='Литые рёбра плафона' else '')+'>'+e(qty)+'</td></tr>' for name,qty in b['parts'])
        questions=[('Можно заказать только литые детали?','Да, можно обсудить цоколи, кронштейны и детали плафонов отдельно. Укажите модель, состав комплекта и количество. Оснастка и технология изготовления требуют согласования с литейкой.'),('Какая мощность и степень защиты у фонаря?','На странице показан эскиз корпуса, а световой блок обозначен условно. Мощность, светораспределение, степень защиты и другие характеристики определяются после выбора комплектующих и разработки исполнения.'),('Можно изменить высоту и форму?','Переключатели помогают выбрать пропорции для запроса. При изменении высоты отдельно проверяются стальная стойка, крепления и основание. Собственный рисунок можно обсудить по эскизу.'),('Это готовое серийное изделие?','Пока это проектная коллекция. Рендеры и габаритные эскизы показывают замысел; выпуск образца и возможность изготовления подтверждаются производством.')]
        content=f'''<section class="container bench-product lamp-product" data-lamp="{b['id']}" data-fins="{b.get('finCount',0)}"><div class="bench-main"><div class="bench-viewer lamp-viewer" id="lamp-viewer" data-geometry="{r}{asset_url(b,'geometry.json')}" data-render="{r}{hero_asset(b)}" data-head-render="{r}{hero_asset(b,True)}" data-assembly="{r}{asset_url(b,'assembly.svg')}"><img id="lamp-fallback" src="{r}{hero_asset(b)}" width="900" height="1200" fetchpriority="high" alt="{e(title)} — проектная визуализация"><canvas id="lamp-gl" width="900" height="1200" aria-label="Интерактивная 3D-модель фонаря" hidden></canvas><svg id="lamp-canvas" viewBox="0 0 900 1200" aria-label="Вращаемая модель фонаря" role="img" hidden></svg><span class="bench-view-tag">Проектная визуализация</span><span class="bench-view-help js-only">Потяните для 3D</span></div><div class="bench-view-buttons js-only" role="group" aria-label="Ракурс фонаря">{views}</div><p class="bench-disclosure">{DISCLOSURE}</p></div><div class="bench-summary"><p class="eyebrow">{e(b['code'])} · Проектная коллекция</p><h1>{e(b['type'])}<br>«{e(b['name'])}»</h1><p>{e(b['description'])}</p><ul class="bench-highlights">{''.join('<li>'+e(f)+'</li>' for f in b['features'])}</ul><div class="bench-config js-only">{fin_buttons}<div class="bench-option"><span>Высота эскиза</span><div class="bench-lengths" role="group" aria-label="Желаемая высота">{height_buttons}</div></div><div class="bench-option"><span>Цвет литья на экране</span><div class="bench-swatches" role="group" aria-label="Цвет литья">{swatches}</div></div><label class="bench-option"><span>Комплектация</span><select id="lamp-supply"><option>Фонарь в сборе — обсудить</option><option>Только литые детали</option></select></label><p>Рендеры и PDF показывают базовый эскиз 3 м{', 16 рёбер' if b.get('finCount') else ''}. Переключатели меняют 3D и текст запроса.</p></div><div class="bench-order"><span>Стоимость после согласования</span>{request}</div><p id="lamp-current" class="bench-current" aria-live="polite">Эскиз: 3000 мм</p></div></section><section class="container section"><div class="section-heading"><div><p class="eyebrow">Замысел модели</p><h2>Форма и конструкция.</h2></div></div><div class="text-columns article-copy"><div><p>{e(b['detail'])}</p><h3>Состав предложения</h3><p>Литые детали предлагаем обсудить с производством в Туле. Стальную стойку, фланец, световой блок и электрическую часть согласуем в составе проекта. Наличие готовой оснастки и серийного изделия не заявлено.</p></div><div><h3>Предварительная комплектация</h3><div class="lamp-table-wrap"><table class="lamp-parts"><thead><tr><th scope="col">Элемент</th><th scope="col">Количество</th></tr></thead><tbody>{parts}</tbody></table></div><p class="bench-disclosure">Состав для обсуждения. Крепёж, сечения, посадки и порядок обслуживания назначаются в рабочей документации.</p></div></div></section><section class="bench-drawing-band" id="drawing"><div class="container"><div class="section-heading"><div><p class="eyebrow">Для выбора и обсуждения</p><h2>Габаритный эскиз</h2></div><div class="bench-downloads"><a class="button secondary" href="{r}{asset_url(b,'drawing.svg')}" download>Скачать SVG ↓</a><a class="button" href="{r}{asset_url(b,'drawing.pdf')}" download>Скачать PDF ↓</a></div></div><a class="bench-drawing" href="{r}{asset_url(b,'drawing.svg')}" target="_blank" rel="noopener"><img src="{r}{asset_url(b,'drawing.svg')}" width="1400" height="990" loading="lazy" alt="{e(title)}: виды спереди, сбоку и сверху с размерами"></a><p class="bench-disclosure">Базовая высота 3000 мм. Габаритный эскиз не заменяет рабочий проект опоры, фундамента и освещения.</p></div></section><section class="container section"><div class="section-heading"><div><p class="eyebrow">Конструктивная схема</p><h2>Что с чем соединяется</h2></div><a class="text-link" href="{r}{asset_url(b,'assembly.svg')}" target="_blank" rel="noopener">Открыть крупно ↗</a></div><a class="bench-drawing" href="{r}{asset_url(b,'assembly.svg')}" target="_blank" rel="noopener"><img src="{r}{asset_url(b,'assembly.svg')}" width="1400" height="990" loading="lazy" alt="Компоновка фонаря: стойка с фланцем, декоративный цоколь и верхний узел"></a><div class="lamp-steps"><article><span>01</span><h3>Основание и стойка</h3><p>Стальная стойка с фланцем устанавливается на основание по отдельному проекту. Литой цоколь закрывает нижнюю часть стойки.</p></article><article><span>02</span><h3>Верхний узел</h3><p>Переходник соединяется со стойкой, к нему крепится рамка или кронштейн. Детали плафона образуют связную сборку.</p></article><article><span>03</span><h3>Свет и обслуживание</h3><p>Подбираются световой блок, кабельные проходы, защита и доступ для замены. Электромонтажная схема разрабатывается отдельно.</p></article></div></section><section class="container section"><div class="faq-grid"><div><p class="eyebrow">Перед расчётом</p><h2>Обсудим исполнение.</h2></div>{faq(questions)}</div></section><section class="container section"><div class="section-heading"><h2>Другие формы</h2><a class="text-link" href="{r}{LAMP_ROUTE}">Все фонари ↗</a></div><div class="product-grid bench-grid">{lamp_cards(r)}</div></section>'''+banner()
        for file in ['lamp-webgl.js','lamp-viewer.js']:content+=f'<script src="{r}{file}?v={hashlib.sha256((ROOT/file).read_bytes()).hexdigest()[:10]}" defer></script>'
        schema={'@type':'CreativeWork','name':title+' — проект','description':b['description'],'url':absolute(route(b)),'image':absolute(asset(b,'social.jpg')),'creator':{'@id':absolute('#organization')},'creativeWorkStatus':'Эскизная разработка'}
        page(route(b),title+' — 3D и эскиз в Туле | Тульская литейная мануфактура',b['description'],content,[('Каталог','catalog/'),('Уличные фонари',LAMP_ROUTE),(b['name'],None)],[schema],asset(b,'social.jpg'))
