#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib.meos import MEoS
from lib import unidades


class nC10(MEoS):
    """Multiparameter equation of state for n-decane

    >>> decano=nC10(T=500, P=0.1)
    >>> print "%0.1f %0.2f %0.2f %0.2f %0.5f %0.4f %0.4f %0.1f" % (decano.T, decano.rho, decano.u.kJkg, decano.h.kJkg, decano.s.kJkgK, decano.cv.kJkgK, decano.cp.kJkgK, decano.w)
    500.0 3.56 377.04 405.10 0.89052 2.4600 2.5333 166.4
    """
    name = "decane"
    CASNumber = "124-18-5"
    formula = "CH3-(CH2)8-CH3"
    synonym = ""
    rhoc = unidades.Density(233.342)
    Tc = unidades.Temperature(617.7)
    Pc = unidades.Pressure(2103.0, "kPa")
    M = 142.28168  # g/mol
    Tt = unidades.Temperature(243.5)
    Tb = unidades.Temperature(447.27)
    f_acent = 0.4884
    momentoDipolar = unidades.DipoleMoment(0.07, "Debye")
    id = 14

    CP1 = {"ao": 19.109,
           "an": [],
           "pow": [],
           "ao_exp": [25.685, 28.233, 12.417, 10.035],
           "exp": [1193, 2140, 4763, 10862],
           "ao_hyp": [], "hyp": []}

    CP2 = {"ao": 4.0,
           "an": [], "pow": [],
           "ao_exp": [], "exp": [],
           "ao_hyp": [21.0069, 43.49310, 58.36570, 0],
           "hyp": [0.267034159*Tc, 1.353835195*Tc, 2.833479035*Tc, 0]}

    helmholtz1 = {
        "__type__": "Helmholtz",
        "__name__": "short Helmholtz equation of state for decane of Lemmon and Span (2006)",
        "__doc__":  u"""Lemmon, E.W., Span, R. Short fundamental equations of state for 20 industrial fluids. J. Chem. Eng. Data 51 (2006), 785 – 850.""",
        "R": 8.314472,
        "cp": CP1,

        "Tmin": Tt, "Tmax": 675.0, "Pmax": 800000.0, "rhomax": 5.41, 
        "Pmin": 0.0014, "rhomin": 5.41, 

        "nr1": [1.0461, -2.4807, 0.74372, -0.52579, 0.15315, 0.00032865],
        "d1": [1, 1, 1, 2, 3, 7],
        "t1": [0.25, 1.125, 1.5, 1.375, 0.25, 0.875],

        "nr2": [0.84178, 0.055424, -0.73555, -0.18507, -0.020775, 0.012335],
        "d2": [2, 5, 1, 4, 3, 4],
        "t2": [0.625, 1.75, 3.625, 3.625, 14.5, 12.],
        "c2": [1, 1, 2, 2, 3, 3],
        "gamma2": [1]*6}

    GERG = {
        "__type__": "Helmholtz",
        "__name__": "Helmholtz equation of state for propane of Kunz and Wagner (2008).",
        "__doc__":  u"""Kunz, O.; Wagner, W. -- The GERG-2008 Wide-Range Equation of State for Natural Gases and Other Mixtures- An Expansion of GERG-2004. J. Chem. Eng. Data, 2012, 57 (11), pp 3032–3091""",
        "R": 8.314472,
        "cp": CP2,

        "Tmin": Tt, "Tmax": 675.0, "Pmax": 800000.0, "rhomax": 5.41, 
        "Pmin": 0.0014, "rhomin": 5.41, 

        "nr1": [0.10461e1, -0.24807e1, 0.74372, -0.52579, 0.15315, 0.32865e-3],
        "d1": [1, 1, 1, 2, 3, 7],
        "t1": [0.25, 1.125, 1.5, 1.375, 0.25, 0.875],

        "nr2": [0.84178, 0.55424e-1, -0.73555, -0.18507, -0.20775e-1, 0.12335e-1],
        "d2": [2, 5, 1, 4, 3, 4],
        "t2": [0.625, 1.75, 3.625, 3.625, 14.5, 12.],
        "c2": [1, 1, 2, 2, 3, 3],
        "gamma2": [1]*6}

    eq = helmholtz1, GERG

    _surface = {"sigma": [0.0536], "exp": [1.26]}
    _dielectric = {"eq": 3, "Tref": 273.16, "rhoref": 1000.,
                   "a0": [0.10924],  "expt0": [-1.], "expd0": [1.],
                   "a1": [49.32, 0.05], "expt1": [0, 1], "expd1": [1, 1],
                   "a2": [220.15, -316.3, -88358, 53511],
                   "expt2": [0, 1, 0, 1], "expd2": [2, 2, 3, 3]}
    _vapor_Pressure = {
        "eq": 5,
        "ao": [-0.87738e1, 0.40864e1, -0.40775e1, -0.64910e1, 0.15598e1],
        "exp": [1.0, 1.5, 1.93, 4.14, 4.7]}
    _liquid_Density = {
        "eq": 1,
        "ao": [0.92435e1, -0.16288e2, 0.20445e2, -0.17624e2, 0.73796e1],
        "exp": [0.535, 0.74, 1.0, 1.28, 1.57]}
    _vapor_Density = {
        "eq": 3,
        "ao": [-0.50378e1, -0.34694e1, -0.15906e2, -0.82894e2, 0.29336e2, -0.10985e3],
        "exp": [0.4985, 1.33, 2.43, 5.44, 5.8, 11.0]}

    visco0 = {"eq": 1, "omega": 1,
              "collision": [0.343267, -0.460514],
              "__name__": "Huber (2004)",
              "__doc__": """Huber, M.L., Laesecke, A. and Xiang, H.W. , "Viscosity correlations for minor constituent fluids in natural gas: n-octane, n-nonane and n-decane" Fluid Phase Equilibria 224(2004)263-270""",
              "ek": 490.51, "sigma": 0.686,
              "Tref": 1., "rhoref": 1.,
              "n_chapman": 0.021357,

              "n_virial": [-0.19572881e2, 0.21973999e3, -0.10153226e4,
                           0.24710125e4, -0.33751717e4, 0.24916597e4,
                           -0.78726086e3, 0.14085455e2, -0.34664158],
              "t_virial": [0, -0.25, -0.5, -0.75, -1, -1.25, -1.5, -2.5, -5.5],
              "Tref_virial": 490.51, "etaref_virial": 0.1944120,

              "Tref_res": 617.7, "rhoref_res": 1.64*M, "etaref_res": 1000,
              "n_packed": [2.55105, 1.71465, 0],
              "t_packed": [0, 0.5, 1],
              "n_poly": [-0.402094e-1, 0.0, 0.404435e-1, -0.142063e-1, -0.453387],
              "t_poly": [-1, -1, -2, -2, 0],
              "d_poly": [2, 3, 2, 3, 1],
              "g_poly": [0, 0, 0, 0, -1],
              "c_poly": [0, 0, 0, 0, 1],
              "n_num": [0.453387],
              "t_num": [0],
              "d_num": [1],
              "g_num": [0],
              "c_num": [0],
              "n_den": [1, -1],
              "t_den": [0, 0],
              "d_den": [0, 1],
              "g_den": [1, 0],
              "c_den": [0, 0]}

    _viscosity = visco0,

    thermo0 = {"eq": 1,
               "__name__": "Huber (2005)",
               "__doc__": """Huber, M.L. and Perkins, R.A., "Thermal conductivity correlations for minor constituent fluids in natural gas: n-octane, n-nonane and n-decane" Fluid Phase Equilibria 227 (2005) 47-55""",

               "Tref": 617.7, "kref": 1,
               "no": [0.105543e-1, -0.514530e-1, 0.118979, -0.372442e-1],
               "co": [0, 1, 2, 3],

               "Trefb": 617.7, "rhorefb": 1.64, "krefb": 1,
               "nb": [-0.294394e-1, 0.150509e-1, 0.499245e-1, 0.0, -0.142700e-1,
                      -0.138857e-1, 0.150828e-2, 0.433326e-2, 0.0, 0.0],
               "tb": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
               "db": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
               "cb": [0]*10,

               "critical": 3,
               "gnu": 0.63, "gamma": 1.239, "R0": 1.03,
               "Xio": 0.194e-9, "gam0": 0.0496, "qd": 7.086368e-10, "Tcref": 926.55}

    _thermal = thermo0,
