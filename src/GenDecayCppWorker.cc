#include "../interface/GenDecayCppWorker.h"

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
    if ( (*GenMomId)[igen]<0 ) continue;

    unsigned momidx=(*GenMomId)[igen];

    if ( interMomPdg[daughterIdx] ==0 ) {

      if ( ((*GenPdgId)[momidx] != momPdg && Match ) &&
	   ((*GenPdgId)[momidx] != -1*momPdg && MatchConj) ) 
         continue;
      BdecayIdx.push_back(igen); 
      BIdx.push_back(momidx);

    } else{

      if ( ((*GenPdgId)[momidx] != interMomPdg[daughterIdx] && Match ) &&
	   ((*GenPdgId)[momidx] != -1*interMomPdg[daughterIdx] && MatchConj) ) 
           continue;
      unsigned grandMomidx=(*GenMomId)[momidx];
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
}
