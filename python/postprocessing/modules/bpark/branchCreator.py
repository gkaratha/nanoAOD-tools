import ROOT
import numpy as np
import itertools
from math import sqrt
from PhysicsTools.HeppyCore.utils.deltar import deltaR

ROOT.PyConfig.IgnoreCommandLineOptions = True


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }




class branchCreator(Module):

    def __init__(self,collection,operation,inputBranches=None,createdBranches=None):
        self.collection = collection
        self.operation = operation
        self.inputBranches = inputBranches
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
            self.out.branch("%s_%s"%(self.collection,br), _rootLeafType2rootBranchType['Double_t'], lenVar="n%s"%self.collection)


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
        # collection based on which we fetch branches in the other collection
        coll = Collection(event,self.collection)

#        for branches in self.inputBranches:
       
        for ioutvar,outvar in enumerate(self.inputBranches):
          out=[]
          for obj in coll:   
            var= [getattr(obj,branch) for branch in outvar]
            num=0.0
            try:
              num=eval(self.operation[ioutvar].format(*var))
            except ZeroDivisionError:
              num=-99.0
            out.append(num)

          self.out.fillBranch("%s_%s"%(self.collection,self.createdBranches[ioutvar]),out)

        return True

