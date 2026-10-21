"""Original procedural profiles, using no supplier geometry or traced outlines."""
import math

class Assembly:
    def __init__(self):self.faces=[];self.parts=[];self.group='seat';self.anchor=None
    def prism(self,profile,x1,x2,material='iron'):
        pid=len(self.parts)
        part={'id':pid,'g':self.group,'x':[x1,x2],'profile':profile,'m':material}
        self.parts.append(part)
        a=[[x1,y,z] for y,z in profile];b=[[x2,y,z] for y,z in profile]
        loops=[a[::-1],b]+[[a[i],a[(i+1)%len(a)],b[(i+1)%len(a)],b[i]] for i in range(len(a))]
        for loop in loops:
            face={'v':loop,'m':material,'g':self.group,'part':pid}
            if self.anchor is not None:face['a']=self.anchor;part['a']=self.anchor
            self.faces.append(face)
    def box(self,x1,x2,y1,y2,z1,z2,material='iron'):
        r=min(4,(z2-z1)/5,(y2-y1)/5)
        self.prism([(y1+r,z1),(y2-r,z1),(y2,z1+r),(y2,z2-r),(y2-r,z2),(y1+r,z2),(y1,z2-r),(y1,z1+r)],x1,x2,material)
    def band(self,x1,x2,points,width=38):
        # Adjacent spans share the same cross-section, forming one continuous
        # casting without gaps on the outer radius of a curved branch.
        sections=[]
        for i,p in enumerate(points):
            prev=points[max(0,i-1)];nxt=points[min(len(points)-1,i+1)]
            dy=nxt[0]-prev[0];dz=nxt[1]-prev[1];length=math.hypot(dy,dz)
            w=width(i/(len(points)-1)) if callable(width) else width
            py=-dz/length*w/2;pz=dy/length*w/2
            sections.append(((p[0]+py,p[1]+pz),(p[0]-py,p[1]-pz)))
        for (p1,p2),(q1,q2) in zip(sections,sections[1:]):
            self.prism([p1,q1,q2,p2],x1,x2)

def bezier(p0,p1,p2,p3,n=24):
    return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in (0,1)) for t in [i/n for i in range(n+1)]]

def tie_and_plates(a,center):
    a.group='tiebar';end=center-28
    for y1,y2,z1,z2 in [(-20,20,370,372),(-20,20,408,410),(-20,-18,372,408),(18,20,372,408)]:a.box(-end,end,y1,y2,z1,z2)
    for sign in (-1,1):
        a.group='plate-left' if sign<0 else 'plate-right';x=sign*center
        a.box(*sorted([x-sign*28,x-sign*22]),-55,55,366,414)
        a.group='fastener-left' if sign<0 else 'fastener-right'
        for y in (-35,35):
            for d1,d2,r,n in [(-38,-30,7.5,6),(-30,-28,9,16),(22,24,9,16),(24,32,7.5,6)]:
                a.prism([(y+r*math.cos(i*math.tau/n),398+r*math.sin(i*math.tau/n)) for i in range(n)],*sorted([x+sign*d1,x+sign*d2]),'metal')

def modern_mesh(b,length=1800,return_parts=False,rib_count=None):
    a=Assembly();center=length/2-250;ribbed=b['id']=='rhythm';flow=b['id']=='flow'
    if not ribbed:
        for i in range(5):
            y=-224+92*i;a.box(-length/2,length/2,y,y+80,418,450,'wood')
    for x in (-center,center):
        a.group='support-left' if x<0 else 'support-right';x1=x-22;x2=x+22
        if flow:
            a.box(x1-10,x2+10,-300,-185,0,20);a.box(x1-10,x2+10,235,350,0,20)
            a.band(x1,x2,bezier((-245,18),(-255,200),(-80,185),(-170,398)),lambda t:34+12*math.sin(math.pi*t)**2)
            a.band(x1,x2,bezier((295,18),(280,180),(80,300),(170,398)),lambda t:34+12*math.sin(math.pi*t)**2)
            a.box(x1,x2,-225,290,378,418)
            a.prism([(240,399),(276,399),(350,820),(314,820)],x1,x2)
        else:
            a.box(x1-10,x2+10,-250,-135,0,20);a.box(x1-10,x2+10,135,250,0,20)
            ztop=330 if ribbed else 398
            points=[(210*math.sin(t),18+(ztop-18)*math.cos(t)) for t in [-math.pi/2+i*math.pi/36 for i in range(37)]]
            a.band(x1,x2,points,32)
            a.box(x1,x2,-225,225,ztop-20,ztop+20)
    if flow:
        a.group='back';slope=74/421
        for i in range(4):
            z=490+80*i;y=240+(z-399)*slope
            a.prism([(y-32,z),(y,z),(y+slope*55,z+55),(y-32+slope*55,z+55)],-length/2,length/2,'wood')
    if not ribbed:tie_and_plates(a,center)
    else:
        # Timber ribs rest on two longitudinal steel bearers; these bear on
        # both cast crossheads. There are no suspended slats or cosmetic tubes.
        for cy,name in [(-145,'bearer-front'),(145,'bearer-rear')]:
            a.group=name
            for y1,y2,z1,z2 in [(cy-20,cy+20,350,352),(cy-20,cy+20,388,390),(cy-20,cy-18,352,388),(cy+18,cy+20,352,388)]:a.box(-length/2+20,length/2-20,y1,y2,z1,z2)
        count=rib_count or b.get('ribCount',21)
        for i in range(count):
            t=i/(count-1);cx=(t-.5)*(length-36);half=210+40*(2*t-1)**2;seat=450+20*math.sin(math.pi*(t-.5))**2
            a.group=f'rib-{i}';a.anchor=cx
            for k in range(12):
                y1=-half+2*half*k/12;y2=-half+2*half*(k+1)/12
                z1=seat+10*(y1/half)**2;z2=seat+10*(y2/half)**2
                a.prism([(y1,390),(y2,390),(y2,z2),(y1,z1)],cx-18,cx+18,'wood')
        a.anchor=None
    return a.parts if return_parts else a.faces
