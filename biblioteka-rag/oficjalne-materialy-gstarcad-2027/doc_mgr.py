"""
图纸文件保存退出示例:
设置当前操作文档->绘制直线,圆形实体->保存退出图纸.

"""

from pygcad.core.runtime import * 
from pygcad.pygrx import *


@command()
def pyMyDoc():
    try:
        curActiveDoc = gcDocManagerPtr().mdiActiveDocument()
        gcDocManagerPtr().setCurDocument(curActiveDoc)

        database = gcdbWorkingDatabase()
        (status, blockTbl) = database.getBlockTable(GcDb.OpenMode.kForRead)
        (status, record) = blockTbl.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blockTbl.close()
        line = GcDbLine(GcGePoint3d(0, 0, 0), GcGePoint3d(1000, 1000, 0))

        x = gcdbWorkingDatabase().ucsxdir()
        y = gcdbWorkingDatabase().ucsydir()
        normal = x.crossProduct(y)
        normal.normalize()

        circle = GcDbCircle(GcGePoint3d(1000,1000,0),normal,500)

        (status, objId) = record.appendGcDbEntity(line)
        (status, objId) = record.appendGcDbEntity(circle)

        record.close()
        line.close()
        circle.close()

        curDoc = gcDocManagerPtr().curDocument()
        gcDocManagerPtr().closeDocument(curDoc)

    except Exception as err:
        gcedPrompt('---- [ERROR]: %s'%err)



