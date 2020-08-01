import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


class compositeRecoMatcher(Module):

    def __init__(self, compositeColl, lepCompositeIdxs, hadronCompositeIdxs, lepMatchedRecoIdxs, hadronMatchedRecoIdxs, outputColl,cuts_vars,cuts,branches=None,sortTwoLepByIdx=False,lepLabelsToSort=[]):
        self.compositeColl = compositeColl
        self.lepCompositeIdxs = lepCompositeIdxs
        self.hadronCompositeIdxs = hadronCompositeIdxs
        self.lepMatchedRecoIdxs = lepMatchedRecoIdxs
        self.hadronMatchedRecoIdxs = hadronMatchedRecoIdxs
        self.cuts_vars = cuts_vars
        self.cuts = cuts
        self.branches = branches
        self.outputColl = outputColl
        self.sortTwoLepByIdx = sortTwoLepByIdx
        self.lepLabelsToSort = lepLabelsToSort
        pass
        if self.sortTwoLepByIdx and len(self.lepLabelsToSort)!=2:
          print "ERROR: provide exactly two labels of leptons for sorting or remove the option. Instead found ",lepLabelsToSort
          exit()

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

        # for lep sorting
        if self.sortTwoLepByIdx:
           realLabel_L=[self.lepLabelsToSort[0], self.lepLabelsToSort[1]]
        
        recoB=None;
        for obj in compColl:        
          Blep = [ getattr(obj,br) for br in self.lepCompositeIdxs ]          
          Bhad = [ getattr(obj,br) for br in self.hadronCompositeIdxs ]
          if set(Blep) == set(lepMatchIdxs) and set(Bhad) == set(hdrMatchIdxs):
            recoB=obj
            # actual sorting
            if self.sortTwoLepByIdx and lepMatchIdxs[0] == Blep[1]:
              realLabel_L[0], realLabel_L[1] = realLabel_L[1], realLabel_L[0]
              sortlepIdx=[Blep[1], Blep[0]]
            elif self.sortTwoLepByIdx: sortlepIdx= [Blep[0], Blep[1]]  
            
        #apply cuts
        if len(self.cuts_vars)>0 and recoB!=None:
           cut_values = [ getattr(event,ct) for ct in self.cuts_vars ]
           if not eval(self.cuts.format( *cut_values ) ):
             recoB=None
        
        if recoB == None:
          for br in self.branches:
            self.out.fillBranch("%s_%s"%(self.outputColl,br),-99)

        else: 
         
          for br in self.branches:
            out=getattr(recoB,br)
            #sort stuff
            outputName=br
            if self.sortTwoLepByIdx:
              for ileb,leb in enumerate(self.lepLabelsToSort):
                if leb+"_" in br: 
                  new_br = br.split("_")
                  new_br[new_br.index(leb)] = realLabel_L[ileb]
                  outputName="_".join(new_br)
              if br in self.lepCompositeIdxs:
                out=sortlepIdx[self.lepCompositeIdxs.index(br)]
            self.out.fillBranch("%s_%s"%(self.outputColl,outputName),out)
           
        return True
