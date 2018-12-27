#!/usr/bin/python
'''
This is a pretty awful 'compiler' script to convert recursions.py to explicit_recursions.py
'''

# a bunch of unfortunate edge cases!
not_data_objects = ['self.Z_BPq','sequence','self.params.C_eff_stack', 'motif_type.strands','match_base_pair_type_sets','motif_type.base_pair_type_sets']
not_2D_dynamic_programming_objects = ['all_ligated','ligated','self.Z_BPq','sequence','self.allow_base_pair','self.in_forced_base_pair','self.params.C_eff_stack','motif_type.strands','match_base_pair_type_sets','motif_type.base_pair_type_sets' ]
dynamic_programming_lists = ['Z_final']
dynamic_programming_data = ['Z_seg1','Z_seg2']


def find_substring(substring, string):
    """
    From stackoverflow...
    Returns list of indices where substring begins in string

    >>> find_substring('me', "The cat says meow, meow")
    [13, 19]
    """
    indices = []
    index = -1  # Begin at -1 so index + 1 is 0
    while True:
        # Find next index of substring, by starting search from index + 1
        index = string.find(substring, index + 1)
        if index == -1:
            break  # All occurrences have been found
        indices.append(index)
    return indices

lines_new = []
lines_deriv = []
lines_contrib = []
in_comment_block = False

with open('recursions.py') as f:  lines = f.readlines()

for line in lines:
    line_new = ''

    # add blocks of deriv & contrib lines that may be accumulating.
    if len( line ) > 1 and line[0] != ' ':
        if len(lines_deriv) > 0:
            lines_new.append('    if self.options.calc_deriv_DP: # AUTOGENERATED DERIV BLOCK\n')
            lines_new     += lines_deriv
            lines_new += '\n'
            lines_deriv = []
        if len( lines_contrib ) > 0:
            lines_new.append('    if self.options.calc_contrib: # AUTOGENERATED CONTRIBS BLOCK\n')
            lines_new += lines_contrib
            lines_contrib = []
            lines_new += '\n'


    if line.count( '.dQ' ) or line.count( '.Q') :
        # if explicitly defining Q, dQ already, special case!!!
        line_new = line.replace( '[i][j].Q', '.Q[i][j]' )
        line_new = line_new.replace( '[i][j].dQ', '.dQ[i][j]' )
        lines_new.append( line_new )
        continue

    if line.count( "'''" ): in_comment_block = not in_comment_block

    # most important thing -- need to look for get/set of Z_BP[i][j] (DynamicProgrammingMatrix)
    in_bracket = False
    in_second_bracket = False
    just_finished_first_bracket = False
    all_args = []
    args = []
    words = []
    word = ''
    bracket_word = ''
    at_beginning = True
    num_indent = 0
    first_char = ''
    for char in line:
        if (char == ' ' or char == '\n') and not in_bracket:
            if at_beginning: num_indent += 1
            if word in dynamic_programming_data:
                line_new += '.Q'
            line_new += char
            if len( word ) > 0:
                words.append( word )
                word = ''
            continue
        else:
            if at_beginning: first_char = char
            at_beginning = False
        if in_bracket:
            bracket_word += char
            arg += char
        if char == '[':
            if not (word in not_2D_dynamic_programming_objects ) and not just_finished_first_bracket: line_new += '.Q'
            bracket_word += char
            arg = ''
            in_bracket = True
            if just_finished_first_bracket:
                in_second_bracket = True
            else:
                args = []
                if len( word ) > 0:
                    words.append( word )
                    word = ''
        elif char == ']':
            if not words[-1].replace('(','') in not_data_objects:
                if len(arg[:-1]) == 1:
                    line_new += '['+arg[:-1]+'%N]'
                else:
                    line_new += '[('+arg[:-1]+')%N]'
            else:
                line_new += bracket_word
            args.append( arg[:-1] )
            if in_second_bracket:
                assert( len( args ) == 2 )
                if not words[-1].replace('(','') in not_data_objects:
                    all_args.append( (len(line_new),words[-1],args[0],args[1]) )
                args = []
            else:
                just_finished_first_bracket = True
            in_bracket = False
            in_second_bracket = False
            bracket_word = ''
        else:
            if not in_bracket: line_new += char
            word += char
            just_finished_first_bracket = False

    # temporary hack -- this is for Z_seg1, Z_seg2 assignment...
    line_new = line_new.replace( '.Q  = DynamicProgrammingData',' = DynamicProgrammingData' )

    lines_new.append( line_new )

    # is this an assignment? then need to create derivative and contribution lines
    assign_pos = line_new.find('+= ')
    if ( assign_pos < 0 ): assign_pos = line_new.find(' = ' )
    is_assignment_line =  assign_pos >= 0 and line_new.count('.Q') > 0

    if first_char != '#' and line_new.count( 'def' ) == 0 and not is_assignment_line and \
       not in_comment_block and not line.count( "'''" ) and first_char != '' and num_indent >= 4:
        lines_deriv.append( ' '*4 + line_new )
        lines_contrib.append( ' '*4 + line_new )

    if line == line_new: continue
    print line,
    print line_new,

    if assign_pos > -1:
        Qpos = find_substring( '.Q', line_new )
        if len( Qpos ) > 0 and Qpos[0] < assign_pos:
            assert( len( Qpos ) > 1 )

            #lines_new.append( ' '*num_indent + 'if self.options.calc_deriv_DP:\n' )
            #print lines_new[-1],
            line_beginning = ' '*4 + line_new[:Qpos[0]] + '.dQ' # extra indent
            # deriv line
            for i in range( 1, len( Qpos ) ):
                line_deriv = line_beginning
                assert( Qpos[i] > assign_pos )
                for j in range(1, len( Qpos) ):
                    line_deriv += line_new[Qpos[j-1]+2 : Qpos[j]]
                    if i == j: line_deriv += '.dQ'
                    else: line_deriv += '.Q'
                line_deriv += line_new[ Qpos[-1]+2:]
                print line_deriv,
                lines_deriv.append(line_deriv)

            # contrib line
            print lines_new[-1],
            line_contrib = ' '*num_indent
            line_contrib += ' '*4
            line_contrib += 'if %s > 0:\n' % line_new[assign_pos+3:-1]
            line_contrib += ' '*8
            line_contrib += line_new[:Qpos[0]] +  '.contribs'  # extra indent
            line_contrib += line_new[Qpos[0]+2 : assign_pos+3]
            line_contrib +=' [ ('
            line_contrib += line_new[assign_pos+3:-1] + ', ['
            for (n,info) in enumerate(all_args):
                if info[ 0 ] <= assign_pos: continue
                line_contrib += '(%s,' % info[1]
                if len(info[2])> 1:  line_contrib += '(%s)%%N' % info[2]
                else: line_contrib += '%s%%N' % info[2]
                line_contrib+=','
                if len(info[3])>1:   line_contrib += '(%s)%%N' % info[3]
                else: line_contrib += '%s%%N' % info[3]
                line_contrib+=')'
                if n < len( all_args )-1: line_contrib += ', '
            line_contrib += '] ) ]\n'
            print line_contrib,
            lines_contrib.append( line_contrib)
    print


with open('explicit_recursions.py','w') as f:
    f.writelines( lines_new )

