from pygcad.core import *
from pygcad.pygrx import *

@command()
def PyDeepClone():
    try:
        ent = gds_name()
        pt = gds_point()
        es = gcedEntSel("select a block to deepclone:",ent,pt)
        if es != RTNORM:
            gcutPrintf("\n select error.\n")
            return
        
        entId = GcDbObjectId()
        gcdbGetObjectId(entId, ent)

        es, pBlockTable = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.kForRead)

        es,MsId= pBlockTable.getObjIdAt(GCDB_MODEL_SPACE, False)
        pBlockTable.close()

        ids = GcDbObjectIdArray()
        ids.append(entId)

        tempMap = GcDbIdMapping()
        es,idMapList = gcdbHostApplicationServices().workingDatabase().deepCloneObjects(ids,MsId,tempMap,False)
        if es == 0:
            gcutPrintf("\n deepclone success.\n")
        else:
            gcutPrintf("\n deepclone failed. \n")
            return
        
        for pairNode in idMapList:
            gcutPrintf(" \n origineID is %d ," % pairNode[0])
            gcutPrintf(" clonedID is %d \n" % pairNode[1])

    except Exception as err:
        gcutPrintf("\n deepclone failed. \n")
        gcedPrompt("\n error is %s \n" % err)