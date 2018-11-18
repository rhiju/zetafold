from wrapped_array import *

def initialize_sequence_and_ligated( sequences, circle, use_wrapped_array = False ):

    if isinstance( sequences, str ): sequence = sequences
    else:
        sequence = ''
        for i in range( len( sequences ) ): sequence += sequences[i]
    N = len( sequence )

    ligated = [True] * N
    if use_wrapped_array: ligated = WrappedArray( N, True )

    if isinstance( sequences, list ):
        L = 0
        for i in range( len(sequences)-1 ):
            L = L + len( sequences[i] )
            ligated[ L-1 ] = False
    if not circle: ligated[ N-1 ] = False

    return sequence, ligated

##################################################################################################
def get_num_strand_connections( sequences, circle ):
    num_strand_connections = len( sequences ) if isinstance( sequences, list ) else 1
    num_strand_connections -= 1
    if circle: num_strand_connections -= 1
    assert( num_strand_connections >= 0 )
    return num_strand_connections

##################################################################################################
def initialize_all_ligated( ligated ):
    '''
    all_ligated is needed to keep track of whether an apical loop is long enough
    to be 'closed' into a hairpin by base pair formation.
    TODO: alternatively could create a 'hairpin_OK' matrix -- that
          would be more analogous to pre-scanning for protein/ligand binding sites too.
    '''
    N = len( ligated )
    all_ligated = initialize_matrix( N, True )
    for i in range( N ): #index of subfragment
        found_cutpoint = False
        all_ligated[ i ][ i ] = True
        for offset in range( N ): #length of subfragment
            j = (i + offset) % N;  # N cyclizes
            all_ligated[ i ][ j ] = ( not found_cutpoint )
            if not ligated[ j ]: found_cutpoint = True
    return all_ligated

