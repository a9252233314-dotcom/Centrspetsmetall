"""Check convex casting contacts, seating and pockets; not a load assessment."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hatch_catalog import HATCHES
from hatch_geometry import mesh,clip,rect
from check_lamp_geometry import prepare,touches
def bounds(parts):return [(min(v[i] for p in parts for v in p['v']),max(v[i] for p in parts for v in p['v'])) for i in range(3)]
def check():
    report=[]
    for b in HATCHES:
        for d in [500,600,700]:
            for count in ([12,18,24] if b.get('rayCount') else [0]):
                parts=[prepare(p) for p in mesh(b,d,count or None,True)]
                frame=[p for p in parts if p['s']=='frame'];lid=[p for p in parts if p['s']=='lid'];skin=[p for p in lid if p['g']=='lid-skin'];body=next(p for p in lid if p['g']=='lid-body');seat=[p for p in frame if p['g']=='frame-seat']
                assert all(touches(p,body) for p in skin),(b['id'],'Detached skin')
                ribs=[p for p in lid if p['g']=='lid-ribs'];assert all(touches(p,body) for p in ribs),(b['id'],'Detached underside rib')
                relief=[p for p in lid if p['g'] not in ['lid-body','lid-skin','lid-ribs']]
                assert relief and all(any(touches(p,s) for s in skin) for p in relief),(b['id'],'Suspended relief')
                assert all(touches(p,body) for p in seat),(b['id'],'Lid not supported around perimeter')
                # The three continuous frame levels meet on coplanar surfaces.
                flange=[p for p in frame if p['g']=='frame-flange'];wall=[p for p in frame if p['g']=='frame-wall']
                assert all(any(touches(p,q) for q in flange) for p in seat+wall),(b['id'],'Detached frame component')
                # All lower ribs remain inside the free opening below the seat.
                for p in ribs:
                    for x,y,z in p['v']:
                        assert max(abs(x),abs(y))<d/2 if b['shape']=='square' else math.hypot(x,y)<d/2
                for p in lid:
                    for x,y,z in p['v']:
                        assert max(abs(x),abs(y))<=d/2+30+1e-6 if b['shape']=='square' else math.hypot(x,y)<=d/2+30+1e-6
                # Recesses are real openings in the upper skin and the relief,
                # with a closed bottom at z=76 in the lower disk/slab.
                pos=(d/2+30)*.62
                for center in [-pos,pos]:
                    pocket=rect(center-19.9,center+19.9,-8.9,8.9)
                    for p in skin+relief:
                        lo=min(v[2] for v in p['v']);poly=[(x,y) for x,y,z in p['v'] if abs(z-lo)<1e-6]
                        assert not clip(poly,pocket),(b['id'],'Blocked pocket',p['g'])
                if count:assert len({p['g'] for p in relief if p['g'].startswith('ray-')})==count
                bb=bounds(parts);assert [round(hi-lo) for lo,hi in bb]==[d+200,d+200,90]
                report.append({'model':b['id'],'opening':d,'rays':count,'solids':len(parts),'seated':True,'relief_attached':True,'pockets_open':True,'frame_height':90})
    return report
if __name__=='__main__':print(json.dumps(check()))
