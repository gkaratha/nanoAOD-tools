// -*- C++ -*-
//
// Package:    PhysicsTools/NanoAOD
// Class:      DiMuonSecVertexTableProducer
// 
/*
 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  George Karathanasis georgios.karathanasis@cern.ch
//         Created:  Mon, 8 Sep 2019 09:26:39 GMT
//
//



// system include files
#include <memory>
#include <sstream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Utils/interface/StringObjectFunction.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"


#include "SecondaryVertexFitter.h"

constexpr float MUON_MASS= 0.105;

typedef std::vector<reco::TransientTrack> TransientTrackCollection;

class DiMuonSecVertexTableProducer : public edm::stream::EDProducer<> {

  public:
     explicit DiMuonSecVertexTableProducer(const edm::ParameterSet &iConfig) :
       muons_(consumes<pat::MuonCollection>(iConfig.getParameter<edm::InputTag>("src"))),
       bspot_{consumes<reco::BeamSpot>( iConfig.getParameter<edm::InputTag>("beamSpot") )},
       pvs_{consumes< std::vector<reco::Vertex> >( iConfig.getParameter<edm::InputTag>("vertices") )},
       mu1_cuts_{iConfig.getParameter<std::string>("mu1Selection")},
       mu2_cuts_{iConfig.getParameter<std::string>("mu2Selection")},
       pre_vtxfit_cuts_{iConfig.getParameter<std::string>("preVtxSelection")},
       post_vtxfit_cuts_{iConfig.getParameter<std::string>("postVtxSelection")},
       refit_{iConfig.getParameter<bool>("RefitTracks")}
       {       
          produces<nanoaod::FlatTable>();
       }

        ~DiMuonSecVertexTableProducer() override {}

    private:
        void produce(edm::Event&, edm::EventSetup const&) override ;

        const edm::EDGetTokenT<pat::MuonCollection> muons_;
        const edm::EDGetTokenT<reco::BeamSpot> bspot_; 
        const edm::EDGetTokenT<std::vector<reco::Vertex>> pvs_;
        const StringCutObjectSelector<pat::Muon> mu1_cuts_;
        const StringCutObjectSelector<pat::Muon> mu2_cuts_;
        const StringCutObjectSelector<pat::CompositeCandidate> pre_vtxfit_cuts_;
        const StringCutObjectSelector<pat::CompositeCandidate> post_vtxfit_cuts_;        
        bool refit_;
              
};

// ------------ method called to produce the data  ------------
void
DiMuonSecVertexTableProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) 
{
   
    edm::Handle<pat::MuonCollection> muons;
    iEvent.getByToken(muons_, muons);
    edm::Handle<reco::BeamSpot> bspot;
    iEvent.getByToken(bspot_, bspot);  
    edm::Handle<std::vector<reco::Vertex>> pvs;
    iEvent.getByToken(pvs_, pvs);  

    edm::ESHandle<MagneticField> bFieldHandle;
    iSetup.get<IdealMagneticFieldRecord>().get(bFieldHandle);
     
    std::vector<pat::CompositeCandidate> pairs;
    math::XYZPoint pv = (pvs->front()).position();
    // muon pair creation 
    for( pat::MuonCollection::const_iterator mu= muons->begin(); mu!=muons->end(); ++mu){

      // remove mu not qualified for trailing mu
      if ( !mu2_cuts_(*mu) ) continue;

      for( pat::MuonCollection::const_iterator mu2= mu+1; mu2!=muons->end(); ++mu2){
        // remove mu not qualified for trailing mu
        if ( !mu2_cuts_(*mu2) ) continue;
         // remove mu not qualified for leading mu        
        if ( !mu1_cuts_(*mu) && !mu1_cuts_(*mu2) ) continue;

        //create pair
        pat::CompositeCandidate muon_pair;
        muon_pair.setP4(mu->p4() + mu2->p4());
        muon_pair.setCharge(mu->charge() + mu2->charge());
        muon_pair.addUserFloat("deltaR", reco::deltaR(*mu, *mu2));

        // cut before vertex
        if ( !pre_vtxfit_cuts_(muon_pair) ) continue;
        reco::TransientTrack tranmu1((*(mu->bestTrack())), &(*bFieldHandle));
        reco::TransientTrack tranmu2((*(mu2->bestTrack())), &(*bFieldHandle));

        //fit
        TransientTrackCollection mutrk{ tranmu1, tranmu2};
        SecondaryVertexFitter vtx(mutrk,{MUON_MASS,MUON_MASS},refit_);

        // remove failures
        if ( !vtx.success() ) continue;

        //pair after fit
        muon_pair.addUserFloat("fit_pt",vtx.motherP4().pt());
        muon_pair.addUserFloat("fit_eta",vtx.motherP4().eta());
        muon_pair.addUserFloat("fit_phi",vtx.motherP4().phi());
        muon_pair.addUserFloat("fit_mass",vtx.motherP4().mass());
        muon_pair.addUserFloat("fit_charge",vtx.motherCh());

        //vertex quality
        muon_pair.addUserFloat("chi2",vtx.chi2());
        muon_pair.addUserFloat("dof",vtx.dof());
        muon_pair.addUserFloat("prob",vtx.prob());

        //vertex position
        muon_pair.addUserFloat("vtx_x",vtx.motherXYZ().x());
        muon_pair.addUserFloat("vtx_y",vtx.motherXYZ().y());
        muon_pair.addUserFloat("vtx_z",vtx.motherXYZ().z());

        //distance variables
	GlobalPoint Dispbeamspot(
				 -1*((bspot->x0()-vtx.motherXYZ().x())+(vtx.motherXYZ().z()-bspot->z0())* bspot->dxdz()),
				 -1*((bspot->y0()-vtx.motherXYZ().y())+ (vtx.motherXYZ().z()-bspot->z0()) * bspot->dydz()), 0);

        float Lxy = Dispbeamspot.perp();  
        float eLxy= vtx.motherXYZError().rerr(Dispbeamspot); 
        eLxy = TMath::Sqrt( eLxy );

        muon_pair.addUserFloat("IP_fromBS",Lxy);
        muon_pair.addUserFloat("EIP_fromBS",eLxy);
        muon_pair.addUserFloat("SIP_fromBS",eLxy==0 ? Lxy/eLxy : 0);
	
        GlobalPoint DispFromPV(
			        pv.x()-vtx.motherXYZ().x(),
			        pv.y()-vtx.motherXYZ().y(), 
                                0 
                               );

        float LxyPV = DispFromPV.perp();  
        float eLxyPV= vtx.motherXYZError().rerr(DispFromPV); 
        eLxyPV = TMath::Sqrt( eLxyPV );

        muon_pair.addUserFloat("IP_fromPV",LxyPV);
        muon_pair.addUserFloat("EIP_fromPV",eLxyPV);
        muon_pair.addUserFloat("SIP_fromPV",eLxyPV == 0 ? LxyPV/eLxyPV : 0);


        //daughter refited
        for (unsigned i=1; i < 3; ++i){
          muon_pair.addUserFloat("mu"+std::to_string(i)+"_pt",vtx.daughterP4(i-1).pt());
          muon_pair.addUserFloat("mu"+std::to_string(i)+"_eta",vtx.daughterP4(i-1).eta()); 
          muon_pair.addUserFloat("mu"+std::to_string(i)+"_phi",vtx.daughterP4(i-1).phi());
        }

        //daughter index
        muon_pair.addUserFloat("mu1_idx",mu-muons->begin());
        muon_pair.addUserFloat("mu2_idx",mu2-muons->begin());

        // cuts after vertex
        if ( !post_vtxfit_cuts_(muon_pair) ) continue;
        pairs.emplace_back(muon_pair);

      }
    }
      
    // fill the table
    auto tab  = std::make_unique<nanoaod::FlatTable>(pairs.size(), "DiMuon_SV", false, false);
    
    
  
    
    // not optimal way
    for ( auto & var : {"deltaR","fit_pt","fit_eta","fit_phi","fit_mass","vtx_x","vtx_y","vtx_z","prob","IP_fromBS","EIP_fromBS","IP_fromPV","EIP_fromPV","mu1_pt","mu1_eta","mu1_phi","mu2_pt","mu2_eta","mu2_phi","mu1_idx","mu2_idx"} )
   {
     std::vector<float> temp;
     for ( auto & pair: pairs)
       temp.push_back(pair.userFloat(var));
     
     tab->addColumn<float>(var, temp, "", nanoaod::FlatTable::FloatColumn, 12);
   }

    //much better - not working -> perhaps we can have compositecandidate tables?
      /*  tab->addColumnValue<float>("SV_deltaR", pair.userFloat("deltaR"), "deltaR between two muons", nanoaod::FlatTable::FloatColumn, 8);
      tab->addColumnValue<float>("SV_pt", pair.userFloat("fit_pt"), "pT of mother refitted", nanoaod::FlatTable::FloatColumn, 8);
      tab->addColumnValue<float>("SV_eta", pair.userFloat("fit_eta"), "eta of mother refitted", nanoaod::FlatTable::FloatColumn, 8);
      tab->addColumnValue<float>("SV_phi", pair.userFloat("fit_phi"), "phi of mother refitted", nanoaod::FlatTable::FloatColumn, 8);
      tab->addColumnValue<float>("SV_mass", pair.userFloat("fit_mass"), "mass of mother refitted", nanoaod::FlatTable::FloatColumn, 8);
      tab->addColumnValue<float>("SV_x", pair.userFloat("vtx_x"), "x of SV", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_y", pair.userFloat("vtx_y"), "y of SV", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_z", pair.userFloat("vtx_z"), "z of SV", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_prob", pair.userFloat("prob"), "secondary vertex probability", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_IP_fromBS", pair.userFloat("IP_fromBS"), "2D impact parameter from beamspot", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_SIP_fromBS", pair.userFloat("SIP_fromBS"), "significance of 2D impact parameter from beamspot", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_IP_fromPV", pair.userFloat("IP_fromPV"), "2D impact parameter from p. vertex", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_SIP_fromPV", pair.userFloat("SIP_fromPV"), "significance of 2D impact parameter from p. vertex", nanoaod::FlatTable::FloatColumn, 12);
      tab->addColumnValue<float>("SV_mu1_pt", pair.userFloat("fit_mu1_pt"), "muon 1 pT after fit", nanoaod::FlatTable::FloatColumn, 6); 
      tab->addColumnValue<float>("SV_mu1_eta", pair.userFloat("fit_mu1_eta"), "muon 1 eta after fit", nanoaod::FlatTable::FloatColumn, 6); 
      tab->addColumnValue<float>("SV_mu1_phi", pair.userFloat("fit_mu1_phi"), "muon 1 phi after fit", nanoaod::FlatTable::FloatColumn, 6); 
      tab->addColumnValue<float>("SV_mu2_pt", pair.userFloat("fit_mu2_pt"), "muon 2 pT after fit", nanoaod::FlatTable::FloatColumn, 6); 
      tab->addColumnValue<float>("SV_mu2_eta", pair.userFloat("fit_mu2_eta"), "muon 2 eta after fit", nanoaod::FlatTable::FloatColumn, 6); 
      tab->addColumnValue<float>("SV_mu2_phi", pair.userFloat("fit_mu2_phi"), "muon 2 phi after fit", nanoaod::FlatTable::FloatColumn, 6);           
      }*/

    iEvent.put(std::move(tab));
}


//define this as a plug-in
DEFINE_FWK_MODULE(DiMuonSecVertexTableProducer);
