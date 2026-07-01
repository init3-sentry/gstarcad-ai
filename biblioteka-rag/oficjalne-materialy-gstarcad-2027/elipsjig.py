"""
..Description:
    提供一个Jig接口实现椭圆的绘制
"""

from pygcad.core.runtime import *
from pygcad.pygrx import *
import traceback


class EllipseJig(GcEdJig):
    def __init__(self, center: GcGePoint3d, normal: GcGeVector3d):
        GcEdJig.__init__(self)

        self._ellipse = GcDbEllipse()
        self._center_pt = center
        self._normal = normal
        self._radius_ratio = 0.0001
        self._prompt_counter = 0
        self._axis_pt = GcGePoint3d()

        self.tmp_pt = GcGePoint3d()
        self.tmp_ratio = 0.0001

        rb = resbuf()
        gcedGetVar("VIEWSIZE", rb)
        major_axis_init_offset = rb.resval.rreal / 1000.0
        self._major_axis = GcGeVector3d(major_axis_init_offset, 0, 0)

    def sampler(self):
        status = GcEdJig.kNormal

        input_flags = GcEdJig.UserInputControls.kAccept3dCoordinates \
                      | GcEdJig.UserInputControls.kNoNegativeResponseAccepted \
                      | GcEdJig.UserInputControls.kNoZeroResponseAccepted
        self.setUserInputControls(GcEdJig.UserInputControls(input_flags))

        if self._prompt_counter == 0:
            status = self.acquirePoint(self._axis_pt, self._center_pt)
            if not self._axis_pt.isEqualTo(self.tmp_pt):
                self.tmp_pt = GcGePoint3d(self._axis_pt.x, self._axis_pt.y, self._axis_pt.z)
            elif status != GcEdJig.kNormal:
                return GcEdJig.kNoChange

        elif self._prompt_counter == 1:
            status, self._radius_ratio = self.acquireDist(self._center_pt)
            if self.tmp_ratio != self._radius_ratio:
                self.tmp_ratio = self._radius_ratio
            elif status != GcEdJig.kNormal:
                return GcEdJig.kNoChange

        return status

    def update(self):
        if self._prompt_counter == 0:
            self._major_axis = self._axis_pt - self._center_pt
        elif self._prompt_counter == 1:
            self._radius_ratio = self._radius_ratio / self._major_axis.length()

        self._ellipse.set(self._center_pt, self._normal, self._major_axis, self._radius_ratio)
        return True

    def entity(self):
        return self._ellipse

    def doIt(self):
        self._ellipse.set(self._center_pt, self._normal, self._major_axis, self._radius_ratio)
        self.setDispPrompt("\nEllipse major axis: ")
        status = self.drag()

        self._prompt_counter += 1
        self.setDispPrompt("\nEllipse minor axis: ")
        status = self.drag()
        self.append(self._ellipse)


def createEllipse():
    tmp_pt = GcGePoint3d()
    gcedGetPoint(None, "\nEllipse center point: ", tmp_pt)

    rb_from = resbuf()
    rb_to = resbuf()
    rb_from.restype = RTSHORT
    rb_from.resval.rint = 1
    rb_to.restype = RTSHORT
    rb_to.resval.rint = 0
    gcedTrans(tmp_pt, rb_from, rb_to, False, tmp_pt)

    x = gcdbWorkingDatabase().ucsxdir()
    y = gcdbWorkingDatabase().ucsydir()
    normal = x.crossProduct(y)
    normal.normalize()

    jig = EllipseJig(tmp_pt, normal)
    jig.doIt()


@command()
def PyEllipse():
    try:
        createEllipse()
    except Exception as err:
        gcutPrintf(traceback.format_exc())
