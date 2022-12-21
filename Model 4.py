from doctest import master
from utils import *
from Rhino.Geometry import NurbsSurface, Line, Polyline, Point3d, Vector3d
import rhinoscriptsyntax as rs
import scriptcontext as sc
from math import *

offsetx = 100
offsety = 100
offsetz = 112.5

offsetx2 = 90
offsety2 = 62.5
offsetz2 = 112.5

ustep = pi / 64
ufreq = ustep * 8
vstep = pi / 64
vfreq = vstep * 8

coneTopDist = 50

def x1(u, v):
    u += v
    return cos(u) * sin(v) + (1 * cos(3 * u) + 3 * cos(5 * u)) / 24

def y1(u, v):
    u += v
    return sin(u) * sin(v) + (1 * sin(3 * u) + 3 * sin(5 * u)) / 24

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

pieces = [[] for i in range(int(pi * 2 / ustep))]
intersects = [[None] * int(pi / vstep / 2) for i in range(int(pi * 2 / ufreq))]
cuttingPlanes = []
normals = []
coneTops = []

innerlayers = []

for u in frange(0, pi * 2, ufreq):
    middleV = Point3d(cos(u), sin(u), 0) * offsetx / sqrt(3)
    planeS = Point3d(middleV[1], - middleV[0], offsetz) + middleV
    planeT = Point3d(- middleV[1], middleV[0], - offsetz) + middleV

    middleV[2] = 0
    middleV = normalizeV(middleV) * 100
    normalV = normalizeV(crossProduct(planeS - planeT, middleV))
    normals.append(normalV)
    normalV = (planeS + planeT) / 2 + normalV * coneTopDist
    coneTops.append(normalV)
    # segment = Polyline(((planeS + planeT) / 2, normalV))
    # sc.doc.Objects.AddPolyline(segment)

    surface = NurbsSurface.CreateFromCorners(
        Point3d(planeS + middleV),
        Point3d(planeS - middleV / 2),
        Point3d(planeT - middleV / 2),
        Point3d(planeT + middleV)
    )
    cuttingPlanes.append(sc.doc.Objects.AddSurface(surface))

for i, u in enumerate(frange(0, pi * 2, ustep)):

    innerlayerpieces = []

    for j, v in enumerate(frange(0, pi, vstep)):

        if (v <= vfreq * 2 - vstep or v > pi - vfreq * 2 - vstep):
            continue

        uu = u + ustep
        vv = v + vstep
        cur = Point3d(x1(u, v) * offsetx, y1(u, v) * offsety, z1(u, v) * offsetz)
        inner = Point3d(x2(u, v) * offsetx, y2(u, v) * offsety, z2(u, v) * offsetz)

        uu = u + ustep
        vv = v + vstep
        surface = NurbsSurface.CreateFromCorners(
            Point3d(x1(u, v) * offsetx, y1(u, v) * offsety, z1(u, v) * offsetz),
            Point3d(x1(uu, v) * offsetx, y1(uu, v) * offsety, z1(uu, v) * offsetz),
            Point3d(x1(uu, vv) * offsetx, y1(uu, vv) * offsety, z1(uu, vv) * offsetz),
            Point3d(x1(u, vv) * offsetx, y1(u, vv) * offsety, z1(u, vv) * offsetz)
        )
        pieces[i].append(sc.doc.Objects.AddSurface(surface))
        surface = NurbsSurface.CreateFromCorners(
            Point3d(x2(u, v) * offsetx2, y2(u, v) * offsety2, z2(u, v) * offsetz2),
            Point3d(x2(uu, v) * offsetx2, y2(uu, v) * offsety2, z2(uu, v) * offsetz2),
            Point3d(x2(uu, vv) * offsetx2, y2(uu, vv) * offsety2, z1(uu, vv) * offsetz2),
            Point3d(x2(u, vv) * offsetx2, y2(u, vv) * offsety2, z2(u, vv) * offsetz2)
        )
        innerlayerpieces.append(sc.doc.Objects.AddSurface(surface))
    innerlayers.append(rs.JoinSurfaces(innerlayerpieces, delete_input = True))

inner = rs.JoinSurfaces(innerlayers, delete_input = True)

def extendPos(base, coneTop, thickness):
    v = base - coneTop
    v = normalizeV(v)
    v = Point3d(v[0], v[1], v[2]) * thickness
    return v

def mirrorPos(base, normal, coneTop, thickness):
    v = extendPos(base, coneTop, thickness)
    dist = normalizeV(normal) * dotProduct(v, normal)
    v = 2 * dist - v
    return v

def thickness(v):
    testLine = sc.doc.Objects.AddPolyline(Polyline((Point3d(v[0] * 2, v[1] * 2, v[2]), Point3d(0, 0, v[2]))))
    intersect = rs.CurveBrepIntersect(testLine, inner)
    lengthLine = rs.AddLine(v, intersect[1][0])
    length = rs.CurveLength(lengthLine, segment_index=-1, sub_domain=None)
    rs.DeleteObject(testLine)
    rs.DeleteObject(intersect[1][0])
    rs.DeleteObject(lengthLine)
    return length / 2 + 10

results = []
for k, cutting in enumerate(cuttingPlanes):
    result = []
    for i in range(len(pieces)):
        for j in range(len(pieces[i])):
            intersect = rs.IntersectBreps(cutting, pieces[i][j])
            if (intersect != None):
                intersects[k].append(rs.coercecurve(intersect[0]))
                sBase = intersects[k][-1].PointAtStart
                sExtend = extendPos(sBase, coneTops[k], thickness(sBase)) + sBase
                sMirror = mirrorPos(sBase, normals[k], coneTops[k], thickness(sBase)) + sBase
                tBase = intersects[k][-1].PointAtEnd
                tExtend = extendPos(tBase, coneTops[k], thickness(tBase)) + tBase
                tMirror = mirrorPos(tBase, normals[k], coneTops[k], thickness(tBase)) + tBase
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

sc.doc.Views.Redraw()