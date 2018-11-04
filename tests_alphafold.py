#!/usr/bin/python
from alphafold.output_helpers import *
from alphafold.partition import *

def test_alphafold():
    (C_init, l, Kd_BP, l_BP, C_eff_stacked_pair, K_coax, l_coax, C_std, min_loop_length, allow_strained_3WJ ) = AlphaFoldParams().get_variables()

    # test of sequences where we know the final partition function.
    sequence = 'CNNNGNN'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, circle = True, calc_deriv = True )
    output_test( Z, C_init  * (l**7) * (1 + (C_init * l_BP**2) / Kd_BP ) / C_std, \
                 bpp, [0,4], (C_init * l_BP**2/ Kd_BP) / ( 1 + C_init * l_BP**2/ Kd_BP) )

    sequence = 'CNG'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True, backtrack = True )
    assert( bps_MFE == [(0,2)] )
    output_test( Z, 1 + C_init * l**2 * l_BP/ Kd_BP, \
                 bpp, [0,2], (C_init * l**2 * l_BP/Kd_BP)/( 1 + C_init * l**2 * l_BP/Kd_BP ) )

    sequences = ['C','G']
    (Z, bpp, bps_MFE, dZ) = partition( sequences, calc_deriv = True ) # note that Z sums over only base pair (not dissociated strands!)
    output_test( Z, C_std/ Kd_BP, \
                 bpp, [0,1], 1.0 )

    sequences = ['GC','GC']
    (Z, bpp, bps_MFE, dZ) = partition( sequences, calc_deriv = True )
    output_test( Z, (C_std/Kd_BP)*(2 + l**2 * l_BP**2 *C_init/Kd_BP + C_eff_stacked_pair/Kd_BP ), \
                 bpp, [0,3], (1 + l**2 * l_BP**2 * C_init/Kd_BP + C_eff_stacked_pair/Kd_BP )/(2 + l**2 * l_BP**2 *C_init/Kd_BP + C_eff_stacked_pair/Kd_BP ) )

    sequence = 'CNGGC'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True )
    output_test( Z, 1 + C_init * l**2 *l_BP/Kd_BP * ( 2 + l ), \
                 bpp, [0,2], C_init*l**2*l_BP/Kd_BP /(  1+C_init*l**2*l_BP/Kd_BP * ( 2 + l )) )

    sequence = 'CGNCG'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True )
    output_test( Z, 1 + C_init*l**2*l_BP/Kd_BP +
                 C_init*l**4*l_BP/Kd_BP  +
                 C_init**2 * (l_BP**3) * l**4 /Kd_BP /Kd_BP +
                 C_init * l_BP * l**2 * C_eff_stacked_pair/Kd_BP /Kd_BP , \
                 bpp, [0,4], ( C_init*l**4*l_BP/Kd_BP  + C_init**2 * (l_BP**3) * l**4 /Kd_BP /Kd_BP  + C_init * l_BP * l**2 * C_eff_stacked_pair/Kd_BP /Kd_BP) / ( 1 + C_init*l**2*l_BP/Kd_BP + C_init*l**4*l_BP/Kd_BP  + C_init**2 * (l_BP**3) * l**4 /Kd_BP /Kd_BP + C_init * l_BP * l**2 * C_eff_stacked_pair/Kd_BP /Kd_BP )  )

    #################################################
    # let's do a numerical vs. analytic deriv test
    #################################################
    params_perturb = AlphaFoldParams()
    delta = 1.0e-10
    params_perturb.Kd_BP += delta
    (Z_perturb, bpp_perturb, bps_MFE_perturb, dZ_perturb) = partition( sequence, params_perturb ) # note that Z sums over only base pair (not dissociated strands!)
    dZ_numerical = (Z_perturb-Z)/delta
    print "dZ_dKd (numerical) =",dZ_numerical, ";  dZ_dKd (analytic) =",dZ
    assert( abs( dZ_numerical - dZ )/ abs( dZ ) < 1.0e-5 )
    print

    sequence = 'CNGCNG'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True )
    output_test( Z, (1 + C_init * l**2 *l_BP/Kd_BP)**2  + C_init * l**5 * l_BP/Kd_BP + (C_init * l**2 *l_BP/Kd_BP)**2 * K_coax, \
                 bpp, [0,2], (C_init * l**2 *l_BP/Kd_BP*(1 + C_init * l**2 *l_BP/Kd_BP) + (C_init * l**2 *l_BP/Kd_BP)**2 * K_coax)/((1 + C_init * l**2 *l_BP/Kd_BP)**2  + C_init * l**5 * l_BP/Kd_BP + (C_init * l**2 *l_BP/Kd_BP)**2 * K_coax) )


    # testing extended alphabet & coaxial stacks
    sequence = ['xy','yz','zx']
    params_allow_strained_3WJ = AlphaFoldParams()
    params_allow_strained_3WJ.allow_strained_3WJ = True
    (Z, bpp, bps_MFE, dZ) = partition( sequence, params_allow_strained_3WJ, calc_deriv = True )
    Z_ref = 3*(C_std/Kd_BP)**2 * (1 + K_coax)  + \
            (C_std/Kd_BP)**2 * (C_init/Kd_BP) * l**3 * l_BP**3  + \
            3*(C_std/Kd_BP)**2 * (C_init/Kd_BP) * K_coax * l_coax*l**2 * l_BP
    bpp_ref = ( 2 * (C_std/Kd_BP)**2 * (1 + K_coax) + \
                (C_std/Kd_BP)**2 * (C_init/Kd_BP) * l**3 * l_BP**3 + \
                3*(C_std/Kd_BP)**2 * (C_init/Kd_BP) * K_coax * l_coax*l**2 * l_BP ) / Z_ref
    output_test( Z, Z_ref, bpp, [1,2], bpp_ref  )

    # testing extended alphabet & coaxial stacks
    sequence = ['xy','yz','zx']
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True )
    Z_ref = 3*(C_std/Kd_BP)**2 * (1 + K_coax)  + \
            (C_std/Kd_BP)**2 * (C_init/Kd_BP) * l**3 * l_BP**3
    bpp_ref = ( 2 * (C_std/Kd_BP)**2 * (1 + K_coax) + \
                (C_std/Kd_BP)**2 * (C_init/Kd_BP) * l**3 * l_BP**3 ) / Z_ref
    output_test( Z, Z_ref, bpp, [1,2], bpp_ref  )

    # test that caught a bug in Z_final
    sequence = 'NyNyxNx'
    (Z, bpp, bps_MFE, dZ) = partition( sequence, calc_deriv = True )
    Z_ref = (1 + C_init * l**2 *l_BP/Kd_BP)**2  +(C_init * l**2 *l_BP/Kd_BP)**2 * K_coax
    bpp_ref = ( C_init * l**2 *l_BP/Kd_BP * (1 + C_init * l**2 *l_BP/Kd_BP)  + (C_init * l**2 *l_BP/Kd_BP)**2 * K_coax ) / Z_ref
    output_test( Z, Z_ref, bpp, [1,3], bpp_ref  )


if __name__=='__main__':
    test_alphafold()
