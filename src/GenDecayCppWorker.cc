/*#include "../interface/GenDecayCppWorker.h"

GenDecayCppWorker::GenDecayCppWorker(){
}

GenDecayCppWorker::~GenDecayCppWorker(){
}



void 
GenDecayCppWorker::setGens(TTreeReaderValue<unsigned> *nGen_,
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


void 
GenDecayCppWorker::setMomId(int momPdg_){
     momPdg=momPdg_;
  }


void
GenDecayCppWorker::setDaughterId(int daughterPdg_){
  daughterPdg.push_back(daughterPdg_);
}

void 
GenDecayCppWorker::setInterMomId(int interMomPdg_){
   interMomPdg.push_back(interMomPdg_);
}


bool
GenDecayCppWorker::Run(){

  momProperties.clear();   
  BdecayIdx.clear();
  BIdx.clear();
  daughtersProperties.clear();
  
  // find final state parts that come from the mother we want
  unsigned n = (*nGen).Get()[0];
  
  for (unsigned igen=0; igen<n; ++igen){
    bool Match=false;
    bool MatchConj=false;
    int daughterIdx=0;
   
    
    for (unsigned idaughter=0; idaughter<daughterPdg.size(); ++idaughter){
      if ( (*GenPdgId)[igen] == daughterPdg[idaughter] ){
         Match=true;  
         daughterIdx=idaughter;        
      }
      if ( (*GenPdgId)[igen] == -1*daughterPdg[idaughter] ){
         MatchConj=true;  
	 daughterIdx=idaughter;
      }      
    }

    if ( !Match && !MatchConj ) continue;
   
   
    auto momidx=(*GenMomId)[igen];
   
    if ( momidx<0 || unsigned(momidx)>n) 
        continue;
    if ( interMomPdg[daughterIdx] ==0 ) {     
      if ( ((*GenPdgId)[momidx] != momPdg && Match ) &&
	   ((*GenPdgId)[momidx] != -1*momPdg && MatchConj) ) 
         continue;
      BdecayIdx.push_back(igen); 
      BIdx.push_back(momidx);
      
     } else{
      if ( fabs((*GenPdgId)[momidx]) != fabs(interMomPdg[daughterIdx]) )
	continue;
      if ( ((*GenPdgId)[momidx] != interMomPdg[daughterIdx] && Match ) &&
	   ((*GenPdgId)[momidx] != -1*interMomPdg[daughterIdx] && MatchConj) ) 
           continue;
      auto grandMomidx=(*GenMomId)[momidx];
      if ( grandMomidx<0 || unsigned(grandMomidx)>n) 
        continue;
      if ( fabs( (*GenPdgId)[grandMomidx] ) != momPdg ) continue;
      BdecayIdx.push_back(igen); 
      BIdx.push_back(grandMomidx);
      
      }
  }
  
  // clear to be sure
  unique_Count.clear();

  // unique items in the vectors
  std::unique_copy(BIdx.begin(),BIdx.end(),std::back_inserter(unique_Count));
  
  unsigned selectB=0;
  bool FoundB=false;
  for ( auto i: unique_Count){
    if ( std::count(BIdx.begin(), BIdx.end(), i) == int(daughterPdg.size()) ){
      selectB=i;
      FoundB=true;
    }
  } 
  // std::cout<<"d size "<<int(daughterPdg.size())<<" "<<std::count(BIdx.begin(), BIdx.end(), selectB)<<std::endl;
  
  if (!FoundB) return false;
  // save B properties
  momProperties.push_back((*GenPdgId)[selectB]);
  momProperties.push_back((*GenPt)[selectB]);
  momProperties.push_back((*GenEta)[selectB]);
  momProperties.push_back((*GenPhi)[selectB]);
  momProperties.push_back((*GenMass)[selectB]);
  
  // save Daughter properties
  for (unsigned id=0; id<BdecayIdx.size(); ++id){
    if ( BIdx[id] != selectB ) continue;
    unsigned idx = BdecayIdx[id];
    std::vector<float> daughterProperties;
    daughterProperties.push_back((*GenPdgId)[idx]);
    daughterProperties.push_back((*GenPt)[idx]);
    daughterProperties.push_back((*GenEta)[idx]);
    daughterProperties.push_back((*GenPhi)[idx]);
    daughterProperties.push_back((*GenMass)[idx]);
    daughtersProperties.push_back(daughterProperties);
  }

  return true;
}*/
