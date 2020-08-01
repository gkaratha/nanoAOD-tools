import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import itertools
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class genTriggerMuon(Module):

    def __init__(self, trgBranch, skipNoTrgEvt, skipProbe, skipTag, selectionPathList=[], outputColl="Trg", recoIdx=[], trgMuMinPt=None, branches=None):
        self.trgBranch = trgBranch
        self.skipNoTrgEvt = skipNoTrgEvt
        self.skipProbe = skipProbe
        self.skipTag = skipTag
        self.selectionPathList = selectionPathList
        self.outputColl = outputColl
        self.recoIdx = recoIdx
        self.trgMuMinPt = trgMuMinPt
        self.branches = branches
 
        self.trgColl= self.trgBranch.split("_")[0]
        self.trgBranch= self.trgBranch.split("_")[1]
        self.recoColl=[clx.split("_")[0] for clx in  self.recoIdx ]
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for br in self.branches:
          self.out.branch("%s_%s"%(self.outputColl,br), _rootLeafType2rootBranchType['Double_t'], lenVar="n%s"%self.outputColl)
        for col in self.recoColl:
          self.out.branch("%s_%s"%(col,"isTrg"),'I')

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""               
        trgObjects = Collection(event,self.trgColl)
        if self.trgMuMinPt!=None and self.trgMuMinPt>0:
           trgObjIdx = [ idx for idx,trg in enumerate(trgObjects) if getattr(trg,"pt")>self.trgMuMinPt and getattr(trg,self.trgBranch)==1]
         
        else:
           trgObjIdx = [ idx for idx,trg in enumerate(trgObjects) if getattr(trg,self.trgBranch)==1]
        
        
        if len(trgObjIdx)==0 and self.skipNoTrgEvt: 
           return False

        passedPath= [ path for path in self.selectionPathList if getattr(event,path)]
        if len(self.selectionPathList)>0 and len(passedPath)==0:
           if self.skipNoTrgEvt:
              return False
           trgObjIdx=[]
        if len(trgObjIdx)==0:
          for br in self.branches:
            self.out.fillBranch("%s_%s"%(self.outputColl,br),[])
          for col in self.recoColl:
            self.out.fillBranch("%s_isTrg"%(col),0)
          if self.skipProbe or self.skipTag:
             return False
        else:
          Bmu_fired=0
  #        print trgObjIdx
          for idx,col in zip(self.recoIdx,self.recoColl):
            out=getattr(event,idx)
            if out in trgObjIdx:
               self.out.fillBranch("%s_isTrg"%(col),1)
               Bmu_fired+=1
            else:
               self.out.fillBranch("%s_isTrg"%(col),0)

          if Bmu_fired==0 and self.skipProbe: 
            return False     
          if Bmu_fired>0 and Bmu_fired==len(trgObjIdx) and self.skipTag:
            return False
          
          for br in self.branches:
            out=[ getattr(trgObjects[idx],br) for idx in trgObjIdx ]
            self.out.fillBranch("%s_%s"%(self.outputColl,br),out)
        return True
