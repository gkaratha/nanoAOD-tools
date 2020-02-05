import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


class compositeRecoMatcher(Module):

    def __init__(self, compositeColl, lepCompositeIdxs, hadronCompositeIdxs, lepMatchedRecoIdxs, hadronMatchedRecoIdxs, outputColl, branches=None):
        self.compositeColl = compositeColl
        self.lepCompositeIdxs = lepCompositeIdxs
        self.hadronCompositeIdxs = hadronCompositeIdxs
        self.lepMatchedRecoIdxs = lepMatchedRecoIdxs
        self.hadronMatchedRecoIdxs = hadronMatchedRecoIdxs
        self.branches = branches
        self.outputColl = outputColl
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for br in self.branches:    
          self.out.branch("%s_%s"%(self.outputColl,br),'F')


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
               
        compColl = Collection(event,self.compositeColl)
        lepMatchIdxs = [ getattr(event,idx) for idx in  self.lepMatchedRecoIdxs ]
        hdrMatchIdxs = [ getattr(event,idx) for idx in  self.hadronMatchedRecoIdxs ]

        recoB=None;
        for obj in compColl:        
          Blep = [ getattr(obj,br) for br in self.lepCompositeIdxs ]
          Bhad = [ getattr(obj,br) for br in self.hadronCompositeIdxs ]
          if set(Blep) == set(lepMatchIdxs) and set(Bhad) == set(hdrMatchIdxs):
            recoB=obj
        
    
        if recoB == None:
          for br in self.branches:
            self.out.fillBranch("%s_%s"%(self.outputColl,br),-99)
        else:  
         for br in self.branches:
           out=getattr(recoB,br)
           self.out.fillBranch("%s_%s"%(self.outputColl,br),out)

        return True

