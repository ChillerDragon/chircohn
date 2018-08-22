#!/usr/bin/env python
#=====================================
# chircohn compiler by ChillerDragon =
#=====================================

import os
import sys

#global vars
source_file = ""
syntax_file=""
output_file=""
step = 0
steps = 4
IsDebug = False
FoundFuncs = -1
BaseFuncs = 0
user_int = []
user_int_name = []
user_int_index = 0
functions=[["" for x in range(3)] for y in range(2)]
rcon_cmds=[]
mod_cmds=[]

def check_ints():
	global user_int
	global user_int_name
	global user_int_index
	global output_file
	if (output_file != ""):
		finish_file2 = open(output_file, "w")
		with open("tmp/out.cfg", "rU") as f:
			for line in f:
				aWords = line.replace('\n','').split(' ')
				if (aWords[0] == "int"):
					if (IsDebug):
						print("Integer found")
					if len(aWords) < 4:
						print("ERROR wrong integer sytnax (user 'int name = value')")
						finish_file2.close()
						exit()
					if (IsDebug):
						print("Integer syntax check len[" + str(len(aWords)) + "/" + "4]")
					if unicode(aWords[3], "utf-8").isnumeric():
						user_int.append(aWords[3])
						user_int_name.append(aWords[1])
						user_int_index += 1
					else:
						print("ERROR value '" + aWords[3] + "' is not an integer")
						exit()
				else:
					finish_file2.write(line)
					if (IsDebug):
						print(aWords[0] + " != " + "int");
		finish_file2.close()
		print("[info] linking '" + str(output_file) + "'")
	else:
		print("[info] skipped linking due to missing flag -o")
	os.remove("tmp/out.cfg") #clean temporary files

def step_msg(msg):
	global step
	global steps
	print("[" + str(step) + "/" + str(steps) + "] " + msg)
	step += 1

def clean_file():
	f = open("tmp/tmp_source.txt", "w")
	with open(source_file,"r") as file:
		for line in file:
			if not line.isspace():
				f.write(line)
	f.close()

def init_compiler():
	if not os.path.exists("tmp"):
		os.makedirs("tmp")
		f = open("tmp/readme.txt","w")
		f.write("==== chircohn compiler tmp folder ====\n")
		f.write("This folder stores temporary files.\n")
		f.write("They get created during compilation and removed after it.\n")
		f.write("It is suggested to leave this folder empty.\n")
		f.close()
	
def load_rcon_commands():
	global rcon_cmds
	global mod_cmds
	vanilla_file="syntax/vanilla_rcon_cmds.txt"
	if (os.path.isfile(vanilla_file) == False):
		print("Error vanilla file '" + str(vanilla_file) + "' not found")
		exit()
	with open(vanilla_file) as f:
		rcon_cmds = f.readlines()
	rcon_cmds = [x.strip() for x in rcon_cmds]
	if (syntax_file == ""):
		return
	with open(syntax_file) as m:
		mod_cmds = m.readlines()
	mod_cmds = [x.strip() for x in mod_cmds]
	rcon_cmds = rcon_cmds + mod_cmds

def check_syntax(syntax):
	for rcon in rcon_cmds:
		if rcon == syntax:
			if (IsDebug):
				print("rcon command found")
			return 1
	if function_exist(syntax):
		if (IsDebug):
			print("function found")
		return 2
	if function_exist(syntax.replace('()','')): #put in two statements for perfomance increase for programs written without ()
		if (IsDebug):
			print("function found")
		return 2
	if syntax.startswith("#"):
		if (IsDebug):
			print("comment found")
		return 3
	print("Syntax error: '" + syntax + "' is no rcon command or function")
	return -1
	
def function_exist(func_name):
	for name in functions[1]:
		if name == func_name:
			return True
	return False

def pre_create_binary():
	IsFunc = False
	lineNUM = 0
	
	tmp_nf_f = open("tmp/tmp_binary_no_funcs.txt", "w")
	clean_file() #create clean tmp file without newlines
	
	with open("tmp/tmp_source.txt", "rU") as f:
		for line in f:
			lineNUM += 1
			if (line.find("{") != -1):
				if (IsDebug):
					print("found { line " + str(lineNUM))
				IsFunc = True
			if not line.startswith("void") and not IsFunc and not line.startswith("int"):
				aWords = line.replace('\n','').split(' ')
				if (check_syntax(aWords[0]) == -1):
					print("error line " + str(lineNUM))
					tmp_nf_f.close()
					exit()
				tmp_nf_f.write(line)
			if (IsFunc):
				if (line.find("}") != -1):
					if (IsDebug):
						print("found } line " + str(lineNUM))
					IsFunc = False

	os.remove("tmp/tmp_source.txt") #clean temporary files
	tmp_nf_f.close()

