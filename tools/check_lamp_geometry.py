"""Convex-polyhedron SAT: contact and dimensions, not a structural calculation."""
from pathlib import Path
import sys,math,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lamp_catalog import LAMPS
from lamp_geometry import mesh,resized_vertex
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(v):
    n=math.sqrt(dot(v,v))
    if n<1e-9:return None
    v=tuple(x/n for x in v)
    if next((x for x in v if abs(x)>1e-8),1)<0:v=tuple(-x for x in v)
    return tuple(round(x,8) for x in v)
def prepare(p):
    p=dict(p);vs=p['v'];p['bounds']=[(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)];edges=set();normals=set()
    for loop in p['loops']:
        pts=[vs[i] for i in loop];n=unit(cross(sub(pts[1],pts[0]),sub(pts[2],pts[0])))
        if n:normals.add(n)
        for a,b in zip(pts,pts[1:]+pts[:1]):
            d=unit(sub(b,a))
            if d:edges.add(d)
    p['edges']=edges;p['normals']=normals;return p
def touches(a,b):
    if any(max(a['bounds'][i][0],b['bounds'][i][0])>min(a['bounds'][i][1],b['bounds'][i][1])+1e-5 for i in range(3)):return False
    axes=a['normals']|b['normals']|{n for x in a['edges'] for y in b['edges'] if (n:=unit(cross(x,y)))}
    for n in axes:
        aa=[dot(v,n) for v in a['v']];bb=[dot(v,n) for v in b['v']]
        if max(min(aa),min(bb))>min(max(aa),max(bb))+1e-5:return False
    return True
def check():
    reports=[]
    for model in LAMPS:
        for h in [2400,3000,3600]:
            for count in ([12,16,20] if model.get('finCount') else [None]):
                parts=[prepare(p) for p in mesh(model,h,count,True)];links={p['id']:set() for p in parts}
                for i,p in enumerate(parts):
                    for q in parts[:i]:
                        if touches(p,q):links[p['id']].add(q['id']);links[q['id']].add(p['id'])
                seen={0};queue=[0]
                while queue:
                    i=queue.pop()
                    for j in links[i]-seen:seen.add(j);queue.append(j)
                assert len(seen)==len(parts),(model['id'],h,count,'Disconnected',set(p['g'] for p in parts if p['id'] not in seen))
                def neighbors(group):return {parts[n]['g'] for p in parts if p['g']==group for n in links[p['id']]}
                assert {'boot','post'}<=neighbors('flange'),(model['id'],'Base/pole connection')
                assert 'post' in neighbors('adapter'),(model['id'],'Adapter/pole connection')
                if count:
                    fins={p['g'] for p in parts if p['g'].startswith('fin-')};assert len(fins)==count
                    for group in fins:assert {'cap','lower-rim'}<=neighbors(group),(model['id'],group,'Fin attachment')
                faces=mesh(model,h,count);base=mesh(model,3000,count)
                for old,new in zip(base,faces):
                    for a,b in zip(old['v'],new['v']):assert all(abs(x-y)<1e-6 for x,y in zip(resized_vertex(old,a,h),b)),(model['id'],'Browser height mismatch')
                vs=[v for p in parts for v in p['v']];bounds=[round(max(v[i] for v in vs)-min(v[i] for v in vs)) for i in range(3)]
                assert bounds[2]==h,(model['id'],bounds)
                # Hollow structural post and separate decorative boot remain distinct.
                assert all(math.hypot(v[0],v[1])>=37-1e-6 for p in parts if p['g']=='post' for v in p['v'])
                reports.append({'model':model['id'],'height':h,'fins':count,'solids':len(parts),'connected':True,'bounds':bounds})
    return reports
if __name__=='__main__':print(json.dumps(check()))
