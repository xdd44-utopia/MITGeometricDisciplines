from doctest import master
from utils import *
from Rhino.Geometry import NurbsSurface, Line, Polyline, Point3d, Vector3d
import rhinoscriptsyntax as rs
import scriptcontext as sc
from math import *

cuttingPos = [
    [
        [
            [1, 1, 1],
            [1, -1, 1],
            [1, -1, -1],
            [1, 1, -1]
        ],
        [
            [1, 1, 1],
            [-1, 1, 1],
            [-1, 1, -1],
            [1, 1, -1]
        ],
        [
            [1, 1, 1],
            [-1, 1, 1],
            [-1, -1, 1],
            [1, -1, 1]
        ]
    ],
    [
        [
            [-1, 1, 1],
            [-1, -1, 1],
            [-1, -1, -1],
            [-1, 1, -1]
        ],
        [
            [1, -1, 1],
            [-1, -1, 1],
            [-1, -1, -1],
            [1, -1, -1]
        ],
        [
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, -1],
            [1, -1, -1]
        ]
    ]
]

def x1(u, v):
    return cos(u) * sin(v) + (1 * cos(3 * u) + 5 * cos(5 * u)) / 24

def y1(u, v):
    return sin(u) * sin(v) + (1 * sin(3 * u) + 5 * sin(5 * u)) / 24

def z1(u, v):
    return cos(v)

def x2(u, v):
    u += v
    u = - u
    return cos(u) * sin(v) + cos(3 * u) / 4

def y2(u, v):
    u += v
    u = - u
    return sin(u) * sin(v) + sin(3 * u) / 4

def z2(u, v):
    return cos(v)

def x1(u, v):
    return cos(u) * sin(v) + cos(v * u)

def y1(u, v):
    return sin(u) * sin(v) + sin(v * u)

def z1(u, v):
    return cos(v)

