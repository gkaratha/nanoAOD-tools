import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *


DiMuonVertex = cms.EDProducer("DiMuonVertexProducer",
    src = cms.InputTag("slimmedMuons"),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    vertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
    mu1Selection = cms.string ("pt>5 && abs(eta)<2.4"),
    mu2Selection = cms.string ("pt>3 && abs(eta)<2.4"),
    preVtxSelection = cms.string ("pt>5 && abs(eta)<2.4"),
    postVtxSelection = cms.string ("userFloat('prob')>0.01"), # WP 0.01
    RefitTracks = cms.bool (True),
    FitTunePTransientTracks = cms.bool(False),
)

DiMuonTable = cms.EDProducer("SimpleCompositeCandidateFlatTableProducer",
    src = cms.InputTag("DiMuonVertex","diMuons"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("DiMuon"),
    doc  = cms.string("dimuons that create a good vertex"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), # this is the main table for the muons
    variables = cms.PSet(
      CandVars,
      fit_pt = Var("userFloat('fit_pt')",float,doc="fitted pT of dimuon system",precision=12),
      fit_eta = Var("userFloat('fit_eta')",float,doc="fitted eta of dimuon system",precision=12),     
      fit_phi = Var("userFloat('fit_phi')",float,doc="fitted phi of dimuon system",precision=12),
      fit_mass = Var("userFloat('fit_mass')",float,doc="fitted mass of dimuon system",precision=-1),
      vtx_chi2 = Var("userFloat('chi2')",float,doc="chi^2 of vertex",precision=12),
      vtx_dof = Var("userFloat('dof')",float,doc="Deegres of freedom of vertex",precision=6),
      vtx_prob = Var("userFloat('prob')",float,doc="Vertex probability",precision=12),
      vtx_x = Var("userFloat('vtx_x')",float,doc="x of dimuon vtx",precision=12),
      vtx_y = Var("userFloat('vtx_y')",float,doc="y of dimuon vtx",precision=12),
      vtx_z = Var("userFloat('vtx_z')",float,doc="z of dimuon vtx",precision=12),
      IP_fromBS = Var("userFloat('IP_fromBS')",float,doc="2D impact parameter measured from beamspot",precision=12),
      EIP_fromBS = Var("userFloat('EIP_fromBS')",float,doc="error on 2D impact parameter measured from beamspot",precision=12),
      SIP_fromBS = Var("userFloat('SIP_fromBS')",float,doc="significance of 2D impact parameter measured from beamspot",precision=12),
      IP_fromPV = Var("userFloat('IP_fromPV')",float,doc="2D impact parameter measured from primary vertex",precision=12),
      EIP_fromPV = Var("userFloat('EIP_fromPV')",float,doc="error on 2D impact parameter measured from primary vertex",precision=12),
      SIP_fromPV = Var("userFloat('SIP_fromPV')",float,doc="significance of 2D impact parameter measured from primary vertex",precision=12),
        fit_mu1_pt = Var("userFloat('mu1_pt')",float,doc="fitted pT of leading muon",precision=12),
        fit_mu1_eta = Var("userFloat('mu1_eta')",float,doc="fitted eta of leading muon",precision=12),     
        fit_mu1_phi = Var("userFloat('mu1_phi')",float,doc="fitted phi of leading muon",precision=12),
        fit_mu2_pt = Var("userFloat('mu2_pt')",float,doc="fitted pT of subleading muon",precision=12),
        fit_mu2_eta = Var("userFloat('mu2_eta')",float,doc="fitted eta of subleading muon",precision=12),     
        fit_mu2_phi = Var("userFloat('mu2_phi')",float,doc="fitted phi of subleading muon",precision=12),
      mu1_idx = Var("userInt('mu1_idx')",int,doc="idx of leading muon"),
      mu2_idx = Var("userInt('mu2_idx')",int,doc="idx of subleading muon"),

    )
)
