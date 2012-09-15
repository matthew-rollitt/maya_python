import maya.cmds as cmds
import math, sys
import random as r

def deleteAllObjects():
    cmds.select(all=True)
    cmds.delete()

deleteAllObjects()

def makeSphere(radius=1.0):
    result = cmds.polySphere(r=radius)
    return result[0]

def makeCube(size=1.0):
    result = cmds.polyCube(w=size, h=size, d=size)
    return result[0]

# copy  make copies (or instances) of a shape
def makeCopy(node):
    copy = cmds.duplicate(node)
    return copy[0]

def placeCube(x,y,z):
    shape = makeCube(1)
    translate(shape, x,y,z);

# transform functinos 
def translate(shape, x, y, z, relative=True):
    cmds.move(x, y, z, shape, r=relative)

def rotate(shape, x, y, z, relative=True):
    cmds.rotate(x, y, z, shape, r=relative)

def scale(shape, x, y, z, relative=True):
    cmds.scale(x, y, z, shape, r=relative)

# ways of placing the copies
def makeRow(shape, n, dx, dy, dz):
    for i in range(n):
        translate(makeCopy(shape), dx*i, dy*i, dz*i)

# bevel objects
def bevel(shape):
    cmds.polyBevel(shape, oaf=True)
    return shape

def makeBrick():
    result = cmds.polyCube(w=2, h=1, d=4)
    shape = result[0]
    bevel(shape)
    return shape

# parent = (child to , parent)
def parent(child, node, r=False):
    cmds.parent(child, node, r=r)
    return child

# make Group of objects 
def makeGroup(name, nodes=[]):
    group = cmds.group(em=True, n=name)
    for node in nodes:
        parent(node, group)
    return group

# rewrite makeRow to return a group
def makeRow(shape, n, dx, dy, dz):
    shapes = []
    for i in range(n):
        copy = makeCopy(shape)
        translate(copy, dx*i, dy*i, dz*i)
        shapes.append(copy)
    return makeGroup('row', shapes)



# we can directly generate 3D distributions
def make3DGrid(shape, nx, ny, nz, dx, dy, dz):
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                translate(makeCopy(shape), dx*ix, dy*iy, dz*iz)



# set pivot of shape
def setPivot(shape, x, y, z):
    cmds.xform(shape, ws=True, piv=(x,y,z))

"""
///////////////////
random distributions
///////////////////
"""

# we can distribute shapes randomly, in a controlled way
def uniformRandom(lo, hi):
    return random.uniform(lo, hi)

def placeRandomlyUniform(shape, n, dx, dy, dz):
    for i in range(n):
        x = uniformRandom(-dx, dx)
        y = uniformRandom(-dy, dy)
        z = uniformRandom(-dz, dz)
        translate(makeCopy(shape), x, y, z)

def gaussianRandom(lo, hi):
    def gaussian():
        return (random.gauss(0.0, 1.0)/4.0)/2.0 + 0.5
    return lo + gaussian()*(hi-lo)

def placeRandomlyGaussian(shape, n, dx, dy, dz):
    for i in range(n):
        x = gaussianRandom(-dx, dx)
        y = gaussianRandom(-dy, dy)
        z = gaussianRandom(-dz, dz)
        translate(makeCopy(shape), x, y, z)

def placeRandomly(shape, n, dx, dy, dz, randomizer=uniformRandom):
    for i in range(n):
        x = randomizer(-dx, dx)
        y = randomizer(-dy, dy)
        z = randomizer(-dz, dz)
        translate(makeCopy(shape), x, y, z)

# random types 
def placeRandomlyUniform(shape, n, dx, dy, dz):
    placeRandomly(shape, n, dx, dy, dz, randomizer=uniformRandom)

def placeRandomlyGaussian(shape, n, dx, dy, dz):
    placeRandomly(shape, n, dx, dy, dz, randomizer=gaussianRandom)

def placeRandomly(shape, n, dx, dy, dz, randomizer=uniformRandom):
    for i in range(n):
        translate(makeCopy(shape),
                  randomizer(-dx, dx),
                  randomizer(-dy, dy),
                  randomizer(-dz, dz))


# another technique we can use is sweeping (extrusion) along paths (curves)
def makeCircle(radius=1.0, normal=(0,1,0)):
    result = cmds.circle(r=radius, nr=normal)
    return result[0]

def makeSweep(profile, path, scale=1.0, hideCurves=False):
    result = cmds.extrude(profile, path, et=2, upn=True, ucp=True, fpt=True, sc=scale)
    if (hideCurves):
        cmds.hide(profile)
        cmds.hide(path)
    return result[0]
