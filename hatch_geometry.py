"""Own conceptual castings in millimetres; no load class or fit is certified.

Frame: 90 high; lid seat: z=60. Opening changes without scaling the seat,
lid thickness or illustrative 4 mm radial/side clearance.
"""
import math
from lamp_geometry import Assembly
N=64
def shape(radius,square=False):
    return [(-radius,-radius),(radius,-radius),(radius,radius),(-radius,radius)] if square else [(radius*math.cos(i*math.tau/N),radius*math.sin(i*math.tau/N)) for i in range(N)]
def clip(poly,mask):
    """Intersection of two convex CCW polygons."""
    output=list(poly)
    for a,b in zip(mask,mask[1:]+mask[:1]):
        if not output:break
        result=[];prev=output[-1]
        def side(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
        sp=side(prev)
        for cur in output:
            sc=side(cur)
            if (sc>=-1e-7)!=(sp>=-1e-7):
                t=sp/(sp-sc);result.append((prev[0]+(cur[0]-prev[0])*t,prev[1]+(cur[1]-prev[1])*t))
            if sc>=-1e-7:result.append(cur)
            prev=cur;sp=sc
        output=result
    clean=[]
    for p in output:
        if not clean or math.dist(p,clean[-1])>1e-6:clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-6:clean.pop()
    if len(clean)<3:return []
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(clean,clean[1:]+clean[:1]))/2
    return clean if area>1e-5 else []
def rect(x1,x2,y1,y2):return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]
def surface_cells(radius,square):
    # A closed bottom under two genuine blind pockets; the upper skin is split
    # around the openings, so the pockets are not painted onto a solid disk.
    pos=radius*.62;cuts=[-radius,-pos-20,-pos+20,pos-20,pos+20,radius];ys=[-radius,-9,9,radius];outline=shape(radius,square);cells=[]
    for i,(x1,x2) in enumerate(zip(cuts,cuts[1:])):
        for j,(y1,y2) in enumerate(zip(ys,ys[1:])):
            if i in (1,3) and j==1:continue
            p=clip(rect(x1,x2,y1,y2),outline)
            if p:cells.append(p)
    return cells
def ring(a,outer,inner,z1,z2,square):
    op=shape(outer,square);ip=shape(inner,square)
    for i in range(len(op)):
        j=(i+1)%len(op);a.prism([op[i],op[j],ip[j],ip[i]],z1,z2)
def bar(p,q,width):
    dx=q[0]-p[0];dy=q[1]-p[1];ln=math.hypot(dx,dy);nx=-dy/ln*width/2;ny=dx/ln*width/2
    return [(p[0]-nx,p[1]-ny),(q[0]-nx,q[1]-ny),(q[0]+nx,q[1]+ny),(p[0]+nx,p[1]+ny)]
def decorations(model,r,count):
    if model['id']=='orbit':
        for rr in [r*.26,r*.46,r*.66,r*.86]:
            for i in range(8):
                for k in range(5):
                    t=(i+(k/5)*.82)*math.tau/8;u=(i+((k+1)/5)*.82)*math.tau/8
                    yield [((rr+d)*math.cos(v),(rr+d)*math.sin(v)) for d,v in [(3,t),(3,u),(-3,u),(-3,t)]],f'ring-{round(rr)}'
        for i in range(8):
            t=(i+.91)*math.tau/8;yield bar((r*.27*math.cos(t),r*.27*math.sin(t)),(r*.88*math.cos(t),r*.88*math.sin(t)),6),f'spoke-{i}'
    elif model['id']=='quarter':
        for i,x in enumerate(range(int(-r+45),int(r-20),80)):
            for j,y in enumerate(range(int(-r+45),int(r-20),80)):
                sign=1 if (i+j)%2 else -1
                yield rect(x-23,x+23,y-3,y+3),f'tile-{i}-{j}'
                yield rect(x-23,x-17,*sorted([y,y+sign*28])),f'tile-{i}-{j}'
    else:
        for i in range(count):
            pts=[]
            for k in range(13):
                t=k/12;rr=r*(.22+.68*t);theta=i*math.tau/count+.72*t*t;pts.append((rr*math.cos(theta),rr*math.sin(theta)))
            edges=[]
            for k,p in enumerate(pts):
                prev=pts[max(0,k-1)];nxt=pts[min(len(pts)-1,k+1)];dx=nxt[0]-prev[0];dy=nxt[1]-prev[1];ln=math.hypot(dx,dy)
                nx=-dy/ln*3.5;ny=dx/ln*3.5;edges.append(((p[0]-nx,p[1]-ny),(p[0]+nx,p[1]+ny)))
            for (p,q),(u,v) in zip(edges,edges[1:]):yield [p,u,v,q],f'ray-{i}'

def mesh(model,opening=600,ray_count=None,return_parts=False):
    a=Assembly();square=model['shape']=='square';r=opening/2;lid=r+30
    a.section='frame';a.group='frame-flange';ring(a,r+100,r,0,18,square)
    a.group='frame-seat';ring(a,r+34,r,18,60,square)
    a.group='frame-wall';ring(a,r+65,r+34,18,90,square)
    a.section='lid';a.group='lid-body';a.prism(shape(lid,square),60,76)
    cells=surface_cells(lid,square)
    a.group='lid-skin'
    for cell in cells:a.prism(cell,76,86)
    a.group='lid-ribs'
    if square:
        for p,q in [((-r+12,0),(r-12,0)),((0,-r+12),(0,r-12))]:a.prism(bar(p,q,16),26,60)
    else:
        for i in range(6):
            t=i*math.tau/6;a.prism(bar((0,0),((r-12)*math.cos(t),(r-12)*math.sin(t)),14),26,60)
    safe=shape(lid-15,square)
    for poly,name in decorations(model,lid,ray_count or model.get('rayCount',18)):
        poly=clip(poly,safe)
        if not poly:continue
        a.group=name
        for cell in cells:
            p=clip(poly,cell)
            if p:a.prism(p,86,90)
    return a.parts if return_parts else a.faces

def section_polygons(opening=600):
    r=opening/2
    return [('frame',[rect(-r-100,-r,0,18),rect(r,r+100,0,18),rect(-r-34,-r,18,60),rect(r,r+34,18,60),rect(-r-65,-r-34,18,90),rect(r+34,r+65,18,90)]),('lid',[rect(-r-30,r+30,60,86),rect(-r+12,r-12,26,60)])]
