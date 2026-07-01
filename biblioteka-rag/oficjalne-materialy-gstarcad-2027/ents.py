"""
...Description:
    一个绘制各种实体和修改实体属性的程序

    1. APPLOAD ents.py
    2. 执行命令 PYMKENTS
    3. 运行命令后程序会绘制一条直线, 一个线型颜色为红色的圆，并创建一个名为ASDK_MYLAYER的图层
"""


from pygcad.core import *
from pygcad.pygrx import *
import pysnooper


def createLine():
    startPt = GcGePoint3d(4.0, 2.0, 0.0)
    entPt = GcGePoint3d(10, 7.0, 0.0)
    pLine = GcDbLine(startPt, entPt)

    es, pBlockTable = gcdbHostApplicationServices(
    ).workingDatabase().getBlockTable(GcDb.kForRead)

    es, pBlockTableRecord = pBlockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    pBlockTable.close()

    es, lineId = pBlockTableRecord.appendGcDbEntity(pLine)
    pBlockTableRecord.close()
    pLine.close()

    return lineId


def createCircle():
    center = GcGePoint3d(9.0, 3.0, 0.0)
    normal = GcGeVector3d(0.0, 0.0, 1.0)
    pCirc = GcDbCircle(center, normal, 2.0)

    es, pBlockTable = gcdbHostApplicationServices(
    ).workingDatabase().getBlockTable(GcDb.kForRead)

    es, pBlockTableRecord = pBlockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    pBlockTable.close()

    es, circleId = pBlockTableRecord.appendGcDbEntity(pCirc)
    pBlockTableRecord.close()
    pCirc.close()

    return circleId


def createNewLayer():
    es, pLayerTable = gcdbHostApplicationServices(
    ).workingDatabase().getLayerTable(GcDb.kForWrite)

    pLayerTableRecord = GcDbLayerTableRecord()
    pLayerTableRecord.setName("ASDK_MYLAYER")

    pLayerTable.add(pLayerTableRecord)
    pLayerTable.close()
    pLayerTableRecord.close()


def createGroup(objIds=[], pGroupName=""):
    pGroup = GcDbGroup(pGroupName)

    es, pGroupDict = gcdbHostApplicationServices(
    ).workingDatabase().getGroupDictionary(GcDb.kForWrite)

    es, pGroupId = pGroupDict.setAt(pGroupName, pGroup)
    pGroupDict.close()

    for i in range(len(objIds)):
        pGroup.append(objIds[i])

    pGroup.close()


def changeColor(entId: GcDbObjectId, newColor: int):
    es, pObj = gcdbOpenObject(entId, GcDb.kForWrite)
    if pObj.isKindOf(GcDbEntity.desc()):
        pEntity = GcDbEntity.cast(pObj)
    pEntity.setColorIndex(newColor)
    pEntity.close()
    return Gcad.eOk


def runIt():
    createNewLayer()

    idArr = []
    idArr.append(createLine())
    idArr.append(createCircle())

    changeColor(idArr[-1], 1)

    createGroup(idArr, "ASDK_TEST_GROUP")


@command()
def pyMKENTS():
    runIt()
