"""Own presentation geometry. Dimensions and joints are proposals for review.

Convex solids are retained for contact checks; no competitor meshes are used.
Units: mm. The post is hollow and the decorative cast boot is not the mast.
"""
import math

class Assembly:
    def __init__(self):self.parts=[];self.faces=[];self.group='base';self.section='base'
    def solid(self,vertices,loops,material='iron'):
        pid=len(self.parts)
        self.parts.append({'id':pid,'g':self.group,'s':self.section,'v':vertices,'loops':loops,'m':material})
        for loop in loops:self.faces.append({'part':pid,'g':self.group,'s':self.section,'m':material,'v':[vertices[i] for i in loop]})
    def prism(self,points,z1,z2,material='iron'):
        n=len(points);v=[[x,y,z] for z in [z1,z2] for x,y in points]
        self.solid(v,[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],material)
    def box(self,x1,x2,y1,y2,z1,z2,material='iron'):
        self.prism([(x1,y1),(x2,y1),(x2,y2),(x1,y2)],z1,z2,material)
    def ring(self,ro1,ro2,ri1,ri2,z1,z2,material='iron',cx=0,cy=0,n=24):
        if not ri1 and not ri2:
            lower=[[cx+ro1*math.cos(i*math.tau/n),cy+ro1*math.sin(i*math.tau/n),z1] for i in range(n)]
            upper=[[cx+ro2*math.cos(i*math.tau/n),cy+ro2*math.sin(i*math.tau/n),z2] for i in range(n)]
            self.solid(lower+upper,[list(range(n-1,-1,-1)),list(range(n,n*2))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],material);return
        for i in range(n):
            t=i*math.tau/n;u=(i+1)*math.tau/n
            v=[]
            for ro,ri,z in [(ro1,ri1,z1),(ro2,ri2,z2)]:
                v.extend([[cx+r*math.cos(a),cy+r*math.sin(a),z] for r,a in [(ro,t),(ro,u),(ri,u),(ri,t)]])
            self.solid(v,[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],material)
    def arch(self,h):
        sections=[]
        for i in range(37):
            t=math.pi-i*math.pi/36;x=250+250*math.cos(t);z=h-310+290*math.sin(t)
            dx=250*math.sin(t);dz=-290*math.cos(t);ln=math.hypot(dx,dz)
            sections.append(((x-dz/ln*20,z+dx/ln*20),(x+dz/ln*20,z-dx/ln*20)))
        for (p,q),(r,s) in zip(sections,sections[1:]):
            v=[[x,y,z] for y in [-22,22] for x,z in [p,r,s,q]]
            self.solid(v,[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])

def mesh(model,height=3000,fin_count=None,return_parts=False):
    a=Assembly();h=height
    a.group='flange';a.ring(210,210,37,37,0,20,'metal',n=8)
    a.group='boot';a.ring(105,64,45,45,20,320)
    a.ring(64,64,45,45,320,360)
    a.group='anchors'
    for t in [math.pi/4+i*math.pi/2 for i in range(4)]:
        a.ring(11,11,0,0,20,34,'metal',cx=180*math.cos(t),cy=180*math.sin(t),n=6)
    top=h-(460 if model['id']=='facet' else 310 if model['id']=='vault' else 300)
    a.group='post';a.section='post';a.ring(45,45,37,37,20,top,'metal')
    a.section='head';a.group='adapter';a.ring(56,56,16,16,top-30,top+20)
    if model['id']=='facet':
        a.group='frame';a.box(-180,180,-70,70,h-460,h-430)
        a.box(-180,-150,-70,70,h-430,h-30);a.box(150,180,-70,70,h-430,h-30)
        a.box(-180,180,-70,70,h-30,h)
        a.group='light-housing';a.box(-130,130,-50,50,h-80,h-30,'metal')
        a.group='diffuser';a.box(-130,130,-50,50,h-86,h-80,'light')
    elif model['id']=='vault':
        a.group='arch';a.arch(h)
        a.group='cap';a.ring(150,30,0,0,h-380,h-310,cx=500)
        a.group='lower-rim';a.ring(95,120,0,0,h-620,h-570,cx=500)
        a.group='diffuser';a.ring(105,105,0,0,h-570,h-380,'light',cx=500)
        a.group='lantern-struts'
        for t in [math.pi/4+i*math.pi/2 for i in range(4)]:
            cx=500+114*math.cos(t);cy=114*math.sin(t)
            a.ring(8,8,0,0,h-575,h-375,'metal',cx=cx,cy=cy,n=8)
    else:
        a.group='lower-rim';a.ring(150,150,35,35,h-300,h-270)
        a.group='diffuser';a.ring(105,105,0,0,h-270,h-45,'light')
        a.group='cap';a.ring(130,120,0,0,h-45,h)
        for i in range(fin_count or model.get('finCount',16)):
            n=fin_count or model.get('finCount',16);t=i*math.tau/n;outer=150+30*math.sin(3*t)**2
            a.group=f'fin-{i}'
            points=[(r*math.cos(t)-s*math.sin(t),r*math.sin(t)+s*math.cos(t)) for r,s in [(110,-6),(outer,-6),(outer,6),(110,6)]]
            a.prism(points,h-280,h-30)
    return a.parts if return_parts else a.faces

def resized_vertex(face,v,height):
    # Base and section thicknesses stay fixed; only the pole length changes.
    return [v[0],v[1],v[2]+(height-3000 if face['s']=='head' or (face['s']=='post' and v[2]>360) else 0)]
