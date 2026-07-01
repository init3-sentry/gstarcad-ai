"""
...Description:
    一个测试图层相关操作的程序

    1. APPLOAD tablerec.py
    2. 执行命令PyAddLayer, 程序会创建一个名为"GSDK_TESTLAYER"的图层
"""

from pygcad.core import *
from pygcad.pygrx import *


def add_layer():
    status, layer_tbl = gcdbWorkingDatabase().getLayerTable(GcDb.kForWrite)

    if not layer_tbl.has("GSDK_TESTLAYER"):
        rcd = GcDbLayerTableRecord()
        rcd.setName("GSDK_TESTLAYER")
        rcd.setIsFrozen(0)
        rcd.setIsOff(0)
        rcd.setVPDFLT(0)
        rcd.setIsLocked(0)

        color = GcCmColor()
        color.setColorIndex(1)
        rcd.setColor(color)

        status, lt_tbl = gcdbWorkingDatabase().getLinetypeTable()
        status, lt_id = lt_tbl.getObjIdAt("DASHED")
        if status != Gcad.eOk:
            gcutPrintf("\nUnable to find DASHED linetype. Using CONTINUOUS")
            status, lt_id = lt_tbl.getObjIdAt("CONTINUOUS")
        lt_tbl.close()

        rcd.setLinetypeObjectId(lt_id)
        layer_tbl.add(rcd)
        rcd.close()
        layer_tbl.close()
    else:
        layer_tbl.close()
        gcutPrintf("\nlayer already exists")


@command()
def PyAddLayer():
    try:
        add_layer()
    except Exception as err:
        gcutPrintf("\n%s" % err)
        # trace_str = traceback.format_exc()
        # gcutPrintf("\n%s" % trace_str)

