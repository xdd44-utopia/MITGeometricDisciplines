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

centerOffset = Vector3d(-8, -22.5, 0)

coneTopDist = 36

def x1(u, v):
    u += v * 0.5
    return cos(u) * ((abs(v - pi / 2) ** 1.5) * 0.8 + pi / 5) + 2 * cos(v * u / 4) / 6

def y1(u, v):
    u += v * 0.5
    return sin(u) * ((abs(v - pi / 2) ** 1.5) * 0.8 + pi / 5) + 2 * cos(v * u / 4) / 6

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
intersects = []
cuttingPlanes = []
normals = []
tangents = []

u = -0.1
while (u < pi * 2):
    middleV = Point3d(cos(u), sin(u), 0) * offsetx / sqrt(3)
    tangents.append(normalizeV(middleV))
    k = 1.2
    planeS = Point3d(middleV[1] * k, - middleV[0] * k, offsetz) + middleV
    planeT = Point3d(- middleV[1] * k, middleV[0] * k, - offsetz) + middleV

    middleV[2] = 0
    middleV = normalizeV(middleV) * 100
    normalV = normalizeV(crossProduct(planeS - planeT, middleV))
    normals.append(normalV)
    # segment = Polyline(((planeS + planeT) / 2, normalV))
    # sc.doc.Objects.AddPolyline(segment)

    surface = NurbsSurface.CreateFromCorners(
        Point3d(planeS + middleV * 2 + centerOffset),
        Point3d(planeS - middleV / 2 + centerOffset),
        Point3d(planeT - middleV / 2 + centerOffset),
        Point3d(planeT + middleV * 2 + centerOffset)
    )
    cuttingPlanes.append(sc.doc.Objects.AddSurface(surface))
    intersects.append([None] * int(pi / vstep / 2))

    u += ufreq

for i, u in enumerate(frange(0, pi * 2, ustep)):
    for j, v in enumerate(frange(0, pi, vstep)):

        if (v <= vfreq - vstep or v > pi - vfreq - vstep):
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

def angleness(v):
    angle = asin(v[1] / magnitudeV([v[0], v[1], 0]))
    if (v[0] < 0):
        angle = (pi - angle) if (angle > 0) else (- pi - angle)
    if (angle < pi / 2):
        angle += pi * 2
    return angle

def angleDiff(angle):
    diff = abs(angle - 5 * pi / 3)
    if (diff > pi):
        diff = pi * 2 - diff
    return diff

def thickness(v, isInside):
    v = v - centerOffset
    angle = angleness(v)
    if (isInside):
        ret = (abs(v[2] - 24) ** 2) / 125 + (angleDiff(angle) ** 2 + 1) * 6 + 16
    else:
        ret = (abs(v[2] - 36) ** 2) / 600 + 24
    return ret

results = []
for k, cutting in enumerate(cuttingPlanes):
    result = []
    for i in range(len(pieces)):
        for j in range(len(pieces[i])):
            intersect = rs.IntersectBreps(cutting, pieces[i][j])
            if (intersect != None):
                intersects[k].append(rs.coercecurve(intersect[0]))
                sBase = intersects[k][-1].PointAtStart
                tBase = intersects[k][-1].PointAtEnd
                sDir = (normals[k] + (4.5 - angleDiff(angleness(sBase)) ** 2 / 2.75) * tangents[k]) * coneTopDist
                tDir = (normals[k] + (4.5 - angleDiff(angleness(tBase)) ** 2 / 2.75) * tangents[k]) * coneTopDist
                sDir[2] = sDir[2] * 1.2
                tDir[2] = tDir[2] * 1.2
                sTop = sBase + sDir
                tTop = tBase + tDir
                sExtend = extendPos(sBase, sTop, thickness(sBase, False)) + sBase
                sMirror = mirrorPos(sBase, normals[k], sTop, thickness(sBase, True)) + sBase
                tExtend = extendPos(tBase, tTop, thickness(tBase, False)) + tBase
                tMirror = mirrorPos(tBase, normals[k], tTop, thickness(tBase, True)) + tBase
                # segment = Polyline((sBase, sTop))
                # sc.doc.Objects.AddPolyline(segment)
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