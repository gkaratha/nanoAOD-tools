import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class branchImporter(Module):

    def __init__(self,collectionSrc,idx,output, branches=None,collectionFetched=None):
        self.collectionSrc = collectionSrc
        self.idx=idx
        self.output = output
        self.branches = branches
        self.collectionFetched = collectionFetched
        self.branchType = {}
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for br in self.branches:    
            self.out.branch("%s_%s"%(self.output,br), _rootLeafType2rootBranchType['Double_t'], lenVar="n%s"%self.output)


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
        collSrc = Collection(event,self.collectionSrc)

        # collection to fetch branches from
        collFetch = Collection(event,self.collectionFetched)
        
        # fill branched 
        for j in self.branches:
          out = []
          for obj in collSrc:
             Idx=getattr(obj,self.idx)
             out.append(getattr(collFetch[Idx],j))
          self.out.fillBranch("%s_%s"%(self.output,j),out)
        return True

