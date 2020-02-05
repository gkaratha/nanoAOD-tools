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

    def __init__(self,recoInput,genInput,output,branches=None,skipNotMatched=False):
        self.recoinput = recoInput
        self.geninput = genInput
        self.output = output
        self.branches = branches        
        self.skipNotMatched=skipNotMatched
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

        if hasattr(event,self.geninput+"_eta") and hasattr(event,self.geninput+"_phi") :
          geta = getattr(event,self.geninput+"_eta") 
          gphi = getattr(event,self.geninput+"_phi") 

        
        recocoll = Collection(event,self.recoinput)
        recoEtaPhi = [ deltaR(obj.eta, obj.phi, geta, gphi) for obj in recocoll  if not isnan(deltaR(obj.eta, obj.phi, geta, gphi))]
        #if any(isnan(recoEtaPhi)) :
        #   print recoEtaPhi
        if len(recoEtaPhi)==0:
          if self.skipNotMatched:
             return False
          for br in self.branches:  
            self.out.fillBranch("%s_%s"%(self.output,br),-99)
          self.out.fillBranch("%s_DR"%(self.output),99)
          self.out.fillBranch("%s_Idx"%(self.output),-1)

        else:
          dr = min(recoEtaPhi)
          idx = recoEtaPhi.index(dr)
          if isnan(dr):
            recoEtaPhi=recoEtaPhi.pop(idx)
            dr = min(recoEtaPhi)
            idx = recoEtaPhi.index(dr)
#          print self.branches
          for br in self.branches:  
             out=getattr(recocoll[idx],br)
#             if self.output=="recoK":
#               print br,out,dr,idx#,recoEtaPhi[:5]
             self.out.fillBranch("%s_%s"%(self.output,br),out)
          self.out.fillBranch("%s_DR"%(self.output),dr) 
          self.out.fillBranch("%s_Idx"%(self.output),idx)   

        return True

