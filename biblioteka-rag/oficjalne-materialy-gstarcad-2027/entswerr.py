"""
...Description:
    一个用于测试错误信息捕获和打印的程序

    1. APPLOAD entswerr.py
    2. 执行命令pyERRTST, 程序会自动绘制一个圆，并创建一个名为ASDK_MYLAYER的图层；
    3. 再次执行命令pyERRTST，这时会提示“重名的图层已经存在”
"""


from pygcad.core import *
from pygcad.pygrx import *

import pysnooper


def createCircle():
    circleId = GcDbObjectId.kNull
    center = GcGePoint3d(9.0, 3.0, 0.0)
    normal = GcGeVector3d(0.0, 0.0, 1.0)
    pCirc = GcDbCircle(center, normal, 2.0)

    if pCirc == None:
        return (Gcad.eOutOfMemory, circleId)

    (es, pBlockTable) = gcdbHostApplicationServices(
    ).workingDatabase().getBlockTable(GcDb.kForRead)
    if es != Gcad.eOk:
        # pCirc.delete()
        return (es, circleId)

    (es, pBlockTableRecord) = pBlockTable.getAt(
        GCDB_MODEL_SPACE, GcDb.kForWrite)
    if es != Gcad.eOk:
        es2 = pBlockTable.close()
        if es2 != Gcad.eOk:
            gcutPrintf(gcadErrorStatusText(es2))
        # pCirc.delete()
        return (es, circleId)

    es = pBlockTable.close()
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))

    (es, circleId) = pBlockTableRecord.appendGcDbEntity(pCirc)
    if es != Gcad.eOk:
        es2 = pBlockTableRecord.close()
        if es2 != Gcad.eOk:
            gcutPrintf(gcadErrorStatusText(es2))
        # pCirc.delete()
        return (es, circleId)

    es = pBlockTableRecord.close()
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))

    es = pCirc.close()
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))
    return (es, circleId)


@pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='createNewLayer_debug: ')
def createNewLayer():
    pLayerTableRecord = GcDbLayerTableRecord()
    if pLayerTableRecord == None:
        return Gcad.eOutOfMemory

    es = pLayerTableRecord.setName("ASDK_MYLAYER")
    if es != Gcad.eOk:
        # pLayerTableRecord.delete()
        return es

    (es, pLayerTable) = gcdbHostApplicationServices(
    ).workingDatabase().getLayerTable(GcDb.kForWrite)
    if es != Gcad.eOk:
        # pLayerTableRecord.delete()
        return es

    (es, pLinetypeTbl) = gcdbHostApplicationServices(
    ).workingDatabase().getLinetypeTable(GcDb.kForWrite)
    if es != Gcad.eOk:
        # pLayerTableRecord.delete()
        es = pLayerTable.close()
        if es != Gcad.eOk:
            gcutPrintf(gcadErrorStatusText(es))

        return es

    (es, ltypeObjId) = pLinetypeTbl.getObjIdAt("CONTINUOUS")
    if es != Gcad.eOk:
        # pLayerTableRecord.delete()
        pLinetypeTbl.close()
        es = pLayerTable.close()
        if es != Gcad.eOk:
            gcutPrintf(gcadErrorStatusText(es))
        return es
    pLinetypeTbl.close()

    pLayerTableRecord.setLinetypeObjectId(ltypeObjId)
    es = pLayerTable.add(pLayerTableRecord)
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))
        es2 = pLayerTable.close()
        if es2 != Gcad.eOk:
            gcutPrintf(gcadErrorStatusText(es2))
        # pLayerTableRecord.delete()
        return es

    es = pLayerTable.close()
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))

    es = pLayerTableRecord.close()
    if es != Gcad.eOk:
        gcutPrintf(gcadErrorStatusText(es))

    return es


def doit():
    (es, circleId) = createCircle()
    # if es != Gcad.eOk:
    #     gcutPrintf(gcadErrorStatusText(es))

    es = createNewLayer()
    # if es != Gcad.eOk:
    #     gcutPrintf(gcadErrorStatusText(es))


@command()
def pyERRTST():
    doit()
