import ROOT
import numpy as np
import itertools
import os

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
_rootLeafType2rootBranchType = { 'UChar_t':'b', 'Char_t':'B', 'UInt_t':'i', 'Int_t':'I', 'Float_t':'F', 'Double_t':'D', 'ULong64_t':'l', 'Long64_t':'L', 'Bool_t':'O' }

class genDecayConstructor(Module):

    def __init__(self,momPdgId,daughtersPdgId,outputMomColl,outputDaughterColls,interDecay=[]):
        #super(genDecayConstructor,self).__init__()
        self.momPdgId= momPdgId
        self.daughtersPdgId = daughtersPdgId
        self.branches = ["pdgId","pt","eta","phi","mass"]                
        self.outputDaughterColls=outputDaughterColls
        self.outputMomColl = outputMomColl
        self.interDecay=interDecay
        #print "lib",ROOT.gSystem.GetLibraries()
        #if "/GenDecayCppWorker_cc.so" not in ROOT.gSystem.GetLibraries():
        if "mhtjuProducerCppWorker_cc.so" not in ROOT.gSystem.GetLibraries():
            print "Load C++ GenDecayCppWorker worker module"
            base = os.getenv("NANOAODTOOLS_BASE")
            if base:
                print "here1"
                #ROOT.gROOT.ProcessLine(".L %s/src/GenDecayCppWorker.cc+O"%base)
                ROOT.gROOT.ProcessLine(".L %s/src/mhtjuProducerCppWorker.cc+O"%base)
                
            else:
                print "here2"
                base = "%s/src/PhysicsTools/NanoAODTools"%os.getenv("CMSSW_BASE")
                print "base",base
                ROOT.gSystem.Load("libPhysicsToolsNanoAODTools.so")
#                ROOT.gROOT.ProcessLine(".L %s/interface/GenDecayCppWorker.h"%base)
                ROOT.gROOT.ProcessLine(".L %s/interface/mhtjuProducerCppWorker.h"%base)

        pass

    def beginJob(self):
 #       self.worker = ROOT.GenDecayCppWorker()
  #      self.worker.setMomId(self.momPdgId)
        for dpdgId in self.daughtersPdgId:
          momChain = 0
          for decay in self.interDecay:
         #    print decay
             decay = decay.split("->")
             mom = int( decay[0] ) 
             daughters = map(int,decay[1].split(","))
             for daughter in daughters:
               if int(daughter) != dpdgId: continue
               momChain = int(mom)
#          self.worker.setInterMomId(momChain) 
#          self.worker.setDaughterId(dpdgId)          
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        #super(genDecayConstructor,self).beginFile(inputFile, outputFile, inputTree, wrappedOutputTree)
        #self.initReaders(inputTree)
        self.out = wrappedOutputTree
        for br in self.branches:
          self.out.branch("%s_%s"%(self.outputMomColl,br),'F')
          for daughter in self.outputDaughterColls:
            self.out.branch("%s_%s"%(daughter,br), 'F')
        pass 


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    '''def initReaders(self,tree): # this function gets the pointers to Value and ArrayReaders and sets them in the C++ worker class
        self.eventNumber = tree.valueReader("event")
        self.nGen = tree.valueReader("nGenPart")
        self.GenPt = tree.arrayReader("GenPart_pt")
        self.GenEta = tree.arrayReader("GenPart_eta")
        self.GenPhi = tree.arrayReader("GenPart_phi")
        self.GenMass = tree.arrayReader("GenPart_mass")
        self.GenPdgId = tree.arrayReader("GenPart_pdgId")
        self.GenIdxMom = tree.arrayReader("GenPart_genPartIdxMother")
        self.worker.setGens(self.nGen,self.GenPt,self.GenEta,self.GenPhi,self.GenMass,self.GenPdgId,self.GenIdxMom)

        self._ttreereaderversion = tree._ttreereaderversion
        pass'''
     
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
        
      #if event._tree._ttreereaderversion > self._ttreereaderversion:
      #   self.initReaders(event._tree)
      
      '''res=self.worker.Run()
      if not res:
         return False

      # only one mother is permited per event
      for ibr, br in enumerate(self.branches):
          output=self.worker.getMomPtEtaPhiMass(ibr)
       #   print output
          self.out.fillBranch("%s_%s"%(self.outputMomColl,br),output)


      # multiple daughters
      for idaughter,daughter in enumerate(self.daughtersPdgId):
         for ibr,br in enumerate(self.branches):
           output=self.worker.getDaughterPtEtaPhiMass(daughter,ibr)
           self.out.fillBranch("%s_%s"%(self.outputDaughterColls[idaughter],br),output)'''

      return True

