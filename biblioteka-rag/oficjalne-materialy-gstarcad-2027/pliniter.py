"""
...Description:
    This program demonstrates iterating over the vertices of
    a polyline

    1. 执行命令setvar PLINETYPE 0；
    2. APPLOAD PyListPLine；
    3. 绘制一条多段线；
    4. 执行命令PyListPLine，根据提示选择之前绘制的多段线，程序会依次打印出该线的各顶点的坐标信息；
"""
from pygcad.core import *
from pygcad.pygrx import *


def iterate(e_id):
    _, line = gcdbOpenObject(e_id, GcDb.kForRead)
    vert_iter = line.vertexIterator()
    line.close()

    vertex_number = 0
    while not vert_iter.done():
        vertex_obj_id = vert_iter.objectId()
        _, tmp_obj = gcdbOpenObject(vertex_obj_id, GcDb.kForRead)
        vertex = GcDb2dVertex.cast(tmp_obj)
        location = vertex.position()
        vertex.close()

        gcutPrintf("\nVertex #%d's location is"
                   " :%0.3f, %0.3f, %0.3f" % (vertex_number, location.x,
                                              location.y, location.z))

        vertex_number += 1
        vert_iter.step()


def list_pline():
    pt = GcGePoint3d()
    en = gds_name()
    rc = gcedEntSel("\nSelect a polyline: ", en, pt)

    if rc != RTNORM:
        gcutPrintf("\nError during object selection")
        return

    e_id = GcDbObjectId()
    gcdbGetObjectId(e_id, en)

    status, obj = gcdbOpenObject(e_id, GcDb.kForRead)
    if obj.isKindOf(GcDb2dPolyline.desc()):
        obj.close()
        iterate(e_id)
    else:
        obj.close()
        gcutPrintf("\nSelected entity is not an GcDb2dPolyline. "
                   "\nMake sure the setvar PLINETYPE is set to 0 "
                   "before createing a polyline")


@command()
def PyListPLine():
    try:
        list_pline()
    except Exception as err:
        gcutPrintf("%s" % err)