# muupi

muupi is an Abstract Syntax Tree based Mutation Testing tool for Python 2.x. The motivation of muupi is to provide mutation testing support for TSTL project (https://github.com/agroce/tstl) by Dr. Alex Groce. Therefore, muupi also works as a module of TSTL. Besides TSTL, the current version of muupi also supports unittest framework, which is the built-in unit test framework of Python 2.x.

**Quick start**



For generating mutants for a target python file, go to _src_ directory and type the following command:

`python muupi.py  -m <fullname of target module> -p <target-file-path>/ -o <mutation-operator1>+<mutation-operator2>`

Here is a concrete sample for _avl.py_, which is located in the _sample_ directory

`-m sample.avl -p <file-path>/muupi/ -o AOR+AOD`

_-m_ option indicates the target module to mutate, and the fullname of the target module should be given.
_-p_ option is used to show the directory, in which the package _sample_ should be there.
_-o_ tells muupi the mutation operator information. At present, muupi supports 20 mutation operators. 
_--list-mutation-operators_ options can show all mutation operators that muupi supports. To show all of them, type `_python muupi.py --list-mutation-operators`.

After the mutant generation, the mutated copies of the original target _.py_ file are output to the _output_ folder along with the diff result.
