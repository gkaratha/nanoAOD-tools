import FWCore.ParameterSet.Config as cms
from  PhysicsTools.NanoAOD.common_cff import *



DiMuonVertexTable = cms.EDProducer("DiMuonSecVertexTableProducer",
    src = cms.InputTag("finalMuons"),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    vertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
    mu1Selection = cms.string ("pt>5 && abs(eta)<2.4"),
    mu2Selection = cms.string ("pt>3 && abs(eta)<2.4"),
    preVtxSelection = cms.string ("pt>5 && abs(eta)<2.4 && mass<3.5 && mass>2.5"),
    postVtxSelection = cms.string ("userFloat('prob')>0.01"),
    RefitTracks = cms.bool (True)
)



DiMuonVertexTableSeq = cms.Sequence( DiMuonVertexTable)

