import ROOT
import numpy as np
import itertools
from math import sqrt
from PhysicsTools.HeppyCore.utils.deltar import deltaR

ROOT.PyConfig.IgnoreCommandLineOptions = True


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }




class branchCreatorMC(Module):

    def __init__(self,inputBranches,operation,createdBranches):
        self.inputBranches = inputBranches
        self.operation = operation
        self.createdBranches = createdBranches
        self.branchType = {}
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for br in self.createdBranches:    
          self.out.branch(br,'F')


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass



    def filterBranchNames(self,branches,collection):
        out = []
        for br in branches:
            name = br.GetName()
            if not name.startswith(collection+'_'): continue
            out.append(name.replace(collection+'_',''))
            self.branchType[out[-1]] = br.FindLeaf(br.GetName()).GetTypeName()
        return out


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        
        for ioutvar,outvar in enumerate(self.inputBranches):
          invars = [getattr(event,vr) for vr in outvar]  
          num=0.0
          try:
            num=eval(self.operation[ioutvar].format(*invars))
          except ZeroDivisionError:
            num=-99.0        
          except ValueError:
            num=-99.0
          except NameError:
#             print num,ioutvar,outvar,invars
            num=-99.0
          if -99 in invars: 
             num=-99.0
          self.out.fillBranch(self.createdBranches[ioutvar],num)

        return True

