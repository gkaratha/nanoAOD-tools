import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class branchRemover(Module):

    def __init__(self, branchesToRemove=[]):
        self.branchesToRemove = branchesToRemove
        self.branchType = {}
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass



    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        for br in self.branchesToRemove:
           branch=event._tree.GetBranch(br)
           event._tree.GetListOfBranches().Remove(branch)
           event._tree.Write()
        return True

