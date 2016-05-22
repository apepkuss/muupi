

import sys


class VirtualModule(object):

   def hello(self):
      return 'Hello World!'


class CustomImporter(object):

   virtual_name = 'my_virtual_module'

   def find_module(self, fullname, path):
      """This method is called by Python if this class
         is on sys.path. fullname is the fully-qualified
         name of the module to look for, and path is either
         __path__ (for submodules and subpackages) or None (for
         a top-level module/package).

         Note that this method will be called every time an import
         statement is detected (or __import__ is called), before
         Python's built-in package/module-finding code kicks in."""

      if fullname ==  self.virtual_name:

         # As per PEP #302 (which implemented the sys.meta_path protocol),
         # if fullname is the name of a module/package that we want to
         # report as found, then we need to return a loader object.
         # In this simple example, that will just be self.

         return self

      # If we don't provide the requested module, return None, as per
      # PEP #302.

      return None

   def load_module(self, fullname):
      """This method is called by Python if CustomImporter.find_module
         does not return None. fullname is the fully-qualified name
         of the module/package that was requested."""

      if fullname != self.virtual_name:
         # Raise ImportError as per PEP #302 if the requested module/package
         # couldn't be loaded. This should never be reached in this
         # simple example, but it's included here for completeness. :)
         raise ImportError(fullname)

      # PEP#302 says to return the module if the loader object (i.e,
      # this class) successfully loaded the module.
      # Note that a regular class works just fine as a module.
      return VirtualModule()


if __name__ == '__main__':

   # Add our import hook to sys.meta_path
   sys.meta_path.append(CustomImporter())

   # Let's use our import hook
   import my_virtual_module
   print my_virtual_module.hello()
