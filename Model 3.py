from doctest import master
from utils import *
from Rhino.Geometry import NurbsSurface, Line, Polyline, Point3d, Vector3d
import rhinoscriptsyntax as rs
import scriptcontext as sc
from math import *

def x1(u, v):
    u += v
    return cos(u) * sin(v) + (1 * cos(3 * u) + 3 * cos(5 * u)) / 24

def y1(u, v):
    u += v
    return sin(u) * sin(v) + (1 * sin(3 * u) + 3 * sin(5 * u)) / 24

def z1(u, v):
    return cos(v) * 1.125

def x2(u, v):
    u += v
    u = - u
    return cos(u) * sin(v) + cos(3 * u) / 4

def y2(u, v):
    u += v
    u = - u
    return sin(u) * sin(v) + sin(3 * u) / 4

def z2(u, v):
    return cos(v) * 1.125

def generate(x, y, z, ustep, ufreq, vstep):

    piecesid = [[] for i in range(int(pi * 2 / ustep))]
    piecesm = [[] for i in range(int(pi * 2 / ustep))]
    intersectsid = [[None] * int(pi / vstep / 2) for i in range(int(pi * 2 / ufreq))]
    cuttingPlaneids = []

    for u in frange(0, pi * 2, ufreq):
        planeS = Point3d(x[0](u, vfreq * 2) * offsetx[0], y[0](u, vfreq * 2) * offsety[0], z[0](u, vfreq * 2))
        planeT = Point3d(x[0](u, vfreq * 6) * offsetx[0], y[0](u, vfreq * 6) * offsety[0], z[0](u, vfreq * 6))
        middleV = (planeS + planeT) / 2
        middleV[2] = 0
        middleV = normalize(middleV)
        middleV = Point3d(middleV[0], middleV[1], middleV[2]) / 10

        surface = NurbsSurface.CreateFromCorners(
            Point3d(planeS + middleV * 10),
            Point3d(planeS),
            Point3d(planeT),
            Point3d(planeT + middleV * 10)
        )
        cuttingPlaneids.append(sc.doc.Objects.AddSurface(surface))

    for i, u in enumerate(frange(0, pi * 2, ustep)):

        for j, v in enumerate(frange(0, pi, vstep)):

            if (v <= vfreq * 2 - vstep or v > pi - vfreq * 2 - vstep):
                continue
            
            for f in range(len(x)):
                uu = u + ustep
                vv = v + vstep
                cur = Point3d(x[f](u, v) * offsetx[f], y[f](u, v) * offsety[f], z[f](u, v))
                nex = Point3d(x[f](u, vv) * offsetx[f], y[f](u, vv) * offsety[f], z[f](u, vv))

                uu = u + ustep
                vv = v + vstep
                surface = NurbsSurface.CreateFromCorners(
                    Point3d(x[0](u, v) * offsetx[0], y[0](u, v) * offsety[0], z[0](u, v)),
                    Point3d(x[0](uu, v) * offsetx[0], y[0](uu, v) * offsety[0], z[0](uu, v)),
                    Point3d(x[0](uu, vv) * offsetx[0], y[0](uu, vv) * offsety[0], z[0](uu, vv)),
                    Point3d(x[0](u, vv) * offsetx[0], y[0](u, vv) * offsety[0], z[0](u, vv))
                )
                piecesid[i].append(sc.doc.Objects.AddSurface(surface))
                piecesm[i].append((
                    Point3d(x[0](uu, v) * offsetx[0], y[0](uu, v) * offsety[0], z[0](uu, v)) + 
                    Point3d(x[0](u, vv) * offsetx[0], y[0](u, vv) * offsety[0], z[0](u, vv))
                ) / 2)

    for k, cuttingid in enumerate(cuttingPlaneids):
        for j in range(len(piecesid[i])):
            for i in range(len(piecesid)):
                intersectid = rs.IntersectBreps(cuttingid, piecesid[i][j])
                if (intersectid != None):
                    intersectsid[k][j] = rs.coercecurve(intersectid[0])
                    segment = Polyline((intersectsid[k][j].PointAtStart, intersectsid[k][j].PointAtEnd))
                    sc.doc.Objects.AddPolyline(segment)
                    segment = Line(intersectsid[k][j].PointAtStart, intersectsid[k][j].PointAtEnd)
                    closestPoint = segment.ClosestPoint(piecesm[i][j], False)
                    closestV = normalize(piecesm[i][j] - closestPoint)
                    closestV = Point3d(closestV[0], closestV[1], closestV[2]) / 10
                    if (closestV[2] > 0):
                        closestV = - closestV
                    otherPoint = closestPoint + closestV
                    normal = Polyline((closestPoint, otherPoint))
                    sc.doc.Objects.AddPolyline(normal)

xf = [x1]
yf = [y1]
zf = [z1]
offsetx = [1]
offsety = [1]

# xf = [x1, x1]
# yf = [y1, y1]
# zf = [z1, z1]
# offsetx = [1, 0.9]
# offsety = [1, 0.9]
    
ustep = pi / 256
ufreq = ustep * 64
vstep = pi / 64
vfreq = vstep * 8

generate(xf, yf, zf, ustep, ufreq, vstep)

sc.doc.Views.Redraw()
