"""Original bench concepts: one polygon model supplies views, drawings and the viewer.

The mesh is presentation geometry, not casting tooling or an approved working drawing.
"""
from pathlib import Path
from html import escape
import json, math, hashlib
from PIL import Image, ImageDraw, ImageFilter
from modern_benches import modern_mesh

ROOT = Path(__file__).resolve().parent
BENCHES = json.loads((ROOT/'benches.json').read_text(encoding='utf-8'))
BENCH_ROUTE = 'blagoustroystvo/chugunnye-skameyki/'
DISCLOSURE = 'Проектная визуализация. Конструкция, размеры и комплектация согласуются перед изготовлением.'
COLORS = {'wood': '#a56d42', 'iron': '#33453d', 'metal': '#8b938a'}

def e(v): return escape(str(v), quote=True)
def route(b): return 'products/'+b['slug']+'/'
def asset(b, suffix): return 'assets/benches/'+b['id']+'-'+suffix

def asset_url(b,suffix):
    path=asset(b,suffix);target=ROOT/path
    return path+('?v='+hashlib.sha256(target.read_bytes()).hexdigest()[:10] if target.exists() else '')

def hero_asset(b):
    manifest=ROOT/'assets/benches/render-manifest.json'
    if manifest.exists():
        info=json.loads(manifest.read_text(encoding='utf-8')).get(b['id'],{})
        geom=ROOT/asset(b,'geometry.json')
        if geom.exists() and (ROOT/asset(b,'render.webp')).exists() and info.get('geometry_sha256')==hashlib.sha256(geom.read_bytes()).hexdigest():return asset_url(b,'render.webp')
    return asset_url(b,'view.webp')

def mesh(b,length=1800,return_parts=False,rib_count=None):
    if b.get('family') in ('modern','ribbed'):return modern_mesh(b,length,return_parts,rib_count)
    faces=[];parts=[];group='seat'
    def prism(profile, x1, x2, material='iron'):
        part_id=len(parts)
        parts.append({'id':part_id,'g':group,'x':[x1,x2],'profile':profile,'m':material})
        a=[[x1,y,z] for y,z in profile]; c=[[x2,y,z] for y,z in profile]
        faces.append({'v':a[::-1], 'm':material,'g':group,'part':part_id}); faces.append({'v':c,'m':material,'g':group,'part':part_id})
        for i in range(len(a)):
            j=(i+1)%len(a); faces.append({'v':[a[i],a[j],c[j],c[i]],'m':material,'g':group,'part':part_id})
    def bar(x1,x2,y1,z1,y2,z2,width=30):
        dy=y2-y1; dz=z2-z1; ln=math.hypot(dy,dz)
        py=-dz/ln*width/2; pz=dy/ln*width/2
        prism([(y1+py,z1+pz),(y2+py,z2+pz),(y2-py,z2-pz),(y1-py,z1-pz)],x1,x2)
    def box(x1,x2,y1,y2,z1,z2,material):
        bevel=min(4,(z2-z1)/5,(y2-y1)/5)
        prism([(y1+bevel,z1),(y2-bevel,z1),(y2,z1+bevel),(y2,z2-bevel),(y2-bevel,z2),(y1+bevel,z2),(y1,z2-bevel),(y1,z1+bevel)],x1,x2,material)
    # Five 80 mm boards, four 12 mm visual joints, 32 mm visual board depth.
    for i in range(5):
        y=-224+i*92
        box(-length/2,length/2,y,y+80,418,450,'wood')
    back=b['id']!='line'
    depth=b['depth']; front=-290 if b['id']=='park' else (-300 if back else -240)
    rear=front+depth
    support_center=length/2-250
    for x in (-support_center,support_center):
        group='support-left' if x<0 else 'support-right'
        x1=x-22; x2=x+22
        # Continuous open frame, feet and a rail below the wooden seat.
        box(x1-10,x2+10,front,front+115,0,20,'iron')
        box(x1-10,x2+10,rear-115,rear,0,20,'iron')
        bar(x1,x2,front+55,18,-170,407,38)
        bar(x1,x2,rear-55,18,170,407,38)
        bar(x1,x2,-270 if back else -225,398,290 if back else 225,398,40)
        def leg_at(z,front_leg):
            start=front+55 if front_leg else rear-55
            end=-170 if front_leg else 170
            return start+(end-start)*(z-18)/389
        if back:
            top=b['height']
            # Back support ends at the exact overall depth/height envelope.
            prism([(240,399),(276,399),(rear,top),(rear-36,top)],x1,x2)
            # Arm front stays outside the seat boards; its rear passes through
            # the 545..570 gap between back boards, never through timber.
            bar(x1,x2,-252,398,-252,615,25)
            bar(x1,x2,-252,615,170,615,32)
            bar(x1,x2,170,615,170,556,20)
            join_y=240+(556-399)*(rear-276)/(top-399)+18
            bar(x1,x2,170,556,join_y,556,20)
            if b['id']=='ornament':
                for k in range(40):
                    t=2*math.pi*k/40; u=2*math.pi*(k+1)/40
                    bar(x1,x2,112*math.cos(t),242+112*math.sin(t),112*math.cos(u),242+112*math.sin(u),18)
                for k in range(8):
                    t=2*math.pi*k/8
                    bar(x1,x2,23*math.cos(t),242+23*math.sin(t),105*math.cos(t),242+105*math.sin(t),14)
                for k in range(18):
                    t=2*math.pi*k/18;u=2*math.pi*(k+1)/18
                    bar(x1,x2,26*math.cos(t),242+26*math.sin(t),26*math.cos(u),242+26*math.sin(u),12)
                bar(x1,x2,-112,242,leg_at(242,True),242,19)
                bar(x1,x2,112,242,leg_at(242,False),242,19)
                bar(x1,x2,0,354,0,398,19)
            else:
                bar(x1,x2,leg_at(360,True),360,leg_at(110,False),110,22)
        else:
            bar(x1,x2,front+70,62,rear-70,62,28)
    if back:
        group='back'
        for i in range(4):
            z=490+i*80
            slope=(rear-276)/(b['height']-399)
            y=240+(z-399)*slope
            profile=[(y-32,z),(y,z),(y+slope*55,z+55),(y-32+slope*55,z+55)]
            prism(profile,-length/2,length/2,'wood')
    # The longitudinal tie is under the seat, with real mating end plates.
    # It meets the inner faces of the cast crossheads, rather than open air.
    # Hollow rectangular presentation section; production sizing is separate.
    group='tiebar'
    end=support_center-28
    for y1,y2,z1,z2 in [(-20,20,370,372),(-20,20,408,410),(-20,-18,372,408),(18,20,372,408)]:
        box(-end,end,y1,y2,z1,z2,'iron')
    for sign in (-1,1):
        group='plate-left' if sign<0 else 'plate-right'
        center=sign*support_center
        x1,x2=sorted([center-sign*28,center-sign*22])
        box(x1,x2,-55,55,366,414,'iron')
        # Bolt heads/washers and nuts are shown conventionally at mating faces.
        # Nominal grade, holes and fit are for the working design, not assigned here.
        group='fastener-left' if sign<0 else 'fastener-right'
        for y in (-35,35):
            for offset1,offset2,radius,sides in [(-38,-30,7.5,6),(-30,-28,9,16),(22,24,9,16),(24,32,7.5,6)]:
                a,c=sorted([center+sign*offset1,center+sign*offset2])
                profile=[(y+radius*math.cos(t*2*math.pi/sides),398+radius*math.sin(t*2*math.pi/sides)) for t in range(sides)]
                prism(profile,a,c,'metal')
    return parts if return_parts else faces

