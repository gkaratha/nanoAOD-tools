import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class collectionSkimmer(Module):

    def __init__(self,input,output,branches, #mandatory imputs
                 TriggerMuonId=None,  # excludes triggering muon from B
                 selectTagMuons=None,  # selects only the triggering muon from B
                 sortOutput=False, # output B will be sorted if True
                 sortkey = lambda x : x.pt, # variable to sort
                 reverse=True, # ascending or desceding order
                 selector=lambda l:True, # cuts
                 maxObjects=-1, # number of max evts
                 importedVariables = [],
                 varnames = [],
                 importIds = [],
                 flat = False
                ):
        self.input = input
        self.output = output
        self.nInputs = len(self.input)
        self.branches = branches
        self.sortkey = lambda obj : sortkey(obj)
        self.reverse = reverse
        self.TriggerMuonId = TriggerMuonId
        self.selectTagMuons = selectTagMuons
        self.maxObjects = maxObjects
        self.selector = selector
        self.sortOutput = sortOutput
        self.importedVariables = importedVariables
        self.varnames = varnames
        self.importIds = importIds
        self.flat = flat
        self.branchType = {}
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        self.is_there = np.zeros(shape=(len(self.branches),self.nInputs),dtype=bool)
        for bridx,br in enumerate(self.branches):
          if br in self.branches: self.is_there[bridx]=True

        self.out = wrappedOutputTree
        if not self.flat:
          for br in self.branches:
            self.out.branch("%s_%s"%(self.output,br), _rootLeafType2rootBranchType['Double_t'], lenVar="n%s"%self.output)
        else:
          for br in self.branches:
            self.out.branch("%s_%s"%(self.output,br), _rootLeafType2rootBranchType['Double_t'],lenVar="n%s"%self.output)

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
        # read objects
        objects = Collection(event,self.input)

        # add variables from other collections
        if self.importedVariables != "None":
          cols = [ (Collection(event, (var.split("_"))[0] ), (var.split("_"))[1], i )  for i,var in enumerate(self.importedVariables) ]
          for col, var, ivar in cols:
            varname = self.varnames[ivar]
            idx = self.importIds[ivar]
            for obj in objects:
              value=getattr( col[ getattr(obj, idx) ], var )
              setattr(obj, varname, value)

        # apply cuts
        objects = filter( self.selector, objects)         
        '''# remove trigger bias
        if not self.exclTriggerMuonId == None:
           fltrobj = []
           trgIds = Collection(event, ( self.exclTriggerMuonId.split("_") )[0] )
           trg_br = ( self.exclTriggerMuonId.split("_") )[1]
           for trg in trgIds:
             trgIdx = getattr( trg, trg_br )
             for obj in objects:
               if obj.l1Idx !=trgIdx and obj.l2Idx !=trgIdx:
                  fltrobj.append(obj)
           objects=fltrobj

        # sel only trigger muons
        if not self.selTriggerMuonId == None:
           fltrobj = []
           trgIds = Collection(event, ( self.selTriggerMuonId.split("_") )[0] )
           trg_br = ( self.selTriggerMuonId.split("_") )[1]
           for trg in trgIds:
             trgIdx = getattr( trg, trg_br )
             for obj in objects:
               if obj.l1Idx ==trgIdx or obj.l2Idx == trgIdx:
                  fltrobj.append(obj)
           objects=fltrobj'''
        if self.TriggerMuonId != None and self.selectTagMuons!=None: 
           fltrobj = []
           trgIds = Collection(event, ( self.TriggerMuonId.split("_") )[0] )
           trg_br = ( self.TriggerMuonId.split("_") )[1]
           trg_results = [ itrg for itrg,trg in enumerate(trgIds)  if getattr( trg, trg_br )==1]
           for iobj,obj in enumerate(objects):
             if self.selectTagMuons==True:
               if (obj.l1Idx in trg_results) or (obj.l2Idx in trg_results):
                  fltrobj.append(obj)
             elif self.selectTagMuons==False:
               ntrg=0
               if obj.l1Idx in trg_results: ntrg+=1;
               if obj.l2Idx  in trg_results: ntrg+=1;
               if ntrg < len(trg_results): 
                  fltrobj.append(obj)
           objects=fltrobj    
        if (self.TriggerMuonId == None and self.selectTagMuons!=None) or (self.TriggerMuonId != None and self.selectTagMuons==None):
           print "problem with tag/probe or triggering ID"

        if len(objects)==0: return False
        # sort
        if self.sortOutput:
           objects.sort (key = self.sortkey, reverse = self.reverse)

        # reduce number
        if self.maxObjects>0 and self.maxObjects<len(objects): 
           objects = objects[:self.maxObjects]

        # fill branches
        if not self.flat:
           for br in self.branches:
              out = []
              for obj in objects:
                 out.append(getattr(obj,br))
              self.out.fillBranch("%s_%s"%(self.output,br), out)
        else:
           for obj in objects:
             for br in self.branches:
               out=[getattr(obj,br)]
               self.out.fillBranch("%s_%s"%(self.output,br), out)
             self.out.fill()
           return False  

        return True
      