def create_binary():
	finish_file = open("tmp/out.cfg", "w")
	pre_create_binary() #removing all function definitions and cleaning newlines
	
	with open("tmp/tmp_binary_no_funcs.txt", "rU") as f:
		for line in f:
			aWords = line.replace('\n','').split(' ')
			if (check_syntax(aWords[0]) == 2):
				aWords[0] = aWords[0].replace('()','')
				func_index = -1
				for i in range(FoundFuncs + 1):
					if functions[1][i] == aWords[0]:
						func_index = i
				
				if func_index == -1:
					print("Error loading function " + aWords[0] + "()")
					finish_file.close()
					exit()	
				#replace function calls with the function code
				finish_file.write(functions[0][func_index])
			else: #no function --> just copy the plain code
				finish_file.write(line)

	os.remove("tmp/tmp_binary_no_funcs.txt") #clean temporary files
	finish_file.close()
	check_ints() #search for user variabales
	
def init_base_functions():
	global BaseFuncs
	global FoundFuncs

	functions[1][0] = "HelloWorld"
	functions[0][0] = "echo helloworld"
	BaseFuncs += 1
	
	functions[1][1] = "test"
	functions[0][1] = "echo test"
	BaseFuncs += 1
	
	functions[1][2] = "test2"
	functions[0][2] = "echo test2\necho test2\necho test2"
	BaseFuncs += 1
	
	FoundFuncs += BaseFuncs

def load_user_functions():
	global FoundFuncs
	IsFunc = False
	with open(source_file, "rU") as f:
		for line in f:
			if line.startswith("void"):
				FoundFuncs += 1
				aWords = line.replace('()', '').replace('\n','').split(' ') #fish the function name		
				if function_exist(aWords[1]):
					print("ERROR function " + aWords[1] + " already exsists")
					exit()
				functions[1].append(aWords[1]) #store the function name in func array
				functions[0].append("") #add empty array part for code
			if (IsFunc):
				if (line.find("}") != -1):
					IsFunc = False
				else:
					aWords = line.replace('()', '').replace('\n','').split(' ')
					if (check_syntax(aWords[0]) == -1):
						print("Syntax error in function " + functions[1][FoundFuncs] + "()")
						exit()
					functions[0][FoundFuncs] += line
					
			if (line.find("{") != -1):
				IsFunc = True
	
	
	
	

	
def compile_main():
	global user_int_index
	global FoundFuncs
	global step
	global steps
	print("===================================")
	print("ChillerDragon's chircohn compiler")
	print("===================================")
	step_msg("init compiler")
	init_compiler()
	step_msg("init base functions")
	init_base_functions()
	step_msg("load rcon commands")
	load_rcon_commands()
	
	load_user_functions()
	if (IsDebug and FoundFuncs):
			for i in range(FoundFuncs + 1):
				print("--------  Index[" + str(i) + "]  -----------")
				print("Name: " + functions[1][i])
				print("Code: \n" + functions[0][i])
				print("functions: " + str(FoundFuncs) + " + 1")
	step_msg("loading functions succeded (" + str(FoundFuncs) + ")")
	
	create_binary()
	
	if (IsDebug and user_int_index > 0):
		for i in range(user_int_index):
			print("===== Int Index[" + str(i) + "] =====")
			print("Name: " + user_int_name[i])
			print("Value: "+ str(user_int[i]))
	step_msg("loading ints succeded (" + str(user_int_index) + ")")
	
def print_help():
	print("==== chircohn compiler manual page ====\n")
	print("usage: chircohn.py <source_file> <options>")
	print("\n=== options ===")
	print("-v                for verbose output")
	print("--help            to show this help")
	print("-mod (file)       syntax file")

def init_script():
	global IsDebug
	global source_file
	global syntax_file
	global output_file
	if len(sys.argv) < 2:
		print("ERROR missing source file")
		print("usage: chircohn.py <source_file> <options>")
		print("'chircohn.py --help' for help")
	else:
		for i in range(len(sys.argv)):
			if sys.argv[i] == "-v":
				IsDebug = True
			if sys.argv[i] == "--help":
				print_help()
				exit()
			if sys.argv[i] == "-o":
				if ((i + 1) < len(sys.argv)):
					output_file=sys.argv[i + 1]
				else:
					print("Error Missing file for the -o argument")
					exit()
			if sys.argv[i] == "-mod":
				if ((i + 1) < len(sys.argv)):
					syntax_file=sys.argv[i + 1]
					if (os.path.isfile(syntax_file) == False):
						print("Error '" + str(syntax_file) + "' is not a valid file path")
						exit()
				else:
					print("Error Missing file for the -mod argument")
					exit()
		source_file = sys.argv[1]
		if (os.path.isfile(source_file) == False):
			print("Error '" + str(source_file) + "' is not a valid source file path")
			exit()
		compile_main()

init_script()
