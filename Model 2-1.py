from ast import Delete
from Rhino.Geometry import NurbsSurface, Polyline, Point3d
import rhinoscriptsyntax as rs
import scriptcontext as sc
from math import *

def frange(start, stop=None, step=None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1

def x1(u, v):
    u += v
    return cos(u) * (sin(v)) + ((1 * cos(3 * u) + 3 * cos(5 * u)) / 24)

def y1(u, v):
    u += v
    return sin(u) * (sin(v)) + ((1 * sin(3 * u) + 3 * sin(5 * u)) / 24)

def z1(u, v):
    return cos(v) * 1.25

def x2(u, v):
    u += v
    return cos(u) * (sin(v)) + (1 * cos(3 * u) / 5)

def y2(u, v):
    u += v
    return sin(u) * (sin(v)) + (1 * sin(3 * u) / 5)

def z2(u, v):
    return cos(v) * 1.25
    
ustep = pi / 36
vstep = pi / 12

x = [x1, x2]
y = [y1, y2]
z = [z1, z2]
offsetx = [1.2, 1.08]
offsety = [1.2, 0.75]

def generate(ustep, vstep):

    for i, u in enumerate(frange(0, pi * 2, ustep)):
        for j, v in enumerate(frange(0, pi, vstep)):

            if (v <= vstep * 2 or v > pi - vstep * 4):
                continue
            
            for f in range(len(x)):
                cur = Point3d(x[f](u, v) * offsetx[f], y[f](u, v) * offsety[f], z[f](u, v))
                uu = u + ustep
                vv = v + vstep
                nex = Point3d(x[f](uu, vv) * offsetx[f], y[f](uu, vv) * offsety[f], z[f](uu, vv))
                # segment = Polyline((cur, nex))
                # sc.doc.Objects.AddPolyline(segment)

                if (f > 0 and i % 3 == 0):
                    surface = NurbsSurface.CreateFromCorners(
                        Point3d(x[f](u, v) * offsetx[f], y[f](u, v) * offsety[f], z[f](u, v)),
                        Point3d(x[f](uu, vv) * offsetx[f], y[f](uu, vv) * offsety[f], z[f](uu, vv)),
                        Point3d(x[f - 1](uu, vv) * offsetx[f - 1], y[f - 1](uu, vv) * offsety[f - 1], z[f - 1](uu, vv)),
                        Point3d(x[f - 1](u, v) * offsetx[f - 1], y[f - 1](u, v) * offsety[f - 1], z[f - 1](u, v))
                    )
                    uu = u + 3 * ustep
                    vv = v + vstep
                    # surface = NurbsSurface.CreateFromCorners(
                    #     Point3d(x[f](u, v) * offset[f], y[f](u, v) * offset[f], z[f](u, v)),
                    #     Point3d(x[f](uu, vv) * offset[f], y[f](uu, vv) * offset[f], z[f](uu, vv)),
                    #     Point3d(x[f - 1](uu, vv) * offset[f - 1], y[f - 1](uu, vv) * offset[f - 1], z[f - 1](uu, vv)),
                    #     Point3d(x[f - 1](u, v) * offset[f - 1], y[f - 1](u, v) * offset[f - 1], z[f - 1](u, v))
                    # )
                    # sc.doc.Objects.AddSurface(surface)
                    for kk in range(2):
                        k = kk
                        k = kk - 0.5 * j
                        p1 = [
                            Point3d(x[f](u + k * ustep, v) * offsetx[f], y[f](u + k * ustep, v) * offsety[f], z[f](u + k * ustep, v)),
                            Point3d(x[f](u + (k + 1) * ustep, v) * offsetx[f], y[f](u + (k + 1) * ustep, v) * offsety[f], z[f](u + (k + 1) * ustep, v)),
                            Point3d(x[f](u + (k + 2) * ustep, v + vstep) * offsetx[f], y[f](u + (k + 2) * ustep, v + vstep) * offsety[f], z[f](u + (k + 2) * ustep, v + vstep)),
                            Point3d(x[f](u + (k + 1) * ustep, v + vstep) * offsetx[f], y[f](u + (k + 1) * ustep, v + vstep) * offsety[f], z[f](u + (k + 1) * ustep, v + vstep))
                        ]
                        p2 = [
                            Point3d(x[f - 1](u + k * ustep, v) * offsetx[f - 1], y[f - 1](u + k * ustep, v) * offsety[f - 1], z[f - 1](u + k * ustep, v)),
                            Point3d(x[f - 1](u + (k + 1) * ustep, v) * offsetx[f - 1], y[f - 1](u + (k + 1) * ustep, v) * offsety[f - 1], z[f - 1](u + (k + 1) * ustep, v)),
                            Point3d(x[f - 1](u + (k + 2) * ustep, v + vstep) * offsetx[f - 1], y[f - 1](u + (k + 2) * ustep, v + vstep) * offsety[f - 1], z[f - 1](u + (k + 2) * ustep, v + vstep)),
                            Point3d(x[f - 1](u + (k + 1) * ustep, v + vstep) * offsetx[f - 1], y[f - 1](u + (k + 1) * ustep, v + vstep) * offsety[f - 1], z[f - 1](u + (k + 1) * ustep, v + vstep))
                        ]
                        surface = NurbsSurface.CreateFromCorners(p1[0], p1[1], p1[3])
                        sc.doc.Objects.AddSurface(surface)
                        surface = NurbsSurface.CreateFromCorners(p1[1], p1[2], p1[3])
                        sc.doc.Objects.AddSurface(surface)
                        surface = NurbsSurface.CreateFromCorners(p2[0], p2[1], p2[3])
                        sc.doc.Objects.AddSurface(surface)
                        surface = NurbsSurface.CreateFromCorners(p2[1], p2[2], p2[3])
                        sc.doc.Objects.AddSurface(surface)
                        # surface = NurbsSurface.CreateFromCorners(p1[0], p1[1], p1[2], p1[3])
                        # sc.doc.Objects.AddSurface(surface)
                        # surface = NurbsSurface.CreateFromCorners(p2[0], p2[1], p2[2], p2[3])
                        # sc.doc.Objects.AddSurface(surface)
                        if (kk == 0):
                            # surface = NurbsSurface.CreateFromCorners(p1[3], p2[3], p2[0])
                            # sc.doc.Objects.AddSurface(surface)
                            # surface = NurbsSurface.CreateFromCorners(p1[0], p1[3], p2[0])
                            # sc.doc.Objects.AddSurface(surface)
                            surface = NurbsSurface.CreateFromCorners(p1[0], p1[3], p2[3], p2[0])
                            sc.doc.Objects.AddSurface(surface)
                        if (kk == 1):
                            # surface = NurbsSurface.CreateFromCorners(p1[1], p1[2], p2[2])
                            # sc.doc.Objects.AddSurface(surface)
                            # surface = NurbsSurface.CreateFromCorners(p2[2], p2[1], p1[1])
                            # sc.doc.Objects.AddSurface(surface)
                            surface = NurbsSurface.CreateFromCorners(p1[1], p1[2], p2[2], p2[1])
                            sc.doc.Objects.AddSurface(surface)
                        # surface = NurbsSurface.CreateFromCorners(p1[0], p1[1], p2[1], p2[0])
                        # sc.doc.Objects.AddSurface(surface)
                        # surface = NurbsSurface.CreateFromCorners(p1[2], p1[3], p2[3], p2[2])
                        # sc.doc.Objects.AddSurface(surface)


generate(ustep, vstep)

# for u in frange(0, pi * 2, ustep):
#     for v in frange(0, pi, vstep):
#         cur = Point3d(x2(u, v) * scale, y2(u, v) * scale, z2(u, v))
#         uu = u + ustep
#         vv = v
#         nex = Point3d(x2(uu, vv) * scale, y2(uu, vv) * scale, z2(uu, vv))
#         segment = Polyline((cur, nex))
#         sc.doc.Objects.AddPolyline(segment)

sc.doc.Views.Redraw()
