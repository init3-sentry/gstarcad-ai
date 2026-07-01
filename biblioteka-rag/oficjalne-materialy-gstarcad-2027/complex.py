import time

from pygcad.core import *
from pygcad.pygrx import *

import debugpy
# import sys
import traceback
import socket

def makeABlock():
    pBlockTableRec = GcDbBlockTableRecord()
    pBlockTableRec.setName("ASDK-NO-ATTR")
    es, obj = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.OpenMode.kForWrite)
    pBlockTable = GcDbBlockTable.cast(obj)
    blockTableRecordId = GcDbObjectId()
    st = pBlockTable.add(blockTableRecordId, pBlockTableRec)
    pBlockTable.close()

    pLine = GcDbLine()
    pLine.setStartPoint(GcGePoint3d(3, 3, 0))
    pLine.setEndPoint(GcGePoint3d(600, 600, 0))
    pLine.setColorIndex(3)

    pBlockTableRec.appendGcDbEntity(pLine)
    pLine.close()
    pBlockTableRec.close()


def defineBlockWithAttributes(basePoint: GcGePoint3d, textHeight: float, textAngle: float):
    pBlockRecord = GcDbBlockTableRecord()
    pBlockRecord.setName("ASDK-BLOCK-WITH-ATTR")
    pBlockRecord.setOrigin(basePoint)
    es, obj = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.OpenMode.kForWrite)
    pBlockTable = GcDbBlockTable.cast(obj)
    blockId = GcDbObjectId()
    st = pBlockTable.add(blockId, pBlockRecord)

    if st != Gcad.eOk:
        pBlockTable.close()

    pCircle = GcDbCircle()
    pCircle.setCenter(basePoint)
    pCircle.setRadius(textHeight * 4.0)
    pCircle.setColorIndex(3)

    # st, entityId = pBlockRecord.appendGcDbEntity(pCircle)
    pBlockRecord.appendGcDbEntity(pCircle)
    pCircle.close()

    pAttdef = GcDbAttributeDefinition()
    pAttdef.setPosition(basePoint)
    pAttdef.setHeight(textHeight)
    pAttdef.setRotation(textAngle)

    pAttdef.setHorizontalMode(GcDb.kTextLeft)
    pAttdef.setVerticalMode(GcDb.kTextBase)
    pAttdef.setPrompt("Prompt")
    pAttdef.setTextString("DEFAULT")
    pAttdef.setTag("Tag")
    pAttdef.setInvisible(True)
    pAttdef.setVerifiable(False)
    pAttdef.setPreset(False)
    pAttdef.setConstant(False)
    pAttdef.setFieldLength(25)
    pBlockRecord.appendGcDbEntity(pAttdef)
    gcutPrintf('debug:%f' % pAttdef.height())

    obj = pAttdef.clone()
    # inc_ref(obj)
    pAttdef2 = GcDbAttributeDefinition.cast(obj)
    tempPt = basePoint
    tempPt.y -= pAttdef2.height()
    pAttdef2.setPosition(tempPt)
    pAttdef2.setColorIndex(1)
    pAttdef2.setConstant(True)

    pBlockRecord.appendGcDbEntity(pAttdef2)
    pAttdef.close()
    pAttdef2.close()
    pBlockRecord.close()
    pBlockTable.close()

    return blockId