def generate(x, y, z, ustep, ufreq, vstep, cuttingInterval, thickness, coneTopDist, direction):

    # direction 0: yz, 1: xz, 2: xy

    coneTop = Point3d(
        coneTopDist * offsetx if direction == 0 else 0,
        coneTopDist * offsetx if direction == 1 else 0,
        coneTopDist * offsetx if direction == 2 else 0
    )

    cuttingPlanes = []
    pieces = [[] for i in range(int(pi * 2 / ustep))]
    bounding = max(abs(x(0, pi / 2)), abs(x(pi / 2, pi / 2)), abs(y(0, pi / 2)), abs(y(pi / 2, pi / 2)))

    for v in frange(cuttingInterval, bounding * offsetx, cuttingInterval):

        px = v if direction == 0 else bounding * offsetx
        py = v if direction == 1 else bounding * offsety
        pz = v if direction == 2 else z(0, pi) * offsetz

        surface1 = NurbsSurface.CreateFromCorners(
            Point3d(
                cuttingPos[0][direction][0][0] * px,
                cuttingPos[0][direction][0][1] * py,
                cuttingPos[0][direction][0][2] * pz
            ),
            Point3d(
                cuttingPos[0][direction][1][0] * px,
                cuttingPos[0][direction][1][1] * py,
                cuttingPos[0][direction][1][2] * pz
            ),
            Point3d(
                cuttingPos[0][direction][2][0] * px,
                cuttingPos[0][direction][2][1] * py,
                cuttingPos[0][direction][2][2] * pz
            ),
            Point3d(
                cuttingPos[0][direction][3][0] * px,
                cuttingPos[0][direction][3][1] * py,
                cuttingPos[0][direction][3][2] * pz
            )
        )
        surface2 = NurbsSurface.CreateFromCorners(
            Point3d(
                cuttingPos[1][direction][0][0] * px,
                cuttingPos[1][direction][0][1] * py,
                cuttingPos[1][direction][0][2] * pz
            ),
            Point3d(
                cuttingPos[1][direction][1][0] * px,
                cuttingPos[1][direction][1][1] * py,
                cuttingPos[1][direction][1][2] * pz
            ),
            Point3d(
                cuttingPos[1][direction][2][0] * px,
                cuttingPos[1][direction][2][1] * py,
                cuttingPos[1][direction][2][2] * pz
            ),
            Point3d(
                cuttingPos[1][direction][3][0] * px,
                cuttingPos[1][direction][3][1] * py,
                cuttingPos[1][direction][3][2] * pz
            )
        )
        cuttingPlanes = [sc.doc.Objects.AddSurface(surface1)] + cuttingPlanes + [sc.doc.Objects.AddSurface(surface2)]
    
    intersects = [[] for i in range(len(cuttingPlanes))]
    results = []

    for i, u in enumerate(frange(0, pi * 2, ustep)):

        for j, v in enumerate(frange(0, pi, vstep)):

            if (v <= vfreq * 2 - vstep or v > pi - vfreq * 2 - vstep):
                continue
            
            uu = u + ustep
            vv = v + vstep

            uu = u + ustep
            vv = v + vstep
            surface = NurbsSurface.CreateFromCorners(
                Point3d(x(u, v) * offsetx, y(u, v) * offsety, z(u, v) * offsetz),
                Point3d(x(uu, v) * offsetx, y(uu, v) * offsety, z(uu, v) * offsetz),
                Point3d(x(uu, vv) * offsetx, y(uu, vv) * offsety, z(uu, vv) * offsetz),
                Point3d(x(u, vv) * offsetx, y(u, vv) * offsety, z(u, vv) * offsetz)
            )
            pieces[i].append(sc.doc.Objects.AddSurface(surface))

    def extendPos(base):
        # v = base - (1 if base[direction] > 0 else -1) * coneTop
        v = base + coneTop
        v = normalizeV(v)
        v = Point3d(v[0], v[1], v[2]) * thickness
        return base + v
    
    def mirrorPos(base, mirrorPlane):
        # mirrorPlane = 0 : yz, 1 : xz, 2 : xy
        # v = base - (1 if base[direction] > 0 else -1) * coneTop
        v = base + coneTop
        v = normalizeV(v)
        v = Point3d(v[0], v[1], v[2]) * thickness
        v[mirrorPlane] = - v[mirrorPlane]
        v = - v
        return base + v

    for k, cutting in enumerate(cuttingPlanes):
        result = []
        for j in range(len(pieces[i])):
            for i in range(len(pieces)):
                intersect = rs.IntersectBreps(cutting, pieces[i][j])
                if (intersect != None):
                    intersects[k].append(rs.coercecurve(intersect[0]))
                    sBase = intersects[k][-1].PointAtStart
                    sExtend = extendPos(sBase)
                    sMirror = mirrorPos(sBase, direction)
                    tBase = intersects[k][-1].PointAtEnd
                    tExtend = extendPos(tBase)
                    tMirror = mirrorPos(tBase, direction)
                    surface = NurbsSurface.CreateFromCorners(
                        sBase,
                        tBase,
                        tExtend,
                        sExtend
                    )
                    result.append(sc.doc.Objects.AddSurface(surface))
                    surface = NurbsSurface.CreateFromCorners(
                        sBase,
                        tBase,
                        tMirror,
                        sMirror
                    )
                    result.append(sc.doc.Objects.AddSurface(surface))
                    rs.DeleteObject(intersect[0])
        results.append(rs.JoinSurfaces(result, delete_input = True))

    for cutting in cuttingPlanes:
        rs.DeleteObject(cutting)
    for piece in pieces:
        for p in piece:
            rs.DeleteObject(p)

offsetx = 100
offsety = 100
offsetz = 112.5

# ustep = pi / 64
# ufreq = ustep * 16
# vstep = pi / 64
# vfreq = vstep * 8
# cuttingInterval = 25
# thickness = 12.5

# generate(x1, y1, z1, ustep, ufreq, vstep, cuttingInterval, thickness, 1.5, 1)

offsetx = 100
offsety = 100
offsetz = 112.5

ustep = pi / 64
ufreq = ustep * 16
vstep = pi / 64
vfreq = vstep * 8
cuttingInterval = 15
thickness = 16

generate(x1, y1, z1, ustep, ufreq, vstep, cuttingInterval, thickness, 1.5, 2)

sc.doc.Views.Redraw()
