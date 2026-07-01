from pygcad.core.runtime import * 
from pygcad.pygrx import *


@command()
def pyPrint():
    gcedPrompt('\nhellopython')


@command()
def pyDrawLine():
    # mkLine()
    try:
        database = gcdbWorkingDatabase()
        (status, blockTbl) = database.getBlockTable(GcDb.OpenMode.kForRead)
        (status, record) = blockTbl.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTbl.close()
        line = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(100, 100, 0))
        (status, objId) = record.appendGcDbEntity(line)

        record.close()
        line.close()
    except Exception as err:
        gcedPrompt('---- [ERROR]: %s'%err)


@command()
def pyDrawLineViaTrans():
    try:
        database = gcdbWorkingDatabase()
        with gcdbTransactionManagerPtr() as trans:
            (status, blockTbl) = database.getBlockTable(GcDb.OpenMode.kForRead)
            (status, record) = blockTbl.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
            blockTbl.close()

            line = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(-100, 100, 0))
            (status, objId) = record.appendGcDbEntity(line)
            record.close()

            trans.addNewlyCreatedDBRObject(line)
            line.close()

    except Exception as err:
        gcedPrompt('---- [ERROR]: %s'%err)




