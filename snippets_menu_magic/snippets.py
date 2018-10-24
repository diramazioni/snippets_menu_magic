# %load snippets_menu_magic/snippets.py

from IPython.core.magic import (
    Magics, magics_class, cell_magic, line_magic
)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring
)
import os
import json
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
        shell.user_ns['__menu'] = self._menu
        self.default_menu = []

        self.reserved = ('snippet', 'internal-link', 'external-link',
                         'menu-direction', 'sub-menu-direction')
        self._dump_path = os.path.join(
            os.path.expanduser("~"), '.jupyter', 'custom')
        if '__file__' in globals():
            self._module_path = os.path.abspath(os.path.dirname(__file__))
        else:
            self._module_path = os.path.join(os.path.abspath(
                os.getcwd()), 'snippets_menu_magic')  # interactive load

    def dict2list(self, src_dict):
        dest = []
        for menu, d in src_dict.items():
            #         print("%s -> %s"% (menu,d))
            dmenu = {}
            dmenu.update(d)  # copy all from the source dict
            sub_menu_ = {}
            for sub, v in d.items():
                if sub not in self.reserved:
                    sub_menu_[sub] = v
                    # remove the menu that is going to be a sub-menu
                    del dmenu[sub]
            if len(sub_menu_):
                dmenu["sub-menu"] = self.dict2list(sub_menu_)
            dmenu['name'] = menu
            dest.append(dmenu)
        return dest

    def _is_leaf_node(self, dict_):
        for k in dict_.keys():
            if k in self.reserved:
                return False
        return True

    def _get_path(self, path=None):
        if path:
            try:
                dump = dpath.util.get(self._menu, path)
            except KeyError:
                print("Can't find", path)
                return None
        else:
            dump = self._menu.copy()
        return dump

    def _format_filter_results(self, results):
        result_keys = []
        for p, r in results:  # get the entire snippet not just the pertaining line
            result_keys.append(('/').join(p.rsplit('/')[:-1]))
        for r in result_keys:
            print("\n-> %s " % r)
            print(('\n').join(dpath.util.get(self._menu, r)))

    def _format_results(self, results):
        for p, r in results:
            if isinstance(r, dict):
                if not self._is_leaf_node(r):
                    print("/%s" % p)
                self._format_results(r.items())
            elif isinstance(r, str):
                print('\n' + '-' * 20)
                print(r)
            else:  # is a list
                print('\n' + '-' * 20)
                print(('\n').join(r))
                print('=' * 20)

    def _format_path(self, path):
        if isinstance(path, str):
            #             print("->", path)
            return dequote(path)
        else:
            #             print("[]>", path)
            path = [dequote(menu) for menu in path]
            if len(path) == 1:
                path = path[0]
            return path

    def _dump(self, path=None):
        pre = '''
requirejs(["nbextensions/snippets_menu/main"], function (snippets_menu) {
    console.log('Loading `snippets_menu` customizations from `custom.js`');
    ''' + ('\n    ').join(self.default_menu) + '''
    snippets_menu.options['menus'] = snippets_menu.default_menus;
    var horizontal_line = '---';
    snippets_menu.options['menus'][0]['sub-menu'].push(horizontal_line);
'''
        # To-do: add the option to remove the default menu completely
        post = '''
});
'''
        fpath = os.path.join(self._dump_path, 'custom.js')
        dump = self._get_path(path)
        if not dump:
            return
        if 'top' in dump:
            top = dump['top']
            del dump['top']
            _have_top = True
        else: _have_top = False
        #         print("Writing ", fpath)
        with open(fpath, 'w') as file:
            file.write(pre)
            if _have_top:  # insert as a top menu
                for m in self.dict2list(top):
                    file.write("    snippets_menu.options['menus'].push(%s);\n" % m)
            for m in self.dict2list(dump):
                # insert as a normal submenu of Snippets
                file.write("    snippets_menu.options['menus'][0]['sub-menu'].push(%s);\n" % m)
            file.write(post)

    def _dump_json(self, path=None, fname='menu.json', debug=False):
        fpath = os.path.join(self._dump_path, fname)
        dump = self._get_path(path)
        if not dump:
            return
        print("writting ", fname)
        with open(fpath, 'w') as file:
            if not debug:
                json.dump(dump, file, indent=4)
            else:
                json.dump(self.dict2list(dump), file, indent=4)

    def _load_json(self, path=None, fname='menu.json', append=False):
        with open(fname) as file:
            if append:
                dpath.util.merge(self._menu, json.load(
                    file), flags=dpath.util.MERGE_REPLACE)
                # self._menu.update(json.load(file))
            elif path:
                dpath.util.new(self._menu, path, json.load(file))
            else:
                self._menu = json.load(file)

    @line_magic
    @magic_arguments()
    @argument('-f', '--file', help='file.json to load the menu from', default='menu.json',  nargs='?')
    @argument('path', help='path glob of the destination menu', nargs='?')
    @argument('-a', help='append to the current menu without changing existing values', default=False, action='store_true')
    def snip_load(self, line):
        ''' Load the menu from json '''
        args = parse_argstring(self.snip_load, line)
        path = self._format_path(args.path) if args.path else None
        if args.file:
            for p in [os.path.join(self._dump_path, args.file),
                      os.path.join(self._module_path, args.file)]:
                if os.path.exists(p):
                    self._load_json(path=path, fname=p, append=args.a)
                    return
            return "File not found %s" % args.file
        self._load_json(path=path, fname=os.path.join(
            self._module_path, 'menu.json'), append=args.a)

    @line_magic
    @magic_arguments()
    @argument('-f', '--file', help='file.json to dump the menu to', default='menu.json',  nargs='?')
    @argument('path', help='path glob of the source menu', nargs='?')
    def snip_dump(self, line):
        ''' Dump the menu to custom.js and to menu.json (if file is not provided) '''
        args = parse_argstring(self.snip_dump, line)
        path = self._format_path(args.path) if args.path else None
        self._dump(path=path)
        if args.file:
            fname = args.file[0] if isinstance(args.file, list) else args.file
            self._dump_json(path=path, fname=fname)
        else:
            self._dump_json(path=path)

    @cell_magic
    @magic_arguments()
    @argument('path', help='path glob of the menu', nargs='+')
    @argument('-ilink', '--internal-link', help='add an internal link instead of a snippet', default=False, action='store_true')
    @argument('-link', '--external-link', help='add an external link instead of a snippet', default=False, action='store_true')
    @argument('--menu-direction', help='define the direction of the menu CURRENTLY NOT WORKING', default=False, action='store_true')
    @argument('--sub-menu-direction', help='define the direction of the sub-menu CURRENTLY NOT WORKING', default=False, action='store_true')
    def snip_add(self, line, cell):
        """
              inset a new menu in the tree
              The path must be a unique path rappresenting the menu tree structure
              The path will replace eventually preexisting nodes
              and will create all the intermidiate node (like mkdir -p)
              The path can be a list of separate words like
              %snip_add  test_menu "sub menu" "dive deep"
              or with a path like syntax
              %snip_add  test_menu/sub_menu/"dive deep"
        """

        args = parse_argstring(self.snip_add, line)
        # print(args)
        path = self._format_path(args.path) if args.path else None
        for r in self.reserved:
            if r in path:
                raise Exception(
                    "Can't use %s because it is a reserved keyword" % r)
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
        dpath.util.new(self._menu, path, new)

        self._dump()
        # self._dump_json()

    @line_magic
    def snip_load_test(self, line):
        self._load_json(fname='test3.json', append=False)

    @line_magic
    def snip_clear(self, line):
        """ remove all """
        self._menu = {}

    def _printJson(self, dict_):
        print(json.dumps(dict_, indent=4))

    @line_magic
    def snip_show(self, line):
        """ show all """
        self._printJson(self._menu)

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
        splice = "snippets_menu.default_menus[0]['sub-menu'].splice(%s, %s);" % (
            start, times)
        self.default_menu.append(splice)
        self._dump()

    @line_magic
    @magic_arguments()
    @argument('path', help='path glob of the menu', nargs='+')
    def snip_rm(self, line):
        """ remove the menu that match the given glob """
        args = parse_argstring(self.snip_rm, line)
        path = self._format_path(args.path) if args.path else None
        try:
            rows = dpath.util.delete(self._menu, path)
            print("deleted ", rows)
        except dpath.exceptions.PathNotFound as e:
            print("Path not found \n%s" % e)
            return
        self._dump()
        # self._dump_json()

    @line_magic
    @magic_arguments()
    @argument('src', help='source menu path', nargs='+')
    @argument('dst', help='destination menu path', nargs='+')
    def snip_mv(self, line):
        """
        %snip_mv src_path dest_path
        rename/move a menu with the given path to a new path """
        args = parse_argstring(self.snip_mv, line)
        src_path = self._format_path(args.src) if args.src else None
        dst_path = self._format_path(args.dst) if args.dst else None
        try:
            results = list(dpath.util.search(self._menu, src_path, yielded=True))
            for path, src_ in results:
                new_dst = dst_path + '/' + path.rsplit('/')[-1:][0]
                dpath.util.new(self._menu, new_dst, src_)
                dpath.util.delete(self._menu, path)
        except dpath.exceptions.PathNotFound as e:
            print("Path not found \n%s" % e)
            return
        self._dump()
        # self._dump_json()

    @line_magic
    @magic_arguments()
    @argument('path', help='path glob of the menu', nargs='?')
    def snip_get(self, line):
        ''' return the value for the menu matching the given glob '''
        args = parse_argstring(self.snip_get, line)
        path = self._format_path(args.path) if args.path else None
        return dpath.util.get(self._menu, path)
    @line_magic
    def snip_get_all(self, line):
        ''' return the value for the menu matching the given glob '''
        return self._menu

    @line_magic
    @magic_arguments()
    @argument('path', help='path glob of the menu', nargs='+')
    @argument('-f', '--filter', help='filter the result containing this string', nargs='?')
    def snip_subset(self, line):
        """
            returns a menu subset with the given path glob and string filter
        """
        args = parse_argstring(self.snip_subset, line)
        path = self._format_path(args.path) if args.path else None
        if args.filter:
            print("Filter: %s" % args.filter)
            results = dpath.util.search(
                self._menu, path, afilter=lambda x: args.filter in str(x))
        else:
            results = dpath.util.search(self._menu, path)
        return results

    @line_magic
    @magic_arguments()
    @argument('path', help='%snip_search "a/b/[cd]"', nargs='+')
    @argument('-f', '--filter', help='filter the result containing this string', nargs='?')
    def snip_search(self, line):
        """
            search the menu content with the given path glob and string filter.
            returns a generator with the results and print out
        """
        args = parse_argstring(self.snip_search, line)
        path = self._format_path(args.path) if args.path else None
        if args.filter:
            print("Filter: %s" % args.filter)
            results = list(dpath.util.search(self._menu, path, yielded=True, afilter=lambda x: args.filter in str(x)))
            self._format_filter_results(results)
        else:
            results = list(dpath.util.search(self._menu, path, yielded=True))
            self._format_results(results)
        return results

# get_ipython().register_magics(SnippetsMenuMagic)


def load_ipython_extension(ipython):
    sm = SnippetsMenuMagic(ipython)
    ipython.register_magics(sm)
