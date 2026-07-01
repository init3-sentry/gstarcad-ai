"""
...Description:
    一个测试选择集相关功能的程序

    1. APPLOAD entsel.py
    2. 执行命令 PyEraseAll，会删除图形空间中的所有实体；
    3. 执行命令 PyGetPoint，会获取一个用户输入的一个坐标点，并打印；
"""

from pygcad.core import *
from pygcad.pygrx import *


@command()
def PyEraseAll():
    try:
        s_name = gds_name()
        gcedSSGet('A', None, None, None, s_name)
        (status, length) = gcedSSLength(s_name)
        gcedPrompt("rt=%d, length=%d" % (status, length))
        if status != RTNORM or length <= 0:
            gcedPrompt("\n没有选中任何实体!")
            gcedSSFree(s_name)
            return

        ent_name = gds_name()
        ent_id = GcDbObjectId()
        for i in range(length):
            gcedSSName(s_name, i, ent_name)
            gcdbGetObjectId(ent_id, ent_name)
            (status, entity) = gcdbOpenGcDbEntity(ent_id, GcDb.kForWrite, False)
            entity.erase()
            entity.close()

        gcedSSFree(s_name)

    except Exception as err:
        gcedPrompt('---- [ERROR]: %s' % err)


@command()
def PyGetGdsPoint():
    try:
        pt = gds_point()
        status = gcedGetPoint(None, "\n请选择点:", pt)
        gcedPrompt("%s" % pt)
    except Exception as err:
        gcedPrompt('---- [ERROR]: %s' % err)
