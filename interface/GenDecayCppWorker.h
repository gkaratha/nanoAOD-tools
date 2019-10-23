#ifndef PhysicsTools_NanoAODTools_GenDecayCppWorker_h
#define PhysicsTools_NanoAODTools_GenDecayCppWorker_h

#include <utility>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>
#include "DataFormats/Math/interface/LorentzVector.h"




class GenDecayCppWorker {

public:
  GenDecayCppWorker(){
  }

  void setGens(TTreeReaderValue<unsigned> *nGen_,
               TTreeReaderArray<float> *GenPt_,
               TTreeReaderArray<float> *GenEta_,
               TTreeReaderArray<float> *GenPhi_,
               TTreeReaderArray<float> *GenMass_,
               TTreeReaderArray<int> *GenPdgId_,
               TTreeReaderArray<int> *GenMomId_
  ){
    nGen=nGen_;        GenPt=GenPt_;         GenEta=GenEta_;    GenPhi=GenPhi_; 
    GenMass=GenMass_;  GenPdgId=GenPdgId_;   GenMomId=GenMomId_;
  }

  void setMomId(int momPdg_){
     momPdg=momPdg_;
  }

  void setDaughterId(int daughterPdg_){
     daughterPdg.push_back(daughterPdg_);
  }

  void setInterMomId(int interMomPdg_){
     interMomPdg.push_back(interMomPdg_);
  }

  bool Run();

  float getMomPtEtaPhiMass(int i){
    return momProperties[i];
  }

  float getDaughterPtEtaPhiMass(int pdg,int i){
    for (unsigned int idgh=0; idgh<daughtersProperties.size(); ++idgh){
      if (pdg != daughtersProperties[idgh][0]*(momProperties[0]/momPdg) ) 
         continue;
      return daughtersProperties[idgh][i];
    }
  }

private:
  TTreeReaderValue<unsigned> *nGen = nullptr;
  TTreeReaderArray<float> *GenPt = nullptr;
  TTreeReaderArray<float> *GenEta = nullptr;
  TTreeReaderArray<float> *GenPhi = nullptr;
  TTreeReaderArray<float> *GenMass = nullptr;
  TTreeReaderArray<int> *GenPdgId = nullptr;
  TTreeReaderArray<int> *GenMomId = nullptr;
  int momPdg;
  std::vector<int> daughterPdg;
  std::vector<int> interMomPdg;
  std::vector<float> momProperties;
  std::vector<std::vector<float>> daughtersProperties;
  std::vector<unsigned> BdecayIdx;
  std::vector<unsigned> BIdx;
  std::vector<int> unique_Count;
  
};

#endif
