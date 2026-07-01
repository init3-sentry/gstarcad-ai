"""
.. Description
一个利用Jig画线的程序

1. load linejig.py
2. 执行命令 PYLINEJIG, 按照命令提示分别选择 *开始点* 和 *结束点*
3. 命令执行结束

"""
import sys

from pygcad.core import *
from pygcad.pygrx import *


class LineJig(GcEdJig):
    def __init__(self, pt: GcGePoint3d):
        GcEdJig.__init__(self)

        self.startPt = pt
        self.endPt = pt + GcGeVector3d(100, 100, 0)
        self.line = GcDbLine(self.startPt, self.endPt)

    def sampler(self):
        status = GcEdJig.kNoChange
        pt = GcGePoint3d(self.endPt.x, self.endPt.y, self.endPt.z)
        status = self.acquirePoint(pt, self.startPt)
        if status != GcEdJig.kNormal:
            return status
        elif self.endPt == pt:
            return GcEdJig.kNoChange
        else:
            self.endPt = pt
            return status

    def update(self):
        self.line.setEndPoint(self.endPt)
        return True

    def entity(self):
        return self.line

    def doIt(self):
        self.setDispPrompt("\n请选择结束点:")
        self.drag()
        self.append(self.line)


@command()
def PyLineJig():
    try:
        gcedPrompt("\nLineJig Started..")
        pt1 = GcGePoint3d()
        gcedGetPoint(None, "\n选择开始点:", pt1)
        gcedPrompt("UCS:(%f,%f,%f)" % (pt1.x, pt1.y, pt1.z))

        res_from = resbuf()
        res_from.restype = RTSHORT
        res_from.resval = gds_u_val()
        res_from.resval.rint = 1

        res_to = resbuf()
        res_to.restype = RTSHORT
        res_to.resval = gds_u_val()
        res_to.resval.rint = 0
        gcedTrans(pt1, res_from, res_to, 0, pt1)
        gcedPrompt("WCS:(%f,%f,%f)" % (pt1.x, pt1.y, pt1.z))

        # gcedPrompt("(%f,%f,%f)" % (a[0], a[1], a[2]))
        jig = LineJig(pt1)
        jig.doIt()

    except Exception as err:
        gcedPrompt('---- [ERROR]: %s'%err)