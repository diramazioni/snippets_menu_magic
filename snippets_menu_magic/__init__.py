 
""" Snippets menu magic 
    Let's you create menu directly from the notebook. 
    The menu elements can be snippets of code or internal/external links
"""
__version__ = '0.2'

from .snippets import SnippetsMenuMagic

def load_ipython_extension(ipython):
    sm = SnippetsMenuMagic(ipython)
    ipython.register_magics(sm)    
