import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }



class collectionEmbeder(Module):

    def __init__(self, inputColl, embededColl, inputBranches, embededBranches, embededCollIdx):
        self.inputColl = inputColl
        self.embededColl = embededColl
        self.inputBranches = inputBranches
        self.embededBranches = embededBranches
        self.embededCollIdx = embededCollIdx
        self.branchType = {}
        pass


    def beginJob(self):
        pass


    def endJob(self):
        pass


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for br in self.embededBranches:
           self.out.branch("%s_%s"%(self.embededColl,br), _rootLeafType2rootBranchType['Double_t'], lenVar="n%s"%self.embededColl)
        pass

        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # read objects
        embededObjects = Collection(event,self.embededColl)
        inputObjects = Collection(event,self.inputColl)

        for inbr,embr in zip(self.inputBranches,self.embededBranches):
           out = []
           for obj in embededObjects:           
              idx = getattr(obj,self.embededCollIdx)
              out.append(getattr(inputObjects[idx],inbr))
           self.out.fillBranch("%s_%s"%(self.embededColl,embr), out)

        return True
      
