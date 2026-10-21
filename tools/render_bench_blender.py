"""Blender 4.2, deterministic Cycles studio renders from the exact catalog mesh.

blender -b --factory-startup --python tools/render_bench_blender.py -- line
No geometry is inferred from photos. Run build_site.py before this script.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
MODELS=json.loads((ROOT/'benches.json').read_text(encoding='utf-8'))
requested=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []

def material(name,color,roughness,metallic=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    tree=m.node_tree;bsdf=tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*color,1)
    bsdf.inputs['Roughness'].default_value=roughness;bsdf.inputs['Metallic'].default_value=metallic
    return m

def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def make_scene(b):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32
    scene.cycles.use_denoising=True;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.045
    scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
    scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.81,.75,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    iron=material('Powder-coated cast iron',(.047,.074,.057),.58,.25)
    tree=iron.node_tree;noise=tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=170;noise.inputs['Detail'].default_value=2
    bump=tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00025;tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);tree.links.new(bump.outputs['Normal'],tree.nodes['Principled BSDF'].inputs['Normal'])
    wood=material('Oiled timber',(.32,.135,.045),.43)
    tree=wood.node_tree;tex=tree.nodes.new('ShaderNodeTexCoord');mapping=tree.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,100,100)
    tree.links.new(tex.outputs['Generated'],mapping.inputs[0]);noise=tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7;tree.links.new(mapping.outputs['Vector'],noise.inputs['Vector'])
    ramp=tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.19,.072,.025,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.45,.23,.085,1);tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);tree.links.new(ramp.outputs['Color'],tree.nodes['Principled BSDF'].inputs['Base Color'])
    bump=tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0002;tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);tree.links.new(bump.outputs['Normal'],tree.nodes['Principled BSDF'].inputs['Normal'])
    steel=material('Fasteners',(.36,.39,.35),.3,.7);mats={'iron':iron,'wood':wood,'metal':steel}
    data=json.loads((ROOT/'assets/benches'/f"{b['id']}-geometry.json").read_text(encoding='utf-8'));parts={}
    for face in data['faces']:parts.setdefault(face['part'],[]).append(face)
    objects=[]
    for pid,faces in parts.items():
        verts=[];polygons=[];lookup={}
        for face in faces:
            indices=[]
            for v in face['v']:
                key=tuple(round(t/1000,8) for t in v)
                if key not in lookup:lookup[key]=len(verts);verts.append(key)
                indices.append(lookup[key])
            polygons.append(indices)
        mesh=bpy.data.meshes.new(f'Part-{pid}');mesh.from_pydata(verts,[],polygons);mesh.update()
        obj=bpy.data.objects.new(f"{faces[0]['g']}-{pid}",mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mats[faces[0]['m']]);obj['part_group']=faces[0]['g'];obj['part_material']=faces[0]['m']
        bpy.context.view_layer.objects.active=obj;obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');obj.select_set(False)
        objects.append(obj)
    # A cast side is a union, not a set of visibly intersecting bars.
    for group in ('support-left','support-right'):
        members=[o for o in objects if o.get('part_group')==group]
        target=members[0];collection=bpy.data.collections.new('Boolean operands '+group);scene.collection.children.link(collection)
        for o in members[1:]:collection.objects.link(o)
        modifier=target.modifiers.new('Continuous casting','BOOLEAN');modifier.operation='UNION';modifier.solver='EXACT';modifier.operand_type='COLLECTION';modifier.collection=collection
        bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=modifier.name)
        for o in members[1:]:objects.remove(o);bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(collection)
    for obj in objects:
        bevel=obj.modifiers.new('Edge highlights','BEVEL');bevel.width=.001 if obj['part_material']=='wood' else .0006;bevel.segments=3
        bevel.limit_method='ANGLE';bevel.angle_limit=.45
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    floor=material('Warm studio floor',(.74,.76,.70),.85)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));bpy.context.object.data.materials.append(floor)
    for name,location,power,size in [('Key',(-2.2,-3,4.5),450,3),('Fill',(2.5,-1,2.8),230,2.5),('Rim',(.5,3,3.5),380,2)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.shape='DISK';light.size=size;obj=bpy.data.objects.new(name,light);bpy.context.collection.objects.link(obj);obj.location=location;aim(obj,(0,0,.4))
    camera=bpy.data.cameras.new('Camera');camera.type='ORTHO';camera.ortho_scale=2.45;cam=bpy.data.objects.new('Camera',camera);bpy.context.collection.objects.link(cam);cam.location=(2.5,-3.7,2.2);aim(cam,(0,0,b['height']/2000));scene.camera=cam
    return scene,objects

for b in MODELS:
    if requested and b['id'] not in requested:continue
    scene,objects=make_scene(b)
    # Keep lossless masters outside the published site.
    folder=ROOT.parent/'csm-bench-renders';folder.mkdir(exist_ok=True)
    scene.render.filepath=str(folder/f"{b['id']}-render.png");bpy.ops.render.render(write_still=True)
    geometry=ROOT/'assets/benches'/f"{b['id']}-geometry.json"
    (folder/f"{b['id']}-render.json").write_text(json.dumps({'geometry_sha256':hashlib.sha256(geometry.read_bytes()).hexdigest(),'renderer':'Blender '+bpy.app.version_string+' Cycles','samples':scene.cycles.samples}),encoding='utf-8')
    # Save the complete scene for reproducible future edits.
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/f"{b['id']}.blend"))
    print('RENDER_COMPLETE',b['id'],flush=True)
