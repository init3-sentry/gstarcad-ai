"""
Description:

This program demonstrates reading and writing GcDbDatabase Objects. It implements createDwg() and readDwg().


1. Load testdb.py
2. Command: PYCREATE. 这个命令会在桌面上生成一个test1.dwg的文件，里面包含了两个圆
3. Command: PYREAD。这个命令会读取之前输出的test1.dwg文件，然后打印出里面的所有实体的类型名字，实际运行结果如下
        classname: AcDbCircle
        classname: AcDbCircle
"""
from pygcad.core.runtime import *
from pygcad.pygrx import *

import os

desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
file_path = os.path.join(desktop_path, 'test1.dwg')


@command()
def PyCreate():
    try:
        database = GcDbDatabase(True, False)

        (status, blk_table) = database.getBlockTable(GcDb.OpenMode.kForRead)
        (status, blk_record) = blk_table.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForWrite)
        blk_table.close()

        circle_1 = GcDbCircle(GcGePoint3d(1, 1, 1), GcGeVector3d(0, 0, 1), 1.0)
        circle_2 = GcDbCircle(GcGePoint3d(4, 4, 4), GcGeVector3d(0, 0, 1), 1.0)

        blk_record.appendGcDbEntity(circle_1)
        circle_1.close()

        blk_record.appendGcDbEntity(circle_2)
        circle_2.close()

        blk_record.close()

        status = database.saveAs(file_path)
        if status != Gcad.eOk:
            gcedPrompt("\n[CREATE] 文件保存失败")
        else:
            gcedPrompt("\n[CREATE] 文件保存成功(%s)" % file_path)
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyRead():
    try:
        database = GcDbDatabase(False, False)

        if database.readDwgFile(file_path) != Gcad.eOk:
            gcedPrompt("\n[READ] 文件读取失败")
            return

        status, blk_table = database.getBlockTable(GcDb.OpenMode.kForRead)
        status, blk_record = blk_table.getAt(GCDB_MODEL_SPACE, GcDb.OpenMode.kForRead)
        blk_table.close()
        status, iterator = blk_record.newIterator()

        iterator.start()
        print("#1")
        while not iterator.done():
            print("##2")
            (status, entity) = iterator.getEntity()
            gcutPrintf("classname:%s\n" % (entity.isA().name()))
            iterator.step()
    except Exception as err:
        gcutPrintf("[ERROR]:%s" % err)
