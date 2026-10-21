'use strict';
// A depth buffer keeps the same model correctly occluded at every viewing angle.
window.createBenchRenderer=function(canvas){
 const gl=canvas.getContext('webgl',{antialias:true,alpha:true,preserveDrawingBuffer:true});if(!gl)return null;
 const vertex=`attribute vec3 p;attribute vec3 n;attribute vec3 w;attribute float m;varying vec3 normal;varying vec3 world;varying float mat;void main(){gl_Position=vec4(p,1.0);normal=n;world=w;mat=m;}`;
 const fragment=`precision mediump float;varying vec3 normal;varying vec3 world;varying float mat;uniform vec3 iron;uniform vec3 eye;
 float grain(vec3 p){return sin(p.y*.12+sin(p.x*.006)*.7+sin(p.z*.08)*.4)*.5+.5;}
 void main(){vec3 n=normalize(normal);vec3 base=iron;float rough=.6;if(mat<.5){float g=grain(world);base=mix(vec3(.53,.30,.14),vec3(.67,.43,.23),g*.5+.2);rough=.55;}else if(mat>1.5){base=vec3(.5,.54,.5);rough=.32;}
 vec3 l=normalize(vec3(-.35,-.6,.9));vec3 fill=normalize(vec3(.75,.2,.5));float diffuse=.56+.55*max(dot(n,l),0.0)+.18*max(dot(n,fill),0.0);float spec=pow(max(dot(n,normalize(l+eye)),0.0),mix(100.0,18.0,rough))*.15;vec3 result=base*diffuse+vec3(spec);gl_FragColor=vec4(result,1.0);}`;
 function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
 const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))return null;gl.useProgram(program);
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);for(const [name,count,offset] of [['p',3,0],['n',3,3],['w',3,6],['m',1,9]]){const at=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(at);gl.vertexAttribPointer(at,count,gl.FLOAT,false,40,offset*4);}
 gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.clearColor(0,0,0,0);
 return {draw(faces,project,scale,cx,cy,color,yaw,pitch){
  const centers=new Map();for(const f of faces){if(!centers.has(f.part))centers.set(f.part,[]);centers.get(f.part).push(...f.v);}
  for(const [id,vs] of centers){centers.set(id,[0,1,2].map(i=>vs.reduce((s,v)=>s+v[i],0)/vs.length));}
  const data=[];
  for(const f of faces){const a=f.v[0],b=f.v[1],c=f.v[2],u=b.map((v,i)=>v-a[i]),v=c.map((t,i)=>t-a[i]);let n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];const size=Math.hypot(...n)||1;n=n.map(t=>t/size);const center=centers.get(f.part),fc=[0,1,2].map(i=>f.v.reduce((s,t)=>s+t[i],0)/f.v.length);if(n.reduce((s,t,i)=>s+t*(fc[i]-center[i]),0)<0)n=n.map(t=>-t);const mat=f.m==='wood'?0:f.m==='iron'?1:2;
   for(let i=1;i<f.v.length-1;i++)for(const p of [f.v[0],f.v[i],f.v[i+1]]){const q=project(p);data.push((q[0]*scale+cx)/600-1,1-(q[1]*scale+cy)/450,-q[2]/4000,...n,...p,mat);}
  }
  gl.viewport(0,0,canvas.width,canvas.height);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniform3fv(gl.getUniformLocation(program,'iron'),[1,3,5].map(i=>parseInt(color.slice(i,i+2),16)/255));gl.uniform3fv(gl.getUniformLocation(program,'eye'),[-Math.sin(yaw)*Math.cos(pitch),-Math.cos(yaw)*Math.cos(pitch),Math.sin(pitch)]);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.DYNAMIC_DRAW);gl.drawArrays(gl.TRIANGLES,0,data.length/10);
 }};
};
