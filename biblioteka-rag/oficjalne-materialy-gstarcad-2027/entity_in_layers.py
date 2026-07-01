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

def createLine(strLayerName,startPt,endPt):
    line = GcDbLine(startPt,endPt)
    status ,blockTable = gcdbWorkingDatabase().getBlockTable(GcDb.kForRead)
    status,blockTableRecord = blockTable.getAt(GCDB_MODEL_SPACE,GcDb.OpenMode.kForWrite)
    
    blockTableRecord.appendGcDbEntity(line)
    line.setLayer(strLayerName)

    blockTable.close()
    blockTableRecord.close()
    line.close()

def createCircle(strLayerName,center,radius):
    normal = GcGeVector3d(0.0,0.0,1.0)
    circle = GcDbCircle(center,normal,radius)
    status,blockTable = gcdbWorkingDatabase().getBlockTable(GcDb.kForRead)
    status,blockTableRecord = blockTable.getAt(GCDB_MODEL_SPACE,GcDb.OpenMode.kForWrite)
    blockTableRecord.appendGcDbEntity(circle)
    circle.setLayer(strLayerName)

    blockTable.close()
    blockTableRecord.close()
    circle.close()
    

@command()
def pyEntiyInLayers():
    try:
        color = GcCmColor()

        color.setRGB(255,0,0)
        add_layer("layer1",color,"BANKLINE1")

        color.setRGB(0,255,0)
        add_layer("layer2",color,"BANKLINE2")


        pt1 = GcGePoint3d(1000,1000,0)
        pt2 = GcGePoint3d(1000+1000,1000,0)
        createLine("layer1",pt1,pt2)

        center = GcGePoint3d(1000,1000,0)
        radius = 300
        createCircle("layer2",center,radius)

        center = GcGePoint3d(1000,1000,0)
        radius = 600
        createCircle("layer2",center,radius)


    except Exception as err:
        gcutPrintf("\n %s" % err)







