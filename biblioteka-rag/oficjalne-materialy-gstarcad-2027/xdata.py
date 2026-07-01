"""
Description:

This program demonstrates the use of the GcDBObject Xdata
member functions.

1. APPLOAD xdata.py
2. 绘制任意一个实体；
3. 执行命令PyAddXdata, 根据提示先选择一个实体，然后分别输入要添加的xdata的application name(如"test")和值(如"hello");
4. 执行命令PyPrintXdata，根据提示选择之前添加的xdata的哪个实体，然后输入之前设置的application name(如"test")，
这时程序会打印出之前添加的xdata的值，期望结果为hello
"""

from pygcad.core import *
from pygcad.pygrx import *

kDxfXdAsciiString = 1000
kDxfRegAppName = 1001


def select_object(mode):
    en = gds_name()
    pt = gds_point()
    gcedInitGet(RSG_OTHER, "HANDLE _Handle")
    ss = gcedEntSel("Select an Entity or "
                    "enter 'H' to enter its handle", en, pt)

    ent_valid = False
    if ss == RTNORM:
        ent_valid = True
    elif ss == RTKWORD:
        (tmp_ss, handle_str) = gcedGetString(0, "Enter valid object handle")
        if tmp_ss == RTNORM:
            if gcdbHandEnt(handle_str, en) == RTNORM:
                ent_valid = True

    if not ent_valid:
        gcutPrintf("Nothing Selected, Return Code==%d\n" % ss)
        return None

    ent_id = GcDbObjectId()
    ret_stat = gcdbGetObjectId(ent_id, en)
    if ret_stat != Gcad.eOk:
        gcutPrintf("\ngcdbGetObjectId failed")
        gcutPrintf("\nen==(%dl,%dl), retstat==%d" % (en[0], en[1], ret_stat))
        return None

    (ret_stat, obj) = gcdbOpenObject(ent_id, mode)

    if isinstance(obj, GcDbCircle):
        gcutPrintf("[DEBUG]: Yes!! It is Circle")

    if ret_stat != Gcad.eOk:
        gcutPrintf("\ngcdbGetObjectId failed")
        gcutPrintf("\nen==(%dl,%dl), retstat==%d" % (en[0], en[1], ret_stat))
        return None

    return obj


def print_list(p_rb):
    i = 0
    rt = 0
    while p_rb is not None:
        if p_rb.restype < 1010:
            rt = RTSTR
        elif p_rb.restype < 1040:
            rt = RT3DPOINT
        elif p_rb.restype < 1060:
            rt = RTREAL
        elif p_rb.restype < 1071:
            rt = RTSHORT
        elif p_rb.restype == 1071:
            rt = RTLONG
        else:
            rt = p_rb.restype

        if rt == RTSHORT:
            if p_rb.restype == RTSHORT:
                gcutPrintf("RTSHORT: %d\n" % p_rb.resval.rint)
            else:
                gcutPrintf("(%d . %d)\n" % (p_rb.restype, p_rb.resval.rint))
        elif rt == RTREAL:
            if p_rb.restype == RTREAL:
                gcutPrintf("RTREAL: %.3f\n" % p_rb.resval.rreal)
            else:
                gcutPrintf("(%d . %.3f)\n" % (p_rb.restype, p_rb.resval.rreal))
        elif rt == RTSTR:
            if p_rb.restype == RTSTR:
                gcutPrintf("RTSTR: %s\n" % p_rb.resval.rstring)
            else:
                gcutPrintf("(%d . %s)\n" % (p_rb.restype, p_rb.resval.rstring))
        # if rt == RT3DPOINT:
        #     if p_rb.restype == RT3DPOINT:
        #         gcutPrintf("RT3DPOINT: (%.3f, %.3f, %.3f)\n" % p_rb.resval.rpoint)
        #     else:
        #         gcutPrintf("(%d . %d)\n" % (p_rb.restype, p_rb.resval.rint))
        elif rt == RTLONG:
            gcutPrintf("RTLONG: %dl\n" % p_rb.resval.rlong)

        # next turn
        p_rb = p_rb.rbnext
        i += 1


def print_x_data():
    name = gds_name()
    pt = GcGePoint3d()
    p_obj = select_object(GcDb.kForRead)
    if p_obj is None:
        return

    (status, app_name) = gcedGetString(0, "\nEnter the desired Xdata application name: ")
    if status != RTNORM:
        return

    p_rb = p_obj.xData(app_name)
    # p_rb = p_obj.xData()
    if p_rb is not None:
        print_list(p_rb)
        gcutRelRb(p_rb)
    else:
        gcutPrintf("\nNo xdata for this appname")

    p_obj.close()


def add_x_data():
    p_obj = select_object(GcDb.kForRead)
    (status, app_name) = gcedGetString(0, "Enter application name: ")
    (status, res_str) = gcedGetString(0, "Enter string to be added: ")

    p_rb = p_obj.xData(app_name)
    p_tmp = p_rb
    if p_rb is not None:
        while p_tmp.rbnext is not None:
            p_tmp = p_tmp.rbnext
    else:
        gcdbRegApp(app_name)

        # p_rb = gcutNewRb(GcDb.kDxfRegAppName)
        p_rb = gcutNewRb(kDxfRegAppName)
        p_tmp = p_rb
        # DEBUG: 字符串拷贝？
        p_tmp.resval.rstring = app_name

    # gcutNewRb(AcDb::kDxfXdAsciiString)
    p_tmp.rbnext = gcutNewRb(kDxfXdAsciiString)
    p_tmp = p_tmp.rbnext
    p_tmp.resval.rstring = res_str

    p_obj.upgradeOpen()
    p_obj.setXData(p_rb)

    p_obj.close()
    gcutRelRb(p_rb)


@command()
def PyPrintXdata():
    try:
        print_x_data()
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyAddXdata():
    try:
        add_x_data()
    except Exception as err:
        gcedPrompt("%s" % err)