def project(v,yaw=-.66,pitch=.30):
    x,y,z=v; a=math.cos(yaw);s=math.sin(yaw);p=math.sin(pitch);q=math.cos(pitch)
    xx=x*a-y*s; yy=x*s+y*a
    return (xx, -yy*p-z*q, -yy*q+z*p)

def face_color(face,palette):
    vs=face['v']; a=[vs[1][i]-vs[0][i] for i in range(3)];b=[vs[2][i]-vs[0][i] for i in range(3)]
    n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    ln=math.sqrt(sum(t*t for t in n)) or 1
    # Two-sided lighting keeps extruded concept profiles readable from either side.
    light=.70+.28*abs(sum(n[i]*[-.3,-.4,.86][i] for i in range(3))/ln)
    if abs(n[2])/ln>.8:light=1.12
    color=palette[face['m']].lstrip('#')
    return '#'+''.join(f'{min(255,round(int(color[i:i+2],16)*light)):02x}' for i in (0,2,4))

def projected_faces(faces,w=1200,h=900,support=False):
    projected=[([project(v) for v in f['v']],f) for f in faces]
    pts=[p for vs,f in projected for p in vs]
    xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts)
    scale=min((w-150)/(xmax-xmin),(h-180)/(ymax-ymin))
    cx=w/2-(xmin+xmax)/2*scale;cy=h/2-(ymin+ymax)/2*scale-5
    return sorted([([(p[0]*scale+cx,p[1]*scale+cy) for p in vs],sum(p[2] for p in vs)/len(vs),f) for vs,f in projected],key=lambda t:t[1])

def render(b,faces,suffix='view'):
    w,h=1200,900; shapes=projected_faces(faces,w,h)
    bg='#eeeee7'; defs='<defs><filter id="shadow" x="-50%" y="-100%" width="200%" height="300%"><feGaussianBlur stdDeviation="17"/></filter></defs>'
    body=[f'<rect width="1200" height="900" fill="{bg}"/>',defs,'<ellipse cx="610" cy="748" rx="400" ry="32" fill="#24382b" opacity=".15" filter="url(#shadow)"/>']
    for pts,depth,face in shapes:
        points=' '.join(f'{x:.2f},{y:.2f}' for x,y in pts)
        color=face_color(face,COLORS)
        body.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" stroke-width=".65" stroke-linejoin="round"/>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" role="img"><title>'+e(b['type']+' «'+b['name']+'» — проектная визуализация')+'</title>'+''.join(body)+'</svg>'
    (ROOT/asset(b,suffix+'.svg')).write_text(svg,encoding='utf-8')
    # Raster derivative for social previews and efficient catalog thumbnails.
    aa=2;im=Image.new('RGB',(w*aa,h*aa),bg);shadow=Image.new('RGBA',im.size)
    d=ImageDraw.Draw(shadow);d.ellipse((210*aa,716*aa,1010*aa,780*aa),fill=(36,56,43,35));shadow=shadow.filter(ImageFilter.GaussianBlur(17*aa));im.paste(shadow,(0,0),shadow)
    d=ImageDraw.Draw(im)
    for pts,depth,face in shapes:d.polygon([(round(x*aa),round(y*aa)) for x,y in pts],fill=face_color(face,COLORS))
    im=im.resize((w,h),Image.Resampling.LANCZOS)
    im.save(ROOT/asset(b,suffix+'.webp'),quality=92)
    if suffix=='view':im.save(ROOT/asset(b,'social.jpg'),quality=92)

