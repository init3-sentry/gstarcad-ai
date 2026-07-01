"""
Description:

This program demonstrates iterating over a symbol table.
Specifically the linetype table.

1. APPLOAD tbliter.py
2. 执行命令PyIterLineTypes，程序会打印出当前图纸空间支持的线性的名字
"""
from pygcad.core import *
from pygcad.pygrx import *
import time
# import debugpy
# import sys
import traceback
import socket

@command()
def PyIterLineTypes():
    try:
        # sys.executable='/home/cad/.pyenv/versions/3.6.9/bin/python3.6'
        # socket.setdefaulttimeout(60)
        # debugpy.configure(python=r'C:\Users\jxw\AppData\Local\Programs\Python\Python38\python3.exe')
        # debugpy.listen(5678)
        # debugpy.wait_for_client()
        # time.sleep(30)
        
        db = gcdbWorkingDatabase()
        _, obj = gcdbOpenObject(db.linetypeTableId(), GcDb.kForRead)
        tbl = GcDbLinetypeTable.cast(obj)
        inc_ref(tbl)
        gcutPrintf("##0")

        _,  iterator = tbl.newIterator()
        gcutPrintf("#0")
        iterator.start()
        while not iterator.done():
            # itor = GcDbLinetypeTableIterator.fromIter(iterator)
            gcutPrintf("#1")
            _, record = iterator.getRecord()
            gcutPrintf("#2")
            _, name = record.getName()
            gcutPrintf("#3")
            record.close()
            gcutPrintf("\nLinetype name is %s" % name)
            iterator.step()

        tbl.close()
    except Exception as err:
        gcutPrintf("\n[ERROR]: %s" % traceback.format_exc())
