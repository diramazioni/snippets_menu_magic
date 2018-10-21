
# Snippets Menu Magic
---

Introduction
===================

SnippetsMenuMagic is an IPython extension that let's you easly create menu directly from the notebook.

The menu elements can be snippets of code, internal/external links, markdown documents etc.

Is meant to be used with [Snippet Menu](https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/snippets_menu) that is part of [jupyter contrib nbextensions.](https://github.com/ipython-contrib/jupyter_contrib_nbextensions)

Installation
============

The package can be installed as follows:

    pip install snippets_menu_magic

After installation, the extension may be loaded within an IPython
session with :

    %load_ext snippets_menu_magic

This extension rely on [dpath](https://github.com/akesterson/dpath-python) to traverse the dictionary with xpath syntax. (it should be pulled automatically by pip)

It helps to also enable [Snippet Menu](https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/snippets_menu) extension to later see the results


Quick usage how-to
=============
Add a menu and a sub-menu

    %%snip_add usage/how-to
    this content will be pasted when the menu is clicked
    can be multiple lines too
Add a link

    %%snip_add bookmarks nbextensions -link
    https://github.com/ipython-contrib/jupyter_contrib_nbextensions    
Rename and place it as a top menu

    %snip_mv bookmarks/nbextensions top/bookmarks/nbextensions 
Search 

    s=%snip_search "**/*extensions"
    
Remove it

    %snip_rm usage/how-to
    
Please take a moment to read the [Guide](GUIDE.md) or better run the [GUIDE notebook](GUIDE.ipynb) locally and play with it

Development
===========

The latest release of the package may be obtained from
[GitHub](https://github.com/diramazioni/snippets_menu_magic/).

Author
======

This software was written and packaged by Eli Spizzichino

License
=======

This software is licensed under the 

[Apache 2.0
License](https://www.apache.org/licenses/LICENSE-2.0). 