def drawing(b,faces):
    body=['<rect width="1400" height="990" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#233e32}.small{font-size:15px;fill:#68766e}.dim{font-size:17px}.label{font-size:19px;font-weight:bold}.measure{fill:none;stroke:#789283;stroke-width:1.2}</style>',
          '<defs><marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#789283"/></marker></defs>',
          '<text x="55" y="55" font-size="19" font-weight="bold">ЦЕНТРСПЕЦМЕТАЛЛ</text>',
          '<text x="55" y="91" font-size="30" font-weight="bold">'+e(b['type']+' «'+b['name']+'»')+'</text>',
          '<text x="1345" y="55" text-anchor="end" class="small">'+e(b['code'])+' · РЕД. 02</text>',
          '<text x="1345" y="85" text-anchor="end" class="small">ГАБАРИТНЫЙ ЭСКИЗ · ДЛЯ СОГЛАСОВАНИЯ</text>']
    # Orthographic views use exact same coordinates as the presentation mesh.
    views=[('Вид спереди',55,145,780,360,lambda v:(v[0],-v[2],-v[1]),'front'),('Вид сбоку',910,145,400,360,lambda v:(v[1],-v[2],v[0]),'side'),('Вид сверху',55,550,780,270,lambda v:(v[0],v[1],v[2]),'top')]
    for title,x,y,w,h,proj,kind in views:
        ps=[([proj(v) for v in f['v']],f) for f in faces]
        pts=[p for vs,f in ps for p in vs];xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts)
        scale=min((w-90)/(xmax-xmin),(h-85)/max(1,ymax-ymin));ox=x+(w-(xmax-xmin)*scale)/2-xmin*scale;oy=y+30+(h-85-(ymax-ymin)*scale)/2-ymin*scale
        body.append(f'<text x="{x}" y="{y}" class="label">{title}</text>')
        for vs,f in sorted(ps,key=lambda a:sum(v[2] for v in a[0])/len(a[0])):
            coords=' '.join(f'{ox+v[0]*scale:.1f},{oy+v[1]*scale:.1f}' for v in vs)
            body.append(f'<polygon points="{coords}" fill="{"#f2e9de" if f["m"]=="wood" else "#dce5df"}" stroke="#354d40" stroke-width=".85"/>')
        left=ox+xmin*scale;right=ox+xmax*scale;top=oy+ymin*scale;bottom=oy+ymax*scale
        def hd(a,c,yy,label):
            body.append(f'<path class="measure" d="M{a} {bottom+4}V{yy+9}M{c} {bottom+4}V{yy+9}"/><path class="measure" marker-start="url(#arrow)" marker-end="url(#arrow)" d="M{a} {yy}H{c}"/><text x="{(a+c)/2}" y="{yy-8}" text-anchor="middle" class="dim">{label}</text>')
        hd(left,right,bottom+35,b['length'] if kind!='side' else b['depth'])
        if kind in ('front','side'):
            xx=right+30
            body.append(f'<path class="measure" d="M{right+3} {top}H{xx+8}M{right+3} {bottom}H{xx+8}"/><path class="measure" marker-start="url(#arrow)" marker-end="url(#arrow)" d="M{xx} {top}V{bottom}"/><text x="{xx+12}" y="{(top+bottom)/2}" class="dim">{b["height"]}</text>')
    body.extend(['<text x="915" y="575" class="label">Предварительные габариты, мм</text>',f'<text x="915" y="615" font-size="24">{b["length"]} × {b["depth"]} × {b["height"]}</text>',f'<text x="915" y="650" class="small">Высота сиденья: {b["seatHeight"]}</text>',
                 '<text x="915" y="695" class="small">Предлагаемые материалы:</text>','<text x="915" y="723" class="small">литые чугунные опоры, дерево.</text>',
                 '<path d="M55 873H1345" stroke="#cbd6ce"/>','<text x="55" y="908" class="small">Эскиз для выбора внешнего вида и обсуждения заказа. Размеры предварительные. Масштаб условный.</text>',
                 '<text x="55" y="936" class="small">Сечения, соединения, оснастка и крепление к основанию разрабатываются после согласования с производством.</text>',
                 '<text x="55" y="964" class="small">Тула · ЦЕНТРСПЕЦМЕТАЛЛ · csm-factory@bk.ru</text>'])
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="990" viewBox="0 0 1400 990"><title>'+e('Габаритный эскиз «'+b['name']+'»')+'</title>'+''.join(body)+'</svg>'
    (ROOT/asset(b,'drawing.svg')).write_text(svg,encoding='utf-8')

