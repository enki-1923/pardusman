#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# System
import sys
import time


class ExPisiIndex(Exception):
    pass

class ExIndexBogus(ExPisiIndex):
    pass

class ExPackageMissing(ExPisiIndex):
    pass

class ExPackageCycle(ExPisiIndex):
    pass




def maker(op, project_file, work_dir, repo_base_url):
    from repotools import maker, project

    project = project.Project()

  
    err = project.open(project_file, work_dir, repo_base_url)
    if err:
        print "ERROR: %s" % err
        return


    start = time.time()



    if op == "make" or op == "make-repo":
        update_repo = True
        while True:
            try:
                project.get_repo(update_repo=update_repo)
            except ExIndexBogus, e:
                print "ERROR: Unable to load package index. URL is wrong, or file is corrupt."
                return
            except ExPackageCycle, e:
                cycle = " > ".join(e.args[0])
                print "ERROR: package index has errors. Cyclic dependency found:\n  %s." % cycle
                return
            except ExPackageMissing, e:
                print "ERROR: Package index has errors. '%s' depends on non-existing '%s'." % e.args
                return
            missing_components, missing_packages = project.get_missing()
            if len(missing_components):
                print "WARNING: There are missing components. Removing."
                for component in missing_components:
                    if component in project.selected_components:
                        project.selected_components.remove(component)
                update_repo=False
            if len(missing_packages):
                print "WARNING: There are missing packages. Removing."
                for package in missing_packages:
                    if package in project.selected_packages:
                        project.selected_packages.remove(package)
                update_repo=False
            break

        maker.make_repos(project)
    if op == "check-repo":
        maker.check_repo_files(project)
    if op == "make" or op == "make-live":
        maker.make_image(project)
    # install-live
    # configure-live
    if op == "make" or op == "make-live" or op == "pack-live":
        maker.squash_image(project)
    if op == "make" or op == "make-iso":
        maker.make_iso(project)

    end = time.time()
    print "Total time is", end - start, "seconds."


def usage(app):
    print "Usage: %s [command] path/to/project.xml" % app
    print
    print "Commands:"
    print "  make-repo  : Make local repos"
    print "  check-repo : Check repo files"
    print "  make-live  : Install image & make squashfs"
    print "  pack-live  : Make squashfs"
    print "  make-iso   : Make ISO"
    print "  make       : Make all!"

def main(args):
    if len(args) == 2 and args[1] in ["help", "-h", "--help"]:
        usage(args[0])
    else:
        maker(args[1], args[2], args[3], args[4])

if __name__ == '__main__':
    sys.exit(main(sys.argv))