def addBlockWithAttributes():
    basePoint = GcGePoint3d()
    st = gcedGetPoint(None, "\nEnter insertion point: ", basePoint)
    if st != RTNORM:
        return
    st, textAngle = gcedGetAngle(basePoint, "\nEnter rotation angle: ")
    if st != RTNORM:
        return
    st, textHeight = gcedGetDist(basePoint, "\nEnter text height: ")
    if st != RTNORM:
        return


    blockId = defineBlockWithAttributes(basePoint, textHeight, textAngle)
    if blockId.isNull():
        return
    pBlkRef = GcDbBlockReference()
    pBlkRef.setBlockTableRecord(blockId)

    fromvalue = resbuf()
    tovalue = resbuf()

    fromvalue.restype = RTSHORT
    fromvalue.resval.rint = 1
    tovalue.restype = RTSHORT
    tovalue.resval.rint = 0

    normal = GcGeVector3d(0.0, 0.0, 1.0)
    gcedTrans(normal, fromvalue, tovalue, 1, normal)
    pBlkRef.setPosition(basePoint)
    pBlkRef.setRotation(0.0)
    pBlkRef.setNormal(normal)

    es, pBlockTable = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.kForRead)
    _, pBlockTableRecord = pBlockTable.getAt(GCDB_MODEL_SPACE, GcDb.kForWrite)
    pBlockTable.close()
    # pBlockTableRecord = GcDbBlockTableRecord.cast(objr)
    pBlockTableRecord.appendGcDbEntity(pBlkRef)
    pBlockTableRecord.close()

    _, obj = gcdbOpenObject(blockId, GcDb.kForRead)
    pBlockDef = GcDbBlockTableRecord.cast(obj)
    _, iterator = pBlockDef.newIterator()
    iterator.start()
    while not iterator.done():
        _, objEnt = iterator.getEntity(GcDb.kForRead)
        # pEnt = GcDbEntity.cast(objEnt)
        pAttdef = GcDbAttributeDefinition.cast(objEnt)
        if pAttdef is not None and pAttdef.isConstant() == False:
            pAtt = GcDbAttribute()

            pAtt.setPropertiesFrom(pAttdef)
            pAtt.setInvisible(pAttdef.isInvisible())

            basePoint = pAttdef.position()
            basePoint += pBlkRef.position().asVector()
            pAtt.setPosition(basePoint)
            pAtt.setHeight(pAttdef.height())
            pAtt.setRotation(pAttdef.rotation())
            pAtt.setTag("Tag")
            pAtt.setFieldLength(25)
            pStr = pAttdef.tagConst()
            pAtt.setTag(pStr)
            pAtt.setFieldLength(pAttdef.fieldLength())
            pAtt.setTextString("Assigned Attribute Value")

            pBlkRef.appendAttribute(pAtt)
            pAtt.close()
        objEnt.close()
        iterator.step()
    pBlockDef.close()
    pBlkRef.close()


def printAll():
    # time.sleep(30)
    rc, blkName = gcedGetString(True, "Enter Block Name <hit <ENTER> for current space>: ")
    if rc != RTNORM:
        return
    if (blkName is not None) and (len(blkName) > 0):
        if gcdbHostApplicationServices().workingDatabase().tilemode() == False:
            rb = resbuf()
            gcedGetVar("cvport", rb)
            if rb.resval.rint == 1:
                blkName = GCDB_PAPER_SPACE
            else:
                blkName = GCDB_MODEL_SPACE
        else:
            blkName = GCDB_MODEL_SPACE

    _, pBlockTable = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.kForRead)
    es, pBlockTableRecord = pBlockTable.getAt(blkName, GcDb.kForRead)
    pBlockTable.close()

    if es != Gcad.eOk:
        return

    _, iterator = pBlockTableRecord.newIterator()
    iterator.start()
    while not iterator.done():
        _, pEnt = iterator.getEntity(GcDb.kForRead)

        handle = pEnt.getGcDbHandle()
        _, handle_str = handle.getIntoAsciiBuffer()

        pCname = pEnt.isA().name()
        # gcutPrintf("Object Id %lx, handle is None, class %s.\n" % (pEnt.objectId().asOldId(), pCname))
        gcutPrintf("Object Id %lx, handle is %s, class %s.\n" % (pEnt.objectId().asOldId(), handle_str, pCname))
        pEnt.close()
        iterator.step()

    pBlockTableRecord.close()
    gcutPrintf("\n")


def createPolyline():
    # socket.setdefaulttimeout(60)
    # # debugpy.configure(python='/home/cad/.pyenv/versions/3.6.9/bin/python3.6')
    # debugpy.listen(5678)
    # debugpy.wait_for_client()
    # time.sleep(30)

    ptArr = GcGePoint3dArray()
    ptArr.setLogicalLength(4)

    for i in range(0, 4):
        x = float(i / 2.0)
        y = float(i % 2)
        ptArr.at(i).set(x, y, 0.0)

    pNewPline = GcDb2dPolyline(GcDb.k2dSimplePoly, ptArr, 0.0, True)
    pNewPline.setColorIndex(3)

    _, pBlockTable = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.OpenMode.kForRead)
    _, pBlockTableRecord = pBlockTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
    pBlockTable.close()
    pBlockTableRecord.appendGcDbEntity(pNewPline)
    pBlockTableRecord.close()
    pNewPline.setLayer("0")
    pNewPline.close()


def addToModelSpace(objId: GcDbObjectId, pEntity: GcDbEntity):
    _, pBTable = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.OpenMode.kForRead)
    _, pSpaceRe = pBTable.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
    pSpaceRecord = GcDbBlockTableRecord.cast(pSpaceRe)
    pSpaceRecord.appendGcDbEntity(objId, pEntity)
    pBTable.close()
    pEntity.close()
    pSpaceRecord.close()


@command()
def PyMakeABlock():
    try:
        makeABlock()
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyCreatePolyline():
    try:
        createPolyline()
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyAddBlockWithAttributes():
    try:
        addBlockWithAttributes()
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyPrintAll():
    try:
        printAll()
    except Exception as err:
        gcedPrompt("%s" % err)