def joint_drawing(b):
    if b.get('family')=='ribbed':return ribbed_joint_drawing(b)
    # Enlarged front elevation of the actual mating solids; fastener is conventional.
    parts=mesh(b,return_parts=True)
    selected=[]
    for p in parts:
        low=min(v[1] for v in p['profile']);high=max(v[1] for v in p['profile'])
        if p['g'] in ('tiebar','plate-right','fastener-right') or (p['g']=='support-right' and low>=375 and high<=425):selected.append(p)
        elif p['g']=='seat' and min(v[0] for v in p['profile'])<=0<=max(v[0] for v in p['profile']):selected.append(p)
    sx=lambda x:120+(x-450)*3.5
    sy=lambda z:580-(z-350)*3.5
    body=['<rect width="1400" height="990" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#233e32}.small{font-size:18px;fill:#68766e}.label{font-size:22px;font-weight:bold}.leader{fill:none;stroke:#72917b;stroke-width:2}</style>',
          '<text x="60" y="60" font-size="21" font-weight="bold">ЦЕНТРСПЕЦМЕТАЛЛ</text>',f'<text x="60" y="110" font-size="32" font-weight="bold">Узел 01 · Перемычка под сиденьем · {e(b["name"])}</text>',
          '<text x="1340" y="60" text-anchor="end" class="small">РЕД. 02 · СХЕМА ДЛЯ СОГЛАСОВАНИЯ</text>',
          '<text x="60" y="158" class="small">Увеличенный вид спереди. Показана правая сторона; левая собирается зеркально.</text>']
    def key(p):return 0 if p['g']=='seat' else (1 if p['g']=='tiebar' else 2 if p['g']=='plate-right' else 3 if p['g']=='support-right' else 4)
    for p in sorted(selected,key=key):
        x1=max(450,p['x'][0]);x2=min(740,p['x'][1]);z1=min(v[1] for v in p['profile']);z2=max(v[1] for v in p['profile'])
        if x2<=x1:continue
        color='#eee1ce' if p['m']=='wood' else '#a4b5a7' if p['g']=='support-right' else '#c9d7cb' if p['g']=='plate-right' else '#6e7f73' if p['g']=='tiebar' else '#87918a'
        body.append(f'<rect x="{sx(x1):.1f}" y="{sy(z2):.1f}" width="{(x2-x1)*3.5:.1f}" height="{(z2-z1)*3.5:.1f}" fill="{color}" stroke="#344b3d" stroke-width="1.5"/>')
    body.extend([f'<path d="M{sx(600)} {sy(398)}H{sx(695)}" stroke="#5e7564" stroke-width="1.5" stroke-dasharray="9 5"/>',
      '<text x="150" y="675" class="label">01 · Продольная перемычка</text>',f'<path class="leader" d="M340 645V530L{sx(570)} {sy(390)}"/>',
      '<text x="620" y="735" class="label">02 · Торцевая пластина</text>',f'<path class="leader" d="M740 705V600L{sx(625)} {sy(380)}"/>',
      '<text x="1040" y="575" class="label">03 · Литая боковина</text>',f'<path class="leader" d="M1040 548H960L{sx(655)} {sy(390)}"/>',
      '<text x="60" y="245" class="label">Деревянный настил</text>',f'<path class="leader" d="M300 250L{sx(535)} {sy(440)}"/>',
      '<text x="1020" y="305" class="label">Крепёж</text>',f'<path class="leader" d="M1020 325H980L{sx(678)} {sy(398)}"/>',
      '<text x="60" y="805" class="small">Перемычка заканчивается у пластины. Пластина прилегает к внутренней грани верхней части боковины.</text>',
      '<text x="60" y="842" class="small">Болты, шайбы и гайки показаны условно. Отверстия, посадки, сечения и крепёж назначаются в рабочем проекте.</text>',
      '<path d="M60 885H1340" stroke="#cbd6ce"/>','<text x="60" y="925" class="small">Геометрическая сборочная схема для согласования. Расчёт прочности и литейная документация не выполнены.</text>',
      '<text x="60" y="960" class="small">Тула · ЦЕНТРСПЕЦМЕТАЛЛ · csm-factory@bk.ru</text>'])
    (ROOT/asset(b,'joint.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="990" viewBox="0 0 1400 990"><title>Узел крепления перемычки</title>'+''.join(body)+'</svg>',encoding='utf-8')

def ribbed_joint_drawing(b):
    parts=mesh(b,return_parts=True);body=['<rect width="1400" height="990" fill="white"/>','<style>text{font-family:Arial,sans-serif;fill:#233e32}.small{font-size:18px;fill:#68766e}.label{font-size:23px;font-weight:bold}</style>',
      '<text x="60" y="60" font-size="21" font-weight="bold">ЦЕНТРСПЕЦМЕТАЛЛ</text>','<text x="60" y="112" font-size="34" font-weight="bold">Ритм · Схема опирания параметрического настила</text>',
      '<text x="60" y="157" class="small">Вид с торца. Ребро и опора из соседних сечений показаны условно на одном виде.</text>']
    # Show one central rib, both bearer sections, and the cast support crosshead.
    selected=[p for p in parts if p['g']=='rib-10' or p['g'].startswith('bearer-') or (p['g']=='support-right' and min(v[1] for v in p['profile'])>=309 and max(v[1] for v in p['profile'])<=351)]
    for p in sorted(selected,key=lambda p:0 if p['g'].startswith('bearer') else 1 if p['g']=='support-right' else 2):
        xy=' '.join(f'{700+y*2.2:.1f},{640-(z-300)*2.2:.1f}' for y,z in p['profile'])
        color='#ebd5b7' if p['m']=='wood' else '#6d8373' if p['g']=='support-right' else '#a8b8ad'
        body.append(f'<polygon points="{xy}" fill="{color}" stroke="#355240" stroke-width="1.4"/>')
    body.extend(['<text x="60" y="230" class="label">01 · Профилированное деревянное ребро</text>',
      '<path d="M510 240 570 285 700 310" fill="none" stroke="#73907c" stroke-width="2"/>',
      '<text x="60" y="705" class="label">02 · Две продольные стальные балки</text>',
      '<path d="M425 670V565L380 485" fill="none" stroke="#73907c" stroke-width="2"/>',
      '<text x="790" y="705" class="label">03 · Верхняя площадка боковины</text>',
      '<path d="M960 670V615L900 570" fill="none" stroke="#73907c" stroke-width="2"/>',
      '<text x="60" y="790" class="small">Ребро опирается на две балки. Каждая балка опирается на обе чугунные боковины.</text>',
      '<text x="60" y="830" class="small">Базовый вариант: 21 ребро. На странице можно сравнить 25 и 29 рёбер; рабочий крепёж не назначен.</text>',
      '<path d="M60 880H1340" stroke="#cbd6ce"/>','<text x="60" y="920" class="small">Конструктивная схема для обсуждения. Прочность, крепления и изготовление деревянных рёбер требуют проработки.</text>',
      '<text x="60" y="960" class="small">Тула · ЦЕНТРСПЕЦМЕТАЛЛ · csm-factory@bk.ru</text>'])
    (ROOT/asset(b,'joint.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="990" viewBox="0 0 1400 990"><title>Схема параметрического настила</title>'+''.join(body)+'</svg>',encoding='utf-8')

def prepare_assets():
    (ROOT/'assets/benches').mkdir(exist_ok=True)
    for b in BENCHES:
        faces=mesh(b);render(b,faces)
        # Show one whole side support without boards; the supply option is a pair.
        support=[f for f in faces if f['g']=='support-right']
        support=[{**f,'v':[[v[0]-650,v[1],v[2]] for v in f['v']]} for f in support]
        render(b,support,'support');drawing(b,faces);joint_drawing(b)
        (ROOT/asset(b,'geometry.json')).write_text(json.dumps({'id':b['id'],'length':b['length'],'faces':faces},separators=(',',':')),encoding='utf-8')
        if b.get('family')=='ribbed':
            for count in (25,29):
                (ROOT/asset(b,f'geometry-{count}.json')).write_text(json.dumps({'id':b['id'],'length':b['length'],'ribCount':count,'faces':mesh(b,rib_count=count)},separators=(',',':')),encoding='utf-8')
        if 'render.webp' in hero_asset(b):
            with Image.open(ROOT/asset(b,'render.webp')) as im:im.convert('RGB').save(ROOT/asset(b,'social.jpg'),quality=92)

def bench_card(b,r):
    title=b['type']+' «'+b['name']+'»'
    return f'''<article class="product-card bench-card" data-product-id="bench-{b['id']}" data-search="{e((title+' чугунная опоры скамейки '+b['description']).lower())}"><a class="product-media" href="{r}{route(b)}"><img src="{r}{hero_asset(b)}" width="1200" height="900" loading="lazy" decoding="async" alt="{e(title)} — проектная визуализация"><span class="product-status model">Проектная модель</span></a><div class="product-body"><p class="product-category">{e(b['code'])} · Чугун и дерево</p><h3><a href="{r}{route(b)}">{e(title)}</a></h3><p>{e(b['audience'])}</p><p class="bench-card-size">Эскиз: {b['length']} × {b['depth']} × {b['height']} мм</p><div class="card-foot"><span>Расчёт после согласования</span><a href="{r}{route(b)}">Модель и эскиз ↗</a></div></div></article>'''

def ordered_benches():return sorted(BENCHES,key=lambda b:({'rhythm':0,'arc':1,'flow':2}.get(b['id'],3)))

def bench_cards(r,items=None):return ''.join(bench_card(b,r) for b in (ordered_benches() if items is None else items))

def rib_options(b,r):
    buttons=''.join(f'<button type="button" data-bench-ribs="{count}" data-geometry="{r}{asset_url(b,"geometry.json" if count==21 else f"geometry-{count}.json")}" aria-pressed="{str(count==21).lower()}">{count}</button>' for count in (21,25,29))
    return f'<div class="bench-option"><span>Рёбер настила</span><div class="bench-lengths" role="group" aria-label="Количество деревянных рёбер">{buttons}</div></div><p class="bench-density-note">Плотность меняет ритм поверхности. Рендер и PDF показывают базовый вариант: 21 ребро.</p>'

def teaser(r):
    return f'''<section class="container section bench-teaser"><div class="section-heading"><div><p class="eyebrow">Новая проектная коллекция</p><h2>Скамейки.<br>Свои формы.</h2></div><a class="text-link" href="{r}{BENCH_ROUTE}">Все модели · {len(BENCHES)} ↗</a></div><p class="bench-section-lead">Новые силуэты литья и параметрический образец. Выберите форму, сравните варианты в 3D и обсудите изготовление.</p><div class="product-grid bench-grid">{bench_cards(r,[b for b in ordered_benches() if b.get("family")][:3])}</div><p class="bench-disclosure">{DISCLOSURE}</p></section>'''

def build_benches(api):
    page=api['page'];button=api['button'];faq=api['faq'];banner=api['contact_banner'];absolute=api['absolute']
    r='../../'
    catalog=f'''<section class="container bench-collection-hero"><div><p class="eyebrow"><i class="dot"></i>Чугун и дерево · Проектная коллекция</p><h1>Скамейки,<br>которые начинаются<br>с вашего пространства.</h1><p>Собственные эскизы: плавные литые опоры, открытые арки и параметрический настил. Сравните формы, размеры и конструктивные схемы.</p><a class="button" href="#models">Выбрать модель <span aria-hidden="true">↓</span></a></div><a class="bench-collection-art" href="{r}{route(next(b for b in BENCHES if b["id"]=="rhythm"))}"><img src="{r}{hero_asset(next(b for b in BENCHES if b["id"]=="rhythm"))}" width="1200" height="900" fetchpriority="high" alt="Параметрическая скамья Ритм на чугунных опорах"><span>ЦСМ СК-06 · Ритм <span aria-hidden="true">↗</span></span></a></section><section class="container section" id="models"><div class="section-heading"><div><p class="eyebrow">От классики к новым формам</p><h2>Выберите свою скамейку.</h2></div><p>Общий вид, габаритный эскиз<br>и отдельная литая опора.</p></div><div class="product-grid bench-grid">{bench_cards(r)}</div><p class="bench-disclosure">{DISCLOSURE}</p></section><section class="bench-supply-band"><div class="container text-columns"><div><p class="eyebrow">Для мастерских и партнёров</p><h2>Скамейка целиком.<br>Или пара литых опор.</h2><p>Обсудим комплектацию под ваш проект: с деревянным настилом либо только боковины для собственной сборки. Состав поставки, дерево, покрытие и крепёж определяются при расчёте.</p>{button('Рассчитать комплект опор','custom',extra='data-message="Интересуют чугунные опоры для скамеек. Модель: ____. Количество комплектов: ____. Город: ____."')}</div><div><h2>От эскиза к заказу</h2><ol><li>Выбираем модель, габариты и количество.</li><li>Проверяем конструкцию и технологию с литейкой.</li><li>Согласуем оснастку, материалы, комплектацию и стоимость.</li><li>Подготавливаем документацию и условия изготовления.</li></ol><p class="bench-disclosure">Коллекция находится на стадии эскизов. Возможность изготовления и сроки подтверждаются производством по конкретному заказу.</p></div></div></section><section class="container section article-copy"><h2>Чугунные скамейки и литые боковины в Туле</h2><p>ЦЕНТРСПЕЦМЕТАЛЛ развивает направление садовых и парковых скамеек с литыми опорами. В коллекции представлены эскизы со спинкой и без спинки, с подлокотниками и декоративным рисунком боковин. В основе предложения — возможности литейного производства в Туле и разработка изделия под конкретную задачу.</p><p>Для запроса расчёта укажите модель, желаемые размеры, количество и город получения. Если нужен свой рисунок боковины, приложите эскиз или описание. Отдельно обсудим поставку чугунных опор для столярных мастерских и производителей уличной мебели.</p></section>'''+banner()
    collection={'@type':'CollectionPage','name':'Чугунные скамейки — проектная коллекция','url':absolute(BENCH_ROUTE),'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i,'name':b['type']+' «'+b['name']+'»','url':absolute(route(b))} for i,b in enumerate(BENCHES,1)]}}
    page(BENCH_ROUTE,'Чугунные скамейки и опоры в Туле — проекты | ЦЕНТРСПЕЦМЕТАЛЛ','Собственные проекты скамеек в Туле: литые опоры, современные формы и параметрический настил. Визуализации, эскизы и обсуждение изготовления.',catalog,[('Каталог','catalog/'),('Чугунные скамейки',None)],[collection],asset(next(b for b in BENCHES if b['id']=='rhythm'),'social.jpg'))
    for b in BENCHES:
        title=b['type']+' «'+b['name']+'»'
        message='Прошу рассмотреть изготовление: '+title+' ('+b['code']+'). Комплектация: скамейка с настилом. Предварительная длина: 1800 мм. Количество: ____. Город: ____.'
        request=button('Рассчитать изготовление','custom',extra='id="bench-request" data-message="'+e(message)+'"')
        options=''.join(f'<li>{e(f)}</li>' for f in b['features'])
        specs=''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k,v in [('Артикул проекта',b['code']),('Габариты эскиза',f'{b["length"]} × {b["depth"]} × {b["height"]} мм'),('Высота сиденья',str(b['seatHeight'])+' мм'),('Предлагаемые материалы','Чугунные опоры, деревянный настил'),('Статус','Эскизная разработка')])
        related=''.join(bench_card(o,r) for o in [q for q in ordered_benches() if q['id']!=b['id']][:3])
        questions=[('Можно заказать только чугунные опоры?','Да, можно направить запрос на пару боковин или партию опор для собственной сборки. Состав комплекта, соединения, оснастку и стоимость согласуем с производством.'),('Можно изменить размеры и рисунок?','Укажите желаемую длину, посадку, рисунок боковины и место установки. Изменения проверяются при разработке конструкции и подготовке модели для литья.'),('Это фотография готовой скамейки?','На странице показаны проектная визуализация и габаритный эскиз. Изготовление образца, рабочая документация и сроки обсуждаются после согласования конструкции.')]
        content=f'''<section class="container bench-product" data-bench="{b['id']}"><div class="bench-main"><div class="bench-viewer" id="bench-viewer" data-geometry="{r}{asset_url(b,'geometry.json')}" data-support="{r}{asset_url(b,'support.svg')}" data-render="{r}{hero_asset(b)}" data-joint="{r}{asset_url(b,'joint.svg')}"><img id="bench-fallback" src="{r}{hero_asset(b)}" width="1200" height="900" fetchpriority="high" alt="{e(title)} — проектная визуализация"><canvas id="bench-gl" width="1200" height="900" aria-label="Интерактивная 3D-модель скамейки" hidden></canvas><svg id="bench-canvas" viewBox="0 0 1200 900" aria-label="Вращаемая проектная модель скамейки" role="img" hidden></svg><span class="bench-view-tag">Проектная визуализация</span><span class="bench-view-help js-only">Потяните, чтобы повернуть</span></div><div class="bench-view-buttons js-only" role="group" aria-label="Ракурс модели"><button type="button" data-bench-view="render" aria-pressed="true">Рендер 1,8 м</button><button type="button" data-bench-view="perspective" aria-pressed="false">3D</button><button type="button" data-bench-view="joint" aria-pressed="false">Узел</button><button type="button" data-bench-view="front" aria-pressed="false">Спереди</button><button type="button" data-bench-view="side" aria-pressed="false">Сбоку</button><button type="button" data-bench-view="support" aria-pressed="false">Опора</button></div><p class="bench-disclosure">{DISCLOSURE}</p></div><div class="bench-summary"><p class="eyebrow">{e(b['code'])} · Проектная коллекция</p><h1>{e(b['type'])}<br>«{e(b['name'])}»</h1><p>{e(b['description'])}</p><ul class="bench-highlights">{options}</ul><div class="bench-config js-only"><div class="bench-option"><span>Длина эскиза</span><div class="bench-lengths" role="group" aria-label="Желаемая длина"><button type="button" data-bench-length="1500" aria-pressed="false">1,5 м</button><button type="button" data-bench-length="1800" aria-pressed="true">1,8 м</button><button type="button" data-bench-length="2000" aria-pressed="false">2 м</button></div></div><div class="bench-option"><span>Цвет литья на экране</span><div class="bench-swatches" role="group" aria-label="Визуальный цвет литья"><button type="button" data-bench-color="#33453d" style="--swatch:#33453d" aria-label="Лесной зелёный" aria-pressed="true"></button><button type="button" data-bench-color="#313437" style="--swatch:#313437" aria-label="Графитовый" aria-pressed="false"></button><button type="button" data-bench-color="#776951" style="--swatch:#776951" aria-label="Тёплый бронзовый" aria-pressed="false"></button></div></div><label class="bench-option"><span>Запросить расчёт</span><select id="bench-supply"><option value="Скамейка с настилом">Скамейка с настилом</option><option value="Пара чугунных опор">Пара чугунных опор</option></select></label><p>Варианты помогают сформировать запрос. Итоговое исполнение согласуется.</p></div><div class="bench-order"><span>Стоимость после согласования</span>{request}</div><p class="bench-current" id="bench-current" aria-live="polite">Эскиз: 1800 мм · Скамейка с настилом</p></div></section><section class="container section bench-details"><div class="section-heading"><div><p class="eyebrow">Замысел модели</p><h2>Характер — в деталях.</h2></div></div><div class="text-columns"><div class="article-copy"><p>{e(b['detail'])}</p><h3>Что согласуем с вами</h3><p>Размеры, рисунок литья, древесину, окраску и состав поставки. Для длинных исполнений отдельно проверяется необходимость дополнительных опор. Крепления к основанию выбираются под место установки.</p></div><dl class="features bench-specs">{specs}</dl></div></section><section class="bench-drawing-band" id="drawing"><div class="container"><div class="section-heading"><div><p class="eyebrow">Для выбора и обсуждения</p><h2>Габаритный эскиз</h2></div><div class="bench-downloads"><a class="button secondary" href="{r}{asset_url(b,'drawing.svg')}" download>Скачать SVG ↓</a><a class="button" href="{r}{asset_url(b,'drawing.pdf')}" download>Скачать PDF ↓</a></div></div><a class="bench-drawing" href="{r}{asset_url(b,'drawing.svg')}" target="_blank" rel="noopener" aria-label="Открыть габаритный эскиз крупно"><img src="{r}{asset_url(b,'drawing.svg')}" width="1400" height="990" loading="lazy" alt="{e(title)}: виды спереди, сбоку и сверху с предварительными размерами"></a><p class="bench-disclosure">Размеры относятся к базовому эскизу 1800 мм. Это материал для согласования внешнего вида; рабочая документация подготавливается после проверки конструкции производством.</p></div></section><section class="container section bench-joint-section"><div class="section-heading"><div><p class="eyebrow">Узел 01</p><h2>Как закреплена перемычка</h2></div><a class="text-link" href="{r}{asset_url(b,'joint.svg')}" target="_blank" rel="noopener">Открыть схему ↗</a></div><a class="bench-drawing" href="{r}{asset_url(b,'joint.svg')}" target="_blank" rel="noopener"><img src="{r}{asset_url(b,'joint.svg')}" width="1400" height="990" loading="lazy" alt="Перемычка через торцевую пластину прикреплена к литой боковине"></a><p class="bench-disclosure">Перемычка находится под настилом. На каждом конце — торцевая пластина, прилегающая к боковине. Крепёж на схеме условный; его подбор и рабочие размеры требуют расчёта.</p></section><section class="container section bench-support-block"><figure><img src="{r}{asset_url(b,'support.svg')}" width="1200" height="900" loading="lazy" alt="Проект отдельной чугунной боковины модели {e(b['name'])}"><figcaption>Визуализация одной опоры. Запрос поставки — пара или партия.</figcaption></figure><div><p class="eyebrow">Для собственной сборки</p><h2>Литая опора<br>как отдельное изделие.</h2><p>Столярной мастерской или производителю мебели можно обсудить только чугунные боковины. Деревянный настил и сборку вы выполняете под свой проект.</p><p>Укажите количество пар, размеры настила и пожелания к покрытию. Геометрию соединений, комплект крепежа и необходимость оснастки определяем при расчёте.</p>{button('Запросить пару опор','custom',extra='data-message="'+e('Интересует пара чугунных опор для модели «'+b['name']+'» ('+b['code']+'). Количество пар: ____. Город: ____.')+'"')}</div></section><section class="container section"><div class="faq-grid"><div><p class="eyebrow">Перед расчётом</p><h2>Обсудим исполнение.</h2></div>{faq(questions)}</div></section><section class="container section"><div class="section-heading"><h2>Другой характер</h2><a class="text-link" href="{r}{BENCH_ROUTE}">Все скамейки ↗</a></div><div class="product-grid bench-related">{related}</div></section>'''+banner()
        if b.get('family')=='ribbed':
            content=content.replace('<div class="bench-config js-only">','<div class="bench-config js-only">'+rib_options(b,r))
            content=content.replace('data-bench="rhythm"','data-bench="rhythm" data-ribbed="true"')
            content=content.replace('Чугунные опоры, деревянный настил','Чугунные опоры, стальные балки, деревянные рёбра')
            content=content.replace('Как закреплена перемычка','Как устроен параметрический настил')
            content=content.replace('Перемычка через торцевую пластину прикреплена к литой боковине','Деревянные рёбра опираются на две стальные балки, установленные на чугунных боковинах')
            content=content.replace('Перемычка находится под настилом. На каждом конце — торцевая пластина, прилегающая к боковине. Крепёж на схеме условный; его подбор и рабочие размеры требуют расчёта.','Каждое деревянное ребро опирается на две продольные стальные балки. Балки опираются на чугунные боковины. Крепление рёбер и балок, сечения и технология изготовления требуют проработки.')
            content=content.replace('Размеры относятся к базовому эскизу 1800 мм.','Размеры относятся к базовому эскизу 1800 мм с 21 ребром.')
        gl_version=hashlib.sha256((ROOT/'bench-webgl.js').read_bytes()).hexdigest()[:10]
        content+=f'<script src="{r}bench-webgl.js?v={gl_version}" defer></script>'
        viewer_version=hashlib.sha256((ROOT/'bench-viewer.js').read_bytes()).hexdigest()[:10]
        content+=f'<script src="{r}bench-viewer.js?v={viewer_version}" defer></script>'
        entity={'@type':'CreativeWork','name':title+' — проект','description':b['description'],'url':absolute(route(b)),'image':absolute(asset(b,'social.jpg')),'creator':{'@id':absolute('#organization')},'creativeWorkStatus':'Эскизная разработка'}
        page(route(b),title+' — эскиз и расчёт в Туле | ЦЕНТРСПЕЦМЕТАЛЛ',b['description'],content,[('Каталог','catalog/'),('Чугунные скамейки',BENCH_ROUTE),(b['name'],None)],[entity],asset(b,'social.jpg'))
