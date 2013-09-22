#!/usr/bin/python

import sys
import subprocess
import re
import pprint

pp = pprint.PrettyPrinter(indent=2)

# define fns 

def syntax_error(line_num, line, message) :
    print '! Syntax error at line ' + str(line_num)
    print '! ' + message
    print '  ' + line
    sys.exit(0)

# get started

if (len(sys.argv) != 3) :
    print 'Incorrect number of files provided'
else :
      
    # open files  
    input_file = open(str(sys.argv[1]))
    output_file = open(str(sys.argv[2]) + '.cpp', 'w+')

    # parse the input file

    line_num = 1

    # set up regexes

    p_whitespace = re.compile(r'\s+')
    p_fn_def = re.compile(r'\((.*)\)([a-z][a-zA-Z0-9]*)\((.*)\)\:')
    p_type_def = re.compile(r'type\(([A-Z][a-zA-Z0-9]*)\)\:\((.*)\)')
    p_sym_name = re.compile(r'([a-z][a-zA-Z0-9]*)')
    p_parens = re.compile(r'\((.*)\)')

    # type map

    types = {'Int': 1, 'Float': 2}

    # functions

    funcs = {}
    func_order = []

    # reserved words

    reserved = ['type', 'Type']

    # start reading the file

    lines = input_file.readlines()

    while line_num <= len(lines) :

        line = lines[line_num - 1]    

        if (line.startswith('#') or line.isspace()) :
            # do nothing - comment or empty
            line_num += 1

        elif (line.startswith('(')) :  

            # function definition
            line = re.sub(p_whitespace, '', line)
            m = re.match(p_fn_def, line)
            if (m) :

                arg_members = {}
                ret_members = {}

                fn_name = m.group(2)

                if (fn_name in funcs) :
                    syntax_error(line_num, line, 'Function already defined : ' + fn_name)

                # get the args and return types
                ret_list = m.group(1).split(',')
                arg_list = m.group(3).split(',')

                ret_types = []
                arg_types = []

                if (not (len(arg_list) == 1 and arg_list[0] == '')) :
                    for arg in arg_list :
                        if (not '@' in arg) :
                            syntax_error(line_num, line, 'Argument must have a symbol name : ' + arg)

                    arg_names = [ arg.split('@')[1] for arg in arg_list ]
                    arg_types = [ arg.split('@')[0] for arg in arg_list ]

                    if (len(arg_names) != len(set(arg_names))) :
                        syntax_error(line_num, line, 'Arguments cannot have duplicate names')

                    for arg_type in arg_types :
                        if (not arg_type in types) :
                            syntax_error(line_num, line, 'Undefined type : ' + arg_type)

                    for arg_name in arg_names :
                        if (not re.match(p_sym_name, arg_name)) :
                            syntax_error(line_num, line, 'Invalid symbol name : ' + arg_name)

                    i = 0
                    for m_name, m_type in zip(arg_names, arg_types):
                        arg_members[m_name] = { 'index' : i, 'type' : m_type }
                        i += 1 

                else :
                    arg_list = []

                if (not (len(ret_list) == 1 and ret_list[0] == '')) :
                    for ret in ret_list :
                        if (not '@' in ret) :
                            syntax_error(line_num, line, 'Return must have a symbol name : ' + ret)

                    ret_names = [ ret.split('@')[1] for ret in ret_list ]
                    ret_types = [ ret.split('@')[0] for ret in ret_list ]

                    if (len(ret_names) != len(set(ret_names))) :
                        syntax_error(line_num, line, 'Returns cannot have duplicate names')

                    for ret_type in ret_types :
                        if (not ret_type in types) :
                            syntax_error(line_num, line, 'Undefined type : ' + ret_type)

                    for ret_name in ret_names :
                        if (not re.match(p_sym_name, ret_name)) :
                            syntax_error(line_num, line, 'Invalid symbol name : ' + ret_name)

                    i = 0
                    for m_name, m_type in zip(ret_names, ret_types):
                        ret_members[m_name] = { 'index' : i, 'type' : m_type }
                        i += 1 

                else :
                    ret_list = []

                # make sure that they have been defined
                for type_name in (ret_types + arg_types) :
                    if (type_name != '' and not type_name in types) :
                        syntax_error(line_num, line, 'Undefined type : ' + type_name)

                funcs[fn_name] = {'args' : arg_members, 'rets' : ret_members}
                func_order.append(fn_name)

                print 'function def : ' + fn_name
                print '  returns : ' + str(ret_list)
                print '  args : ' + str(arg_list)

                # parse function body
                line_num += 1
                line = lines[line_num - 1]

                body = ''

                body_start = line_num

                while ((re.match(p_whitespace, line) or line.startswith('#')) and line_num < len(lines)) :

                    if (not line.startswith('#')) :
                        # strip and append to body 
                        line = re.sub(p_whitespace, '', line)
                        body += line

                    line_num += 1
                    line = lines[line_num - 1]

                print '  function body : ' + body 
                m = re.match(p_parens, body)

                if (m) :
                    rets = m.group(1).split(',')
                    #if (len(rets) != len(ret_list)) :
                    #    syntax_error(body_start, lines[body_start - 1], 'Function must return ' + str(len(ret_list)) + ' value(s)')
                else :
                    syntax_error(body_start, lines[body_start - 1], 'Invalid function body')

                line = lines[line_num - 1]

            else :
                syntax_error(line_num, line, 'Invalid function definition')

        elif (line.startswith('type')) :

            # user defined type
            line = re.sub(p_whitespace, '', line)
            m = re.match(p_type_def, line)
            if (m) :

                members = {}

                type_name = m.group(1)
                if type_name in types :
                    syntax_error(line_num, line, 'Type already defined : ' + type_name)
                
                arg_list = m.group(2).split(',')

                arg_types = []

                if (not (len(arg_list) == 1 and arg_list[0] == '')) :
                    for arg in arg_list :
                        if (not '@' in arg) :
                            syntax_error(line_num, line, 'Type member must have a symbol name : ' + arg)

                    arg_names = [ arg.split('@')[1] for arg in arg_list ]
                    arg_types = [ arg.split('@')[0] for arg in arg_list ]

                    if (len(arg_names) != len(set(arg_names))) :
                        syntax_error(line_num, line, 'Type members cannot have duplicate names')

                    for arg_type in arg_types :
                        if (not arg_type in types) :
                            syntax_error(line_num, line, 'Undefined type : ' + arg_type)

                    for arg_name in arg_names :
                        if (not re.match(p_sym_name, arg_name)) :
                            syntax_error(line_num, line, 'Invalid symbol name : ' + arg_name)

                    i = 0
                    for m_name, m_type in zip(arg_names, arg_types):
                        members[m_name] = { 'index' : i, 'type' : m_type }
                        i += 1 

                types[type_name] = members

                print 'type def : ' + type_name
                print '  ' + str(arg_list)

                line_num += 1
                line = lines[line_num - 1]
            else :
                syntax_error(line_num, line, 'Invalid type definition')
        else :
            syntax_error(line_num, line, 'Unknown syntax')  

    print 'Types : ' 
    pp.pprint(types)
    print 'Functions : ' 
    pp.pprint(func_order)
    pp.pprint(funcs)

    # close the input file

    input_file.close()

    # write the boilerplate

    output_file.write("""
#include <iostream>
#include <new>
using namespace std;

typedef struct {
    int type;
    void *value;
} var; 

""")

    # create all functions

    for func_name in func_order :
        if func_name != 'main' :
            output_file.write('void ' + func_name + 
                '(var *' + func_name + '_input, var *' + func_name + '_output) { }\n\n')


    output_file.write("""int main(int argc, const char* argv[]) {

""")

    output_file.write('}\n')

    
    output_file.close()

    # compile translated cpp file and delete it
    print 'File parsed successfully'
    print 'Compiling...'

    cmd = ['g++', str(sys.argv[2]) + '.cpp', '-o', str(sys.argv[2])]

    p = subprocess.Popen(cmd)  
    p.wait() 

    print 'Executable created'

    # cmd = ['rm', str(sys.argv[2]) + '.cpp']

    p = subprocess.Popen(cmd)  
    p.wait() 

    print 'Cleanup finished'

