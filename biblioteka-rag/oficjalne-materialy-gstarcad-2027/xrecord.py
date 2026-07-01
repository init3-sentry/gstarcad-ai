from pygcad.core import *
from pygcad.pygrx import *


def createXrecord():
    es, pNamedobj = gcdbHostApplicationServices().workingDatabase().getNamedObjectsDictionary(GcDb.OpenMode.kForWrite)
    st, pDict = pNamedobj.getAt("ASDK_DICT", GcDb.OpenMode.kForWrite)

    if st == Gcad.ErrorStatus.eKeyNotFound:
        _, DictId = pNamedobj.setAt("ASDK_DICT",pDict)
    pNamedobj.close()

    ptmpDict = GcDbDictionary.cast(pDict)
    pXrec = GcDbXrecord()
    _, xrecObjId = ptmpDict.setAt("XREC1", pXrec)
    pDict.close()

    testpt = {1.0, 2.0, 0.0}
    pHead = gcutBuildList(1, "This is a test Xrecord list", 10, testpt, 40, 3.14159, 50, 3.14159, 62, 1, 70, 180)

    pXrec.setFromRbChain(pHead)

    gcutRelRb(pHead)
    pXrec.close()


def listXrecord():
    es, pNamedobj = gcdbHostApplicationServices().workingDatabase().getNamedObjectsDictionary(GcDb.OpenMode.kForRead)
    _, pDict = pNamedobj.getAt("ASDK_DICT", GcDb.OpenMode.kForRead)
    pNamedobj.close()

    ptmpDict = GcDbDictionary.cast(pDict)
    _, pXrec = ptmpDict.getAt("XREC1", GcDb.OpenMode.kForRead)
    ptmpDict.close()

    ptmpXrec = GcDbXrecord.cast(pXrec)
    _, pRbList = ptmpXrec.rbChain()
    ptmpXrec.close()

    printList(pRbList)
    gcutRelRb(pRbList)


def printList(pBuf):
    i = 0
    rt = 0
    while pBuf is not None:
        if pBuf.restype < 0:
            rt = pBuf.restype
        elif pBuf.restype < 10:
            rt = RTSTR
        elif pBuf.restype < 38:
            rt = RT3DPOINT
        elif pBuf.restype < 60:
            rt = RTREAL
        elif pBuf.restype < 80:
            rt = RTSHORT
        elif pBuf.restype < 100:
            rt = RTLONG
        elif pBuf.restype < 106:
            rt = RTSTR
        elif pBuf.restype < 148:
            rt = RTREAL
        elif pBuf.restype < 290:
            rt = RTSHORT
        elif pBuf.restype < 330:
            rt = RTSTR
        elif pBuf.restype < 370:
            rt = RTENAME
        elif pBuf.restype < 999:
            rt = RT3DPOINT
        else:
            rt = pBuf.restype

        if rt == RTSHORT:
            if pBuf.restype == RTSHORT:
                gcutPrintf("RTSHORT: %d\n" % pBuf.resval.rint)
            else:
                gcutPrintf("(%d . %d)\n" % (pBuf.restype, pBuf.resval.rint))
        elif rt == RTREAL:
            if pBuf.restype == RTREAL:
                gcutPrintf("RTREAL : %0.3f\n" % pBuf.resval.rreal)
            else:
                gcutPrintf("(%d . %0.3f)\n" % (pBuf.restype, pBuf.resval.rreal))
        elif rt == RTSTR:
            if pBuf.restype == RTSTR:
                gcutPrintf("RTSTR : %s\n" % pBuf.resval.rstring)
            else:
                gcutPrintf("(%d . %s)\n" % (pBuf.restype, pBuf.resval.rstring))
        elif rt == RT3DPOINT:
            if pBuf.restype == RT3DPOINT:
                gcutPrintf("RT3DPOINT : %0.3f, %0.3f, %0.3f\n" % pBuf.resval.rstring)
            else:
                gcutPrintf("(%d . %s)\n" % (pBuf.restype, pBuf.resval.rstring))
        elif rt == RTLONG:
            gcutPrintf("RTLONG: %dl\n" % pBuf.resval.rlong)

        pBuf = pBuf.rbnext
        i += 1



@command()
def PyCreateXrecord():
    try:
        createXrecord()
    except Exception as err:
        gcedPrompt("%s" % err)


@command()
def PyListXrecord():
    try:
        listXrecord()
    except Exception as err:
        gcedPrompt("%s" % err)
