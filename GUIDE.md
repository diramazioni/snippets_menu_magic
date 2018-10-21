
# Introduction

In order to use this extention it needs to be loaded with

    %load_ext snippets_menu_magic

Any time you want to see the help for a function use the `?` :

    %%snip_add?
    %snip_search?

# Add a nested snippet menu

A nested menu can be created or replaced on the fly even if the parent tree is not present already (like mkdir -p /new/path)

If a value is alread present it will be replaced with the new one


```python
%%snip_add "testone/bar/sub/sub2"
sub-leaf
```

# Show

show the stored json menu niceley formatted


```python
%snip_show
```

    {
        "testone": {
            "bar": {
                "sub": {
                    "sub2": {
                        "snippet": [
                            "sub-leaf"
                        ]
                    }
                }
            }
        }
    }


# Add

Paths can be specified also using separate words and, as long as they don't contains spaces, quotes can be ommited


```python
%%snip_add testone bar
leaf
etc
```


```python
%%snip_add testone/bar2
leaf and flower
etc foo
```


```python
%%snip_add "testone/bar 3"
etcetc
```

But **not** this. This will **not** error but will produces invalid keys

    %%snip_add testone/"bar 3"


### Don't use reserved name  'snippet', 'internal-link', 'external-link', 'menu-direction', 'sub-menu-direction'
this will error

    %%snip_add magic add snippet

## All the menu under **top** will appear as a top menu. 


## Add external link   


```python
%%snip_add top bookmarks snippets_menu_magic -link
https://github.com/diramazioni/snippets_menu_magic
```


```python
%%snip_add top bookmarks nbextensions -link
https://github.com/ipython-contrib/jupyter_contrib_nbextensions
```

## internal-link
    %%snip_add bookmarks -ilink

# Dump

The custom.js is written every time a menu is add or removed so a simple refresh of the page should show the menu under Snippets

The menu.json (the default menu) or the user specified json is written only with dump. 

A source path to export can be provided exporting only the child of that node

### Dump the default menu


```python
%snip_dump
```

    writting  menu.json


Let's save the bookmarks in a separate file


```python
%snip_dump -f bookmarks.json top/bookmarks
```

    writting  bookmarks.json


# Load


```python
%snip_load -f bookmarks.json top/fav
#%snip_show
```

# Remove


```python
%snip_rm top/bookmarks
```

    deleted  1



```python
#%snip_show
```

# Move / rename


```python
%snip_mv top/fav top/bookmarks
```

# Search

You can search by menu name and content in two ways:

- %snip_search _'pretty'_ prints the results and returns an iteratable to further explore the results
- %snip_subset returns a subset of the original dictionary containing the results

search at all levels a menu called _bar_


```python
%snip_search "**/bar"
```

    /testone/bar
    
    --------------------
    leaf
    etc
    ====================





    [('testone/bar', {'snippet': ['leaf', 'etc']})]



search at all levels a menu that starts with _bar_ and save the result in `s`


```python
s=%snip_search "**/bar*"
```

    /testone/bar
    
    --------------------
    leaf
    etc
    ====================
    /testone/bar2
    
    --------------------
    leaf and flower
    etc foo
    ====================
    /testone/bar 3
    
    --------------------
    etcetc
    ====================


search any menu at all levels for the ones containing the string `etc` as a cell content


```python
s=%snip_search "**" -f etc
```

    Filter: etc
    
    -> testone/bar/snippet 
    leaf
    etc
    
    -> testone/bar2/snippet 
    leaf and flower
    etc foo
    
    -> testone/bar 3/snippet 
    etcetc


## Hacking
since the internal (dpath) menu dictionary is exposed in the user space as `__menu` you can operate directly with dpath and build your custom filter. 

The previous query `s = %snip_search "**" -f etc` is equivalent to
    
    s = dpath.util.search(__menu, '**', afilter=lambda x: 'etc' in str(x))
in both cases returns an iteratable that can be used to treat the result:

Unfortunatly, as far as I know, with ipython's magics that use argparse, you can't pass a variable value so you **can't** do expression like:

    for k,v in s:
        %snip_rm k
but is possible to directly use dpath

    for k,v in s:
        dpath.util.delete(__menu, k)

## Subset

Accepts the same parameter as search but returns a dictionary with the results of the search


```python
import json
sub=%snip_subset "**" -f etc
print(json.dumps(sub, indent=4))
```

    Filter: etc
    {
        "testone": {
            "bar": {
                "snippet": [
                    "etc"
                ]
            },
            "bar2": {
                "snippet": [
                    "etc foo"
                ]
            },
            "bar 3": {
                "snippet": [
                    "etcetc"
                ]
            }
        }
    }


# Clear

clear the current menu from the memory

    %snip_clear

# Remove elements from the default menu


```python
%snip_slice_default 3 1
```


```python
%snip_slice_default 4 3 
```

# Develop it further

This software has been quickly written to fulfil my personal needs for a simple solution to manage snippets, bookmarks etc using the Snippets menu in jupyter notebooks, but it can be potentially useful even without the menu. You can use it as is to keep truck of things, or it can be further extended to do any sort of crazy stuff. 

To develop it I've followed the [K.I.S.S. principles](https://en.wikipedia.org/wiki/KISS_principle) and I'm open to any resonable suggestions via the issue tracker or pull requests

In order to quick test changes in this module you can load the module source directly in this notebook, make changes and then register. 

At this point the changes are in the working kernel and can be tested in the current notebook without reloading (but the dictionary will be empty)

Once the changes are stable you can write back to the module file and reload the extension in other notebooks.

First clone this repo localy and, in the working dir, have it installed with

    flit install -s
### load the module source in this notebook
    %load snippets_menu_magic/snippets.py
### register in the current ipython kernel 
    get_ipython().register_magics(SnippetsMenuMagic)
### write back the changes  in the module
    %%writefile snippets_menu_magic/snippets.py
### reload the extension from other notebooks
    %reload_ext snippets_menu_magic


## Code


```python
#%%writefile snippets_menu_magic/snippets.py
#%load snippets_menu_magic/snippets.py

```


```python
#%%load snippets_menu_magic/nb_register.py
#get_ipython().register_magics(SnippetsMenuMagic)
```
