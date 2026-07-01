"""
...Description:

    This program demonstrates the use of some of the AcDbGroup protocol. It first prompts the user to select some entities
    that are placed into a group called "ASDK_GROUPTEST". Then it calls the function removeAllButLines() to iterate over
    the group and remove all the entities that are not lines. Finally, it changes the remaining entities in the group
    to red.

    To use groups.arx:
    1. Start AutoCAD and open a new drawing.
    2. Create a number of entities, making sure to include some lines, circles, and arcs.
    3. Type the ARX command and load groups.arx.
    4. Type the GROUPTST command, defined by groups.arx. Make a selection set that includes at least one line.
    5. Verify the contents of the group by executing the GROUP command. In the 'Object Grouping' dialog click on the name
    of the group ASDK_GROUPTEST in the Group_Name listbox at the top of the dialog. Next, click the 'Highlight' button to
    highlight the members of the group (this will be a standard dashed-linetype highlight).  Notice that only the red lines
    in the group are highlighted.  Click the Continue button, then exit the Object Grouping dialog by clicking Cancel.

"""

from pygcad.core import *
from pygcad.pygrx import *
import pysnooper


def groups():
    pGroup = GcDbGroup("grouptest")
    es, pGroupDict = gcdbHostApplicationServices(
    ).workingDatabase().getGroupDictionary(GcDb.kForWrite)

    es, groupId = pGroupDict.setAt("ASDK_GROUPTEST", pGroup)
    pGroupDict.close()
    pGroup.close()

    makeGroup(groupId)
    removeAllButLines(groupId)


def makeGroup(groupId: GcDbObjectId):
    sset = gds_name()
    err = gcedSSGet(None, None, None, None, sset)
    if err != RTNORM:
        return

    pGroup = None
    es, pObj = gcdbOpenObject(groupId, GcDb.kForWrite)
    if pObj.isKindOf(GcDbGroup.desc()):
        pGroup = GcDbGroup.cast(pObj)

    ret, length = gcedSSLength(sset)
    entId = GcDbObjectId()
    ename = gds_name()
    for i in range(length):
        gcedSSName(sset, i, ename)
        gcdbGetObjectId(entId, ename)
        pGroup.append(entId)

    pGroup.close()
    gcedSSFree(sset)


@pysnooper.snoop(output=gcutPysnooperDefaultOutput(__file__), prefix='removeAllButLines_debug: ')
def removeAllButLines(groupId: GcDbObjectId):
    es, pGroup = gcdbOpenObject(groupId, GcDb.kForWrite)
    pIter = pGroup.newIterator()

    while not pIter.done():
        (status, pObj) = pIter.getObject(GcDb.kForRead)
        if pObj.isKindOf(GcDbLine.desc()):
            pObj.close()
            pGroup.remove(pIter.objectId())
        else:
            pObj.close()
        pIter.next()

    pGroup.setColorIndex(1)
    pGroup.close()


@command()
def pyGROUPTEST():
    groups()
