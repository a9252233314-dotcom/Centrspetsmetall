"""Blender 4.2/Cycles renders of the exact JSON mesh, full lamp + close-up.
blender -b --factory-startup --python tools/render_lamps_blender.py
"""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
MODELS=json.loads((ROOT/'lamps.json').read_text(encoding='utf-8'))
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
def aim(obj,point):obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()
def material(name,color,metallic=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=.5;return m
def scene_for(b):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.05;scene.cycles.max_bounces=5
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.75,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    iron=material('Coated casting',(.047,.074,.057),.25);steel=material('Coated steel',(.085,.10,.09),.3);light=material('Frosted diffuser',(.82,.86,.72))
    light.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.9,.93,.8,1);light.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.12
    mats={'iron':iron,'metal':steel,'light':light};data=json.loads((ROOT/f"assets/lamps/{b['id']}-geometry.json").read_text(encoding='utf-8'));parts={}
    for f in data['faces']:parts.setdefault(f['part'],[]).append(f)
    objects=[]
    for pid,faces in parts.items():
        vs=[];loops=[];lookup={}
        for f in faces:
            loop=[]
            for v in f['v']:
                key=tuple(round(t/1000,8) for t in v)
                if key not in lookup:lookup[key]=len(vs);vs.append(key)
                loop.append(lookup[key])
            loops.append(loop)
        mesh=bpy.data.meshes.new(f'Part-{pid}');mesh.from_pydata(vs,[],loops);mesh.update();obj=bpy.data.objects.new(f"{faces[0]['g']}-{pid}",mesh);scene.collection.objects.link(obj);obj.data.materials.append(mats[faces[0]['m']]);obj['group']=faces[0]['g'];obj['section']=faces[0]['s'];objects.append(obj)
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');obj.select_set(False)
    # Remove internal seams in continuous castings and the steel tube.
    for group in ['boot','flange','post','adapter','frame','arch','lower-rim']:
        members=[o for o in objects if o['group']==group]
        if len(members)<2:continue
        target=members[0];collection=bpy.data.collections.new(group+' operands');scene.collection.children.link(collection)
        for o in members[1:]:collection.objects.link(o)
        modifier=target.modifiers.new('Continuous component','BOOLEAN');modifier.operation='UNION';modifier.solver='EXACT';modifier.operand_type='COLLECTION';modifier.collection=collection;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=modifier.name)
        for o in members[1:]:objects.remove(o);bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(collection)
    for o in objects:
        bevel=o.modifiers.new('Edge highlights','BEVEL');bevel.width=.0009;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.45;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    floor=material('Studio floor',(.74,.76,.70));bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));bpy.context.object.data.materials.append(floor);plane=bpy.context.object
    lights=[]
    for name,loc,power,size in [('Key',(-3,-4,5),650,4),('Fill',(3,-1,3),380,3),('Rim',(1,4,4),550,3)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=loc;aim(obj,(0,0,1.5));lights.append(obj)
    cam_data=bpy.data.cameras.new('Camera');cam_data.type='ORTHO';cam=bpy.data.objects.new('Camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam
    return scene,objects,plane,lights
folder=ROOT.parent/'csm-lamp-renders';folder.mkdir(exist_ok=True)
for b in MODELS:
    if selected and b['id'] not in selected:continue
    scene,objects,floor,lights=scene_for(b);cam=scene.camera;scene.render.resolution_x=1000;scene.render.resolution_y=1400;cam.data.ortho_scale=3.55;cam.location=(4.8,-7,3.7);aim(cam,(.1 if b['id']=='vault' else 0,0,1.5));scene.render.filepath=str(folder/f"{b['id']}-render.png");bpy.ops.render.render(write_still=True)
    for o in objects:o.hide_render=o['section']!='head'
    floor.hide_render=True;vs=[v.co for o in objects if o['section']=='head' for v in o.data.vertices];center=Vector(tuple((min(v[i] for v in vs)+max(v[i] for v in vs))/2 for i in range(3)));span=max(max(v[i] for v in vs)-min(v[i] for v in vs) for i in range(3));scene.render.resolution_x=1400;scene.render.resolution_y=1050;cam.data.ortho_scale=span*1.65;cam.location=center+Vector((2,-3,1.2));aim(cam,center)
    scene.render.filepath=str(folder/f"{b['id']}-head-render.png");bpy.ops.render.render(write_still=True)
    sha=hashlib.sha256((ROOT/f"assets/lamps/{b['id']}-geometry.json").read_bytes()).hexdigest();(folder/f"{b['id']}-render.json").write_text(json.dumps({'geometry_sha256':sha,'renderer':'Blender '+bpy.app.version_string+' Cycles','samples':32}),encoding='utf-8')
    for o in objects:o.hide_render=False
    floor.hide_render=False;bpy.ops.wm.save_as_mainfile(filepath=str(folder/f"{b['id']}.blend"));print('LAMP_RENDER_COMPLETE',b['id'],flush=True)
