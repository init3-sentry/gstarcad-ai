"""
..Description:
    一个绘制椭圆的程序。

    1. 手动绘制一个任意形状的椭圆
    1. APPLOAD curve.py
    2. 运行命令 pyCurveTEST，根据提示拾取一个椭圆实体；
    3. 拾取成功后，命令有两个分支(Offset/<Project>), 默认为Project模式；
        - Project模式：绘制椭圆在给定平面上的一个投影，该平面的法线向量为(1,1,1)
        - Offset模式：复制一个椭圆实体，将复制后的实体平移0.5个单位

"""


from pygcad.core import *
from pygcad.pygrx import *

import pysnooper


@pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='curves_debug: ')
def curves():
    en = gds_name()
    pt = GcGePoint3d()
    if gcedEntSel("\nSelect an Ellipse: ", en, pt) != RTNORM:
        return

    eId = GcDbObjectId()
    gcdbGetObjectId(eId, en)

    (es, pObj) = gcdbOpenObject(eId, GcDb.OpenMode.kForRead)

    if pObj.isKindOf(GcDbEllipse.desc()):
        pObj.close()

        gcedInitGet(0, "Offset Project")
        (rc, kw) = gcedGetKword("Offset/<Project>: ")

        if rc != RTNORM and rc != RTNONE:
            gcutPrintf("\nNothing selected.")
            return
        elif rc == RTNONE or kw == "Project":
            projectEllipse(eId)
        else:
            offsetEllipse(eId)
    else:
        pObj.close()
        gcutPrintf("\nSelected entity is not an ellipse")


@pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='projectEllipse_debug: ')
def projectEllipse(ellipseId: GcDbObjectId):
    (es, pObj) = gcdbOpenObject(ellipseId, GcDb.OpenMode.kForRead)

    pEllipse = None
    if pObj.isKindOf(GcDbEllipse.desc()):
        pEllipse = GcDbEllipse.cast(pObj)

    (es, pProjectedCurve) = pEllipse.getOrthoProjectedCurve(
        GcGePlane(GcGePoint3d.kOrigin, GcGeVector3d(1, 1, 1)))
    pEllipse.close()

    addToModelSpace(pProjectedCurve)


@pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='offsetEllipse_debug: ')
def offsetEllipse(ellipseId: GcDbObjectId):
    (es, pObj) = gcdbOpenObject(ellipseId, GcDb.OpenMode.kForRead)

    pEllipse = None
    if pObj.isKindOf(GcDbEllipse.desc()):
        pEllipse = GcDbEllipse.cast(pObj)

    (es, curves) = pEllipse.getOffsetCurves(0.5)
    pEllipse.close()

    pEntity = GcDbEntity.cast(curves[0])
    addToModelSpace(pEntity)


def addToModelSpace(pEntity: GcDbEntity):
    (es, pBlockTable) = gcdbHostApplicationServices().workingDatabase().getBlockTable(
        GcDb.OpenMode.kForRead)

    with pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='addToModelSpace_inner_debug: '):
        (es, pSpaceRecord) = pBlockTable.getAt(
            GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)

    pBlockTable.close()
    (res, objId) = pSpaceRecord.appendGcDbEntity(pEntity)

    pEntity.close()
    pSpaceRecord.close()

    return Gcad.eOk


@command()
def pyCurveTEST():
    try:
        curves()
    except Exception as err:
        gcutPrintf("[ERROR]: %s" % err)
