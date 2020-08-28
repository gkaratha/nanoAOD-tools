import ROOT
import numpy as np
import itertools
import importlib


ROOT.PyConfig.IgnoreCommandLineOptions = True


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }




class functionWrapper(Module):

    def __init__(self,functionName,collections=[],createdBranches=[],nCol=None):
        self.functionName = functionName
        self.collections = collections
        self.createdBranches = createdBranches
        self.nCol = nCol
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if self.nCol != None:
           for br in self.createdBranches:    
              self.out.branch(br, _rootLeafType2rootBranchType['Double_t'], lenVar=self.nCol)
        else:
            for br in self.createdBranches:
               self.out.branch(br,'F')
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass



    '''def filterBranchNames(self,branches,collection):
        out = []
        for br in branches:
            name = br.GetName()
            if not name.startswith(collection+'_'): continue
            out.append(name.replace(collection+'_',''))
            self.branchType[out[-1]] = br.FindLeaf(br.GetName()).GetTypeName()
        return out'''


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        # collection based on which we fetch branches in the other collection
        colls=[]
        for icol in self.collections:
          try:
            x=Collection(event,icol)
          except RuntimeError:
            x=getattr(event,icol)
          colls.append(x)
        
#        mod= importlib.import_module("CMGTools.RKAnalysis.tools.nanoAOD.UserFunctions")
        from CMGTools.RKAnalysis.tools.nanoAOD.UserFunctions import *
        outvars = eval(self.functionName)(colls)
        for ioutvar,outvar in enumerate(outvars):
           #for mbr in outvar:
           self.out.fillBranch(self.createdBranches[ioutvar],outvar)

        return True

