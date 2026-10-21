"""Validate assembly contact, not strength or manufacturing tolerances."""
from pathlib import Path
import sys,math,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bench_catalog import BENCHES,mesh

def touches(a,b,tolerance=1e-6):
    if max(a['x'][0],b['x'][0])>min(a['x'][1],b['x'][1])+tolerance:return False
    for polygon in (a['profile'],b['profile']):
        for i,p in enumerate(polygon):
            q=polygon[(i+1)%len(polygon)];n=(q[1]-p[1],p[0]-q[0]);length=math.hypot(*n)
            if length<1e-12:continue
            aa=[sum(v[j]*n[j] for j in range(2))/length for v in a['profile']]
            bb=[sum(v[j]*n[j] for j in range(2))/length for v in b['profile']]
            if max(min(aa),min(bb))>min(max(aa),max(bb))+tolerance:return False
    return True

def connected(parts):
    links={p['id']:set() for p in parts}
    for i,a in enumerate(parts):
        for b in parts[:i]:
            if touches(a,b):links[a['id']].add(b['id']);links[b['id']].add(a['id'])
    remaining=set(links);groups=[]
    while remaining:
        queue=[remaining.pop()];group=[]
        while queue:
            p=queue.pop();group.append(p)
            for n in links[p]&remaining:remaining.remove(n);queue.append(n)
        groups.append(group)
    return groups,links

def penetrates(a,b):
    # Strict convex-prism overlap. Surface contact is allowed, solid overlap isn't.
    if min(a['x'][1],b['x'][1])-max(a['x'][0],b['x'][0])<1e-5:return False
    for polygon in (a['profile'],b['profile']):
        for i,p in enumerate(polygon):
            q=polygon[(i+1)%len(polygon)];n=(q[1]-p[1],p[0]-q[0]);ln=math.hypot(*n)
            if ln<1e-12:continue
            aa=[sum(v[j]*n[j] for j in range(2))/ln for v in a['profile']];bb=[sum(v[j]*n[j] for j in range(2))/ln for v in b['profile']]
            if min(max(aa),max(bb))-max(min(aa),min(bb))<1e-5:return False
    return True

def check():
    report=[]
    for b in BENCHES:
        for length in (1500,1800,2000):
            parts=mesh(b,length=length,return_parts=True);groups,links=connected(parts)
            assert len(groups)==1,(b['id'],length,'Disconnected solids',[[parts[n]['g'] for n in g] for g in groups])
            for side in ('support-left','support-right'):
                support=[p for p in parts if p['g']==side]
                assert len(connected(support)[0])==1,(b['id'],side,'Disconnected casting')
            for part in parts:
                if part['m']=='wood':
                    touched={parts[n]['g'] for n in links[part['id']]}
                    assert {'support-left','support-right'}<=touched,(b['id'],part['id'],'Board lacks two supports',touched)
                    for other in parts:
                        if other['m']!='wood':assert not penetrates(part,other),(b['id'],part['id'],other['id'],'Iron penetrates timber',other['g'])
            for side in ('left','right'):
                plate=next(p for p in parts if p['g']=='plate-'+side)
                touched={parts[n]['g'] for n in links[plate['id']]}
                assert {'tiebar','support-'+side}<=touched,(b['id'],'Tie flange not mated',side,touched)
            faces=mesh(b,length=length);vs=[v for f in faces for v in f['v']]
            bounds=[round(max(v[i] for v in vs)-min(v[i] for v in vs)) for i in range(3)]
            assert bounds==[length,b['depth'],b['height']],(b['id'],bounds)
            report.append({'model':b['id'],'length':length,'solids':len(parts),'connected_components':len(groups),'both_flanges_mated':True,'all_boards_supported':True,'bounds':bounds})
    return report

if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False))