""""
////////////////////
Extrude along a path
//////////////////// 

""""
# run: test makeSweep <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#profile = makeCircle()
#path = makeCircle(radius=3)
#donut = makeSweep(profile, path)

# run: add scale to makeSweep <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#profile = makeCircle()
#path = makeCircle(radius=3)
#horn = makeSweep(path, profile, scale=0)

# we can generate procedural curves
def makeCurve(deg, points):
    return cmds.curve(d=deg, p=points)

def makeWigglyCurve(np, radius, height):
    points = []
    p = (0, 0, 0)
    dy = height / (np-1)
    for i in range(np):
        points.append(p)
        p = (gaussianRandom(-radius, radius), dy*(i+1), gaussianRandom(-radius, radius))
    return makeCurve(3, points)

def children(node):
    return cmds.listRelatives(node, pa=True, typ='transform')

def allShapes(node):
    return cmds.listRelatives(node, pa=True, ad=True, typ='shape')

def nodeShape(node):
    result = cmds.listRelatives(node, pa=True, s=True)
    return result[0]

def turbulentDistribution(shape, n, levels, dx, dy, dz, randomizer=uniformRandom):
    if (levels == 0):
        return
    else:
        placeRandomly(shape, n, dx, dy, dz, randomizer=randomizer)
        scale(shape, .5, .5, .5)
        turbulentDistribution(shape, n*2, levels-1, dx+1, dy+1, dz+1)



# height fields
def makeHeightField(shape, mx , my ,mz ,nx, nz, dx, dz, ex, ez, sy, heightFunc):
    sx = (nx-1.0)*dx
    sz = (nz-1.0)*dz
    for ix in range(nx):
        for iz in range(nz):
            x = dx*ix - sx/2.0
            z = dz*iz - sz/2.0
            y = heightFunc(x/sx, z/sz, ex, ez, sy)
            translate(makeCopy(shape), x+ mx, y+my , z+mz)
    cmds.hide(shape)

def sineXPlusZ(x, z, ex, ez, sy):
    return((math.sin(math.radians(x*ex)) + math.sin(math.radians(z*ez))) * sy)


  
def DeprecatedCreateCurve3D(x1,y1,z1,x2,y2,z2, divide):
    arr = []
    size = 1/divide
    print size
    for i in range(0,size):
        dotx = x1*i+((x2*i-x1*i) *divide) + x1
        doty = y1*i+((y2*i-y1*i) *divide) + y1
        dotz = z1*i+((z2*i-z1*i) *divide) + z1
        dot = [dotx, doty, dotz]       
        print dot
        arr.append(dot)
        
    return arr


def lerp3D(x1, y1, z1, x2, y2, z2, increments):
    arr = []    
    for i in range(increments + 1):
        frac = i / float(increments)
        
        dotx = x1 + (x2 - x1) * frac
        doty = y1 + (y2 - y1) * frac
        dotz = z1 + (z2 - z1) * frac

        arr.append([dotx, doty, dotz])
    return arr    
#arr = createCurve3D(0,0,0,10,10,10,.2)

def makeSweep(profile, path, scale=1.0, hideCurves=True):
    result = cmds.extrude(profile, path, et=2, upn=True, ucp=True, fpt=True, sc=scale)
    if (hideCurves):
        cmds.hide(profile)
        cmds.hide(path)
    return result[0]



class shape:
    def __init__(self, x1, y1,  x2, y2):
        self.x1 = x1
        self.y1 = y1   
        self.x2 = x2
        self.y2 = y2   


def sinc(x, z, ex, ez, sy):
    x0 = math.radians(x*ex)
    z0 = math.radians(z*ez)
    r = math.sqrt(x0*x0+z0*z0)*4
    if (r == 0):
        r = 0.001
    return((math.sin(r)/r)*sy)
    
def foot(fx,fy,fz, mx,my,mz ,endx, endy, endz ):
    for i in range(40):
        randX = r.random()*20 - 10
        randZ = r.random()*20 - 10
        randY = r.random()*10 - 5
        
        lerpArr = lerp3D(fx + randX ,fy,fz +randZ, endx + randX/4, endy + randX/4, endz +randZ/4  ,4)
        lerpArr[len(lerpArr)/2] = [mx + randZ, my +randX -randZ , mz+randX ]
        path = cmds.curve(p=lerpArr)
        profile = makeCircle(r.random()/4)
        makeSweep(profile,path)
        
         
    makeHeightField(makeCube(), fx,fy,fz,40, 40, 0.5, 0.5, 1600, 1200, 20, sinc)


foot(30,0,30,10,16,0,10,20,0)
foot(-30,0,30,-15,16, 0,-10,20,0)

foot(30,0,-30,10,16,0,0,20,0)
foot(-30,0,-30,-15,16, 0,-10,20,0)
