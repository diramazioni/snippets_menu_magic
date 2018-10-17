from IPython.core.magic import  (
    Magics, magics_class, cell_magic, line_magic
)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)    
import os, json, argparse
import dpath.util


def dequote(s):
    """  If a string has single or double quotes around it, remove them  """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s

@magics_class
class SnippetsMenuMagic(Magics):
    def __init__(self, shell=None,  **kwargs):
        super().__init__(shell=shell, **kwargs)
        self._menu = {}
        self._dump_path = os.path.join(os.path.expanduser("~"), '.jupyter', 'custom')
        self.default_menu = []
        #shell.user_ns['__menu'] = self._menu
        self.reserved = ('snippet', 'internal-link', 'external-link', 'menu-direction', 'sub-menu-direction')
    
    def dict2list(self, src_dict):    
        
        dest = []
        for menu, d in src_dict.items():
    #         print("%s -> %s"% (menu,d))
            dmenu = {}
            dmenu.update(d) # copy all from the source dict
            sub_menu_ = {}
            for sub, v in d.items():
                if sub not in self.reserved:
                    sub_menu_[sub] = v
                    del dmenu[sub] # remove the menu that is going to be a sub-menu
            if len(sub_menu_):
                dmenu["sub-menu"] = self.dict2list(sub_menu_)
            dmenu['name'] = menu
            dest.append(dmenu)
        return dest
                
    @line_magic
    def snip_load_test(self, line):
        self._load_json(fname='test3.json', append=False)
        
    @line_magic
    @magic_arguments()
    @argument('file', help='file.json to load the menu from', default='menu.json',  nargs='?')
    @argument('-a', help='append to the current menu without changing existing values', default=False, action='store_true')    
    def snip_load(self, line):
        ''' Load the menu from json '''
        args = parse_argstring(self.snip_load, line)
        #print("fname=%s, append=%s" % (args.file, args.a))
        self._load_json(fname=args.file, append=args.a)
        
    @line_magic
    def snip_clear(self, line):
        """ remove all """
        self._menu = {}
    @line_magic
    def snip_show(self, line):
        """ show all """
        print(json.dumps(self._menu, indent=4))
        
    @line_magic
    def snip_show_custom(self):
        """show custom.js """
        fpath = os.path.join(self._dump_path, 'custom.js')
        with open(fpath) as file: 
            data = file.read() 
            print(data)
            
    @line_magic
    def snip_slice_default(self, line):
        start, times = line.split()
        splice = "snippets_menu.default_menus[0]['sub-menu'].splice(%s, %s);" % (start, times)
        self.default_menu.append(splice)
        self._dump()
        
    @line_magic
    @magic_arguments()
    @argument('-top', help='append to the current menu without changing existing values', default=False, action='store_true')        
    @argument('file', help='file.json to dump the menu to', default='menu.json',  nargs='*')
    def snip_dump(self, line):
        ''' Dump the menu to custom.js '''
        args = parse_argstring(self.snip_dump, line)        
        self._dump(topmenu=args.top)
        if args.file:
            fname = args.file if isinstance(args.file, str) else args.file[0]
            if not len(fname): fname = 'menu.json'
            self._dump_json(fname = fname)
        else: self._dump_json()

    def _dump(self, topmenu=False):
        pre = '''
requirejs(["nbextensions/snippets_menu/main"], function (snippets_menu) {
    console.log('Loading `snippets_menu` customizations from `custom.js`');
    '''+('\n    ').join(self.default_menu)+'''
    snippets_menu.options['menus'] = snippets_menu.default_menus;
    var horizontal_line = '---';
    snippets_menu.options['menus'][0]['sub-menu'].push(horizontal_line);
'''
        post = '''
});
'''       
        fpath = os.path.join(self._dump_path, 'custom.js')
