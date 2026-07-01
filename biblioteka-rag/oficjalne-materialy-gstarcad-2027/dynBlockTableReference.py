from pygcad.core.runtime import *
from pygcad.pygrx import *

@command('PyDynPropTest')

def PyDynPropTest():
    try:
       # open the block table
       es,block_table = gcdbHostApplicationServices().workingDatabase().getBlockTable(GcDb.OpenMode.kForWrite)

        # open inner block table record: model space
       es,model_space_rec = block_table.getAt(GCDB_MODEL_SPACE,GcDb.OpenMode.kForWrite,False)

        # get the block named "asd" in the block table
       es,id = block_table.getObjIdAt("asd",False)
       block_table.close()

        # construct the block reference form "asd" block
       block_table_ref = GcDbBlockReference(GcGePoint3d(0,0,0),id)

       block_table_ref.setRotation(0.789)

         # insert the block reference in the model space
       es,ent_id = model_space_rec.appendGcDbEntity(block_table_ref)

       dyn_block_table_ref = GcDbDynBlockReference(block_table_ref.id())
       props = []
       props = dyn_block_table_ref.getBlockProperties()
       gcedPrompt("props.count is %d \n" % len(props))
       evalue = GcDbEvalVariant()
       for p in props:
           gcedPrompt("propertyName is %s \n" % p.propertyName().constPtr())
           if p.propertyName().constPtr() == "距离1":                                    
                evalue.setValue(GcDb.kDxfReal,200.00)
                p.setValue(evalue)             
           elif p.propertyName().constPtr() == "dimension X":
                evalue.setValue(GcDb.kDxfReal,300.00)
                p.setValue(evalue)    
           elif p.propertyName().constPtr() == "dimension Y":
                evalue.setValue(GcDb.kDxfReal,300.00)
                p.setValue(evalue)                 
       evalue.clear()
       block_table_ref.close()
       model_space_rec.close()
    except Exception as err:
        gcedPrompt("---------error is: %s \n" % err)