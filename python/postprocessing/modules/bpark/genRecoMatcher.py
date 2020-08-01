import ROOT
import numpy as np
import itertools
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import closest
from PhysicsTools.HeppyCore.utils.deltar import *
from math import isnan
from time import sleep



class genRecoMatcher(Module):

    def __init__(self,recoInput,genInput,output,branches=None, addChargeMatching=False,skipNotMatched=False,cuts=True,DRcut=None):
        self.recoinput = recoInput
        self.geninput = genInput
        self.output = output
        self.branches = branches        
        self.addChargeMatching = addChargeMatching
        self.skipNotMatched=skipNotMatched
        self.cuts=cuts
        self.DRcut=DRcut
        if self.DRcut==None:
           self.DRcut=1000
        if skipNotMatched:
          print "WARNING! evts with unmatched objects WILL be skipped. Not ideal for acceptance studies"
          sleep(2)
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("%s_%s"%(self.output,"DR"),'F')
        self.out.branch("%s_%s"%(self.output,"Idx"),'F')
        for br in self.branches:    
            self.out.branch("%s_%s"%(self.output,br),'F')

   
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
       # read gen
        geta = -99
        gphi = -99
        gcharge = 0
        if hasattr(event,self.geninput+"_eta") and hasattr(event,self.geninput+"_phi") :
          geta = getattr(event,self.geninput+"_eta") 
          gphi = getattr(event,self.geninput+"_phi") 
        
        else:
          print "WARNING gen not found!"
          return False
        recocoll = Collection(event,self.recoinput)
        
        recoEtaPhi = [ (deltaR(obj.eta, obj.phi, geta, gphi),iobj,obj) if ( not isnan(deltaR(obj.eta, obj.phi, geta, gphi)) and deltaR(obj.eta, obj.phi, geta, gphi)<self.DRcut and (type(self.cuts)==bool or self.cuts(obj)) )  else (1000,-1)    for iobj,obj in enumerate(recocoll)  ]
        if self.addChargeMatching:
          if hasattr(event,self.geninput+"_charge"):
            gcharge=getattr(event,self.geninput+"_charge") 
            recoEtaPhi = [ (deltaR(obj.eta, obj.phi, geta, gphi),iobj,obj) if (not isnan(deltaR(obj.eta, obj.phi, geta, gphi)) and gcharge==obj.charge  and (type(self.cuts)==bool or self.cuts(obj))  ) else (1000,-1)  for iobj,obj in enumerate(recocoll)   ]
           
        if len(recoEtaPhi)==0:
          if self.skipNotMatched:
             return False
          for br in self.branches:  
            self.out.fillBranch("%s_%s"%(self.output,br),-99)
          self.out.fillBranch("%s_DR"%(self.output),99)
          self.out.fillBranch("%s_Idx"%(self.output),-1)

        else:
          recoEtaPhi.sort(key=lambda l: l[0])
          dr = recoEtaPhi[0][0]
          idx = recoEtaPhi[0][1]
          for br in self.branches:  
             if (idx>0 or idx==0):
                out=getattr(recoEtaPhi[0][2],br)
             else:
                out=-99
             self.out.fillBranch("%s_%s"%(self.output,br),out)

          self.out.fillBranch("%s_DR"%(self.output),dr) 
          self.out.fillBranch("%s_Idx"%(self.output),idx)   

        return True