#         print("Writing ", fpath)
        with open(fpath, 'w') as file: 
            file.write(pre)
            for m in self.dict2list(self._menu):
                if not topmenu:
                    file.write("    snippets_menu.options['menus'][0]['sub-menu'].push(%s);\n" % m)
                else:
                    file.write("    snippets_menu.options['menus'].push(%s);\n" % m)
            file.write(post)
        
        #self.snip_show_custom()
    def _dump_json(self, fname='menu.json', debug=False):
        print("writting ", fname)
        fpath = os.path.join(self._dump_path, fname)
        with open(fpath, 'w') as file: 
            if debug:
                json.dump(self.dict2list(self._menu), file, indent=4)
            else :
                json.dump(self._menu, file, indent=4)
    def _load_json(self, fname='menu.json', append=False):
        fpath = os.path.join(self._dump_path, fname)
        with open(fpath) as file:
            if append:
                dpath.util.merge(self._menu, json.load(file), flags=dpath.util.MERGE_REPLACE)
                #self._menu.update(json.load(file))
            else:
                self._menu = json.load(file)


    @cell_magic
    @magic_arguments()
    @argument('path', help='%%snip_add menu [sub menu] [sub sub menu] [etc]', nargs='+' )    
    @argument('--internal-link', help='add an internal link instead of a snippet', default=False, action='store_true')
    @argument('--external-link', help='add an external link instead of a snippet', default=False, action='store_true')
    @argument('--menu-direction', help='define the direction of the menu') 
    @argument('--sub-menu-direction', help='define the direction of the sub-menu')
    def snip_add(self, line, cell):
        """   
              inset a new menu in the tree 
              menu is a path glob expression for the menu tree structure 
              The node tree is created or replaced with this node the path can be a list of separate words like 
              %snip_add  test_menu "sub menu" "dive deep" 
              or with a path like syntax 
              %snip_add  test_menu/sub_menu/"dive deep" 
        """        

        args = parse_argstring(self.snip_add, line)
        #print(args)
        menus = [dequote(menu) for menu in args.path]
        for r in self.reserved: 
            if r in menus: 
                raise Exception("Can't use %s because is reserved" % r )
        content = cell.split('\n')
        if args.internal_link:
            new = {'internal-link': content[0]}
        elif args.external_link:
            new = {'external-link': content[0]}
        elif args.menu_direction:
            new = {'menu-direction': content[0]}
        elif args.sub_menu_direction:
            new = {'sub-menu-direction': content[0]}
        else:
            new = {"snippet": content}
        dpath.util.new(self._menu, menus, new)
        
        self._dump()
        #self._dump_json()            
    
    @line_magic
    @magic_arguments()
    @argument('path', help='%snip_rm menu [sub menu] [sub sub menu] [etc]', nargs='+' )    
    def snip_rm(self, line):
        """ remove the menu with the given path """
        args = parse_argstring(self.snip_rm, line)
        menus = [dequote(menu) for menu in args.path]
        try:
            dpath.util.delete(self._menu, menus)
        except dpath.exceptions.PathNotFound as e:
            print("Path not found \n%s" % e)
            return
        self._dump()
        #self._dump_json()
        
    @line_magic
    @magic_arguments()
    @argument('src_path', help='source path', nargs='+' )    
    @argument('dst_path', help='destination path', nargs='+' )    
    def snip_mv(self, line):
        """ 
        %snip_mv src_path dest_path
        rename/move a menu with the given path to a new path """
        args = parse_argstring(self.snip_mv, line)
        src_path = [dequote(menu) for menu in args.src_path]
        dst_path = [dequote(menu) for menu in args.dst_path]
        if len(src_path) == 1: src_path = src_path[0] 
        if len(dst_path) == 1: dst_path = dst_path[0] 
        
        try:
            for src_ in dpath.util.values(self._menu, src_path):
                dpath.util.new(self._menu, dst_path, src_)
            dpath.util.delete(self._menu, src_path)
        except dpath.exceptions.PathNotFound as e:
            print("Path not found \n%s" % e)
            return
        self._dump()
        #self._dump_json()

#get_ipython().register_magics(SnippetsMenuMagic)
def load_ipython_extension(ipython):
    sm = SnippetsMenuMagic(ipython)
    ipython.register_magics(sm)
