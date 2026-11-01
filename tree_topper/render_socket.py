import trimesh, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
m=trimesh.load("flake_socket.stl"); print("watertight",m.is_watertight,m.bounds.tolist())

def shaded(ax,mesh,color,light=(0.4,-0.5,0.8),alpha=1):
    tri=mesh.vertices[mesh.faces]; n=mesh.face_normals
    l=np.array(light)/np.linalg.norm(light); s=0.35+0.65*np.clip(n@l,0,1)
    c=np.array(color)[None,:]*s[:,None]; c=np.clip(c,0,1)
    pc=Poly3DCollection(tri,facecolors=np.c_[c,np.full(len(c),alpha)],linewidths=0); ax.add_collection3d(pc)

def box(c,s):
    return trimesh.creation.box(extents=s,transform=trimesh.transformations.translation_matrix(c))

def flake(R=114.5,t=10):
    # simple 6-arm flat flake, bottom arm is a 10x10 bar dropping into the socket
    parts=[]
    for k in range(6):
        a=np.deg2rad(90+60*k)
        d=np.array([np.cos(a),0,np.sin(a)])
        arm=trimesh.creation.box(extents=[R,t,10]); 
        arm.apply_translation([R/2,0,0])
        rot=trimesh.transformations.rotation_matrix(a,[0,1,0]*np.array([0,-1,0])+0) if False else trimesh.transformations.rotation_matrix(-a,[0,1,0])
        arm.apply_transform(rot); parts.append(arm)
        for f,L in ((0.55,38),(0.78,26)):
            for sgn in (-1,1):
                br=trimesh.creation.box(extents=[L,t,8]); br.apply_translation([L/2,0,0])
                br.apply_transform(trimesh.transformations.rotation_matrix(-(a+sgn*np.deg2rad(55)),[0,1,0]))
                br.apply_translation(d*R*f); parts.append(br)
    return trimesh.util.concatenate(parts)

fig=plt.figure(figsize=(15,7))
# 1) isolated socket, two views
for i,(el,az) in enumerate([(18,35),(55,200)]):
    ax=fig.add_subplot(1,3,i+1,projection="3d"); shaded(ax,m,(0.30,0.55,0.85))
    b=m.bounds; ctr=b.mean(0); r=60
    ax.set_xlim(ctr[0]-r,ctr[0]+r);ax.set_ylim(ctr[1]-r,ctr[1]+r);ax.set_zlim(0,2*r); ax.set_box_aspect((1,1,1))
    ax.view_init(el,az); ax.set_axis_off(); ax.set_title(["Socket (side)","Socket (top: slot + funnel)"][i])
# 3) cross-section
ax=fig.add_subplot(1,3,3)
from shapely.geometry import Polygon
sec=m.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
shape=Polygon()
for loop in sec.discrete:
    shape=shape.symmetric_difference(Polygon(loop[:,[0,2]]))
geoms=[shape] if shape.geom_type=="Polygon" else list(shape.geoms)
for g in geoms:
    xs,ys=g.exterior.xy; ax.fill(xs,ys,color="#4d8ad9")
    for h in g.interiors:
        x,y=h.xy; ax.fill(x,y,color="white")
ax.set_aspect("equal"); ax.set_title("Cross-section: rod bore below, arm slot above"); ax.axis("off")
plt.tight_layout(); plt.savefig("socket_views.png",dpi=90); plt.close()

# assembly picture
fig=plt.figure(figsize=(12,8))
ax=fig.add_subplot(111,projection="3d")
sock=m.copy()
shaded(ax,sock,(0.30,0.55,0.85))
rod=trimesh.creation.cylinder(radius=6.35,height=140,sections=32); rod.apply_translation([0,0,-70+40])
shaded(ax,rod,(0.55,0.55,0.58))
fl=flake(); 
# flake lowest arm tip sits in slot: bottom arm points down (-z); tip at z=H-50
pass
fl.apply_translation([0,0,105-50+114.5])
shaded(ax,fl,(0.92,0.96,1.0),light=(0.2,-0.8,0.6))
ax.set_xlim(-130,130);ax.set_ylim(-130,130);ax.set_zlim(-20,300);ax.set_box_aspect((1,1,1.25))
ax.view_init(6,-90); ax.set_axis_off(); ax.set_title("Assembly sketch: 9\" flake dropped into socket on a 1/2\" rod (flake shape is a stand-in)")
plt.savefig("socket_assembly.png",dpi=80); plt.close()
