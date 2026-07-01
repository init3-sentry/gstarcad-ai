from pygcad.core import *
from pygcad.pygrx import *

def add_layer(strName,color,strLineType):
    status,layerTable=gcdbWorkingDatabase().getLayerTable(GcDb.kForWrite)

    if not layerTable.has(strName):
        layerTRecord = GcDbLayerTableRecord()
        layerTRecord.setName(strName)
        layerTRecord.setIsLocked(0)
        layerTRecord.setColor(color)

        status,lineTypeTable = gcdbWorkingDatabase().getLinetypeTable()
        status,lineTypeId = lineTypeTable.getObjIdAt(strLineType)
        if status != 0:
            gcutPrintf("\n can not find %s linetype. default is continuous." % strLineType)
            status,lineTypeId = lineTypeTable.getObjIdAt("continous")
        lineTypeTable.close()
        layerTRecord.setLinetypeObjectId(lineTypeId)
        layerTable.add(layerTRecord)
        layerTRecord.close()
        layerTable.close()
    else:
        layerTable.close()
        gcutPrintf("\n %s is exist." % strName)

def createRect(strLayerName,pt1,pt2):
    x_min = min(pt1.x,pt2.x)
    x_max = max(pt1.x,pt2.x)
    y_min = min(pt1.y,pt2.y)
    y_max = max(pt2.y,pt2.y)

    leftButtom = GcGePoint2d(x_min,y_min)
    leftTop = GcGePoint2d(x_min,y_max)
    rightTop = GcGePoint2d(x_max,y_max)
    rightButtom = GcGePoint2d(x_max,y_min)

    polyLine = GcDbPolyline()
    polyLine.addVertexAt(0,leftButtom,0,0,0)
    polyLine.addVertexAt(1,leftTop,0,0,0)
    polyLine.addVertexAt(2,rightTop,0,0,0)
    polyLine.addVertexAt(3,rightButtom,0,0,0)
    polyLine.addVertexAt(polyLine.numVerts(),leftButtom,0,0,0)
    polyLine.setLayer(strLayerName)

    status,blockTable = gcdbWorkingDatabase().getBlockTable(GcDb.kForRead)
    status,blockTableRecord = blockTable.getAt(GCDB_MODEL_SPACE,GcDb.OpenMode.kForWrite)
    blockTableRecord.appendGcDbEntity(polyLine)

    blockTable.close()
    blockTableRecord.close()
    polyLine.close()
    
def createDim(strLayerName,pt1,pt2,pt3,strText):
    dim = GcDbAlignedDimension(pt1,pt2,pt3,strText)
    #dim.setTextDefinedSize(100,100)
    status,blockTable = gcdbWorkingDatabase().getBlockTable(GcDb.kForRead)
    status,blockTableRecord = blockTable.getAt(GCDB_MODEL_SPACE,GcDb.OpenMode.kForWrite)

    dim.setLayer(strLayerName)

    blockTableRecord.appendGcDbEntity(dim)
    blockTable.close()
    blockTableRecord.close()
    dim.close()

@command()
def pyRectDim():
    try:
        color = GcCmColor()

        color.setRGB(255,0,0)
        add_layer("layer1",color,"BANKLINE1")

        color.setRGB(0,255,0)
        add_layer("layer2",color,"BANKLINE2")

        pt1 = GcGePoint2d(0,0)
        pt2 = GcGePoint2d(2000,2000)
        createRect("layer1",pt1,pt2)

        pt1 = GcGePoint3d(2000,0,0)
        pt2 = GcGePoint3d(2000,2000,0)
        pt3 = GcGePoint3d(2000+100,1000,0)
        strText = "with:2000cm"
        createDim("layer2",pt1,pt2,pt3,strText)
    except Exception as err:
        gcutPrintf("\n %s" % err)