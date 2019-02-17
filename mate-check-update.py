#!/usr/bin/env python3.7


#####################################################
#                                                   #
# This script is used to check for mate packages to #
# update in pkgsrc.                                 #
# Written by youri@NetBSD.org, Feb 17 2019          #
#                                                   #
#####################################################


import urllib.request
import re
import pprint
import sys
from bs4 import BeautifulSoup
from distutils.version import StrictVersion

#####################################################
#                                                   #
# Upstream Versions from the official Xfce Mirrors  #
#                                                   #
#####################################################

version = 1.21
base_url = 'http://pub.mate-desktop.org/releases/'

def get_links(link):
        pars = BeautifulSoup(urllib.request.urlopen(base_url+link),
                features='lxml')
        link = pars.body.find('table').find_all('a', href=True)
        return link
    
def filter_links(links):
        l = list(filter(lambda x: 
            x['href'] not in ['/src/', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A']
            and x.text != ''
            and x.text != 'Parent Directory', links))
        l.sort(key=lambda x: x.text)
        return l

def get_sublinks(link):
        links = filter_links(get_links(link))
        sublinks = []
        for l in links:
            sublinks.append(link + l['href'])
        return sublinks

def get_upstream_version(project):
        #project_versions = get_sublinks(project)

        # sort by project version
        #pv.sort(key=lambda x: StrictVersion(x.split("/")[2]))

        #try: last_version = pv[-1]
        #except IndexError: return # empty project

        #files_versions = get_sublinks(last_version)
        #return files_versions[-1]
        s = get_sublinks(base_url + version + '/')
        print(s)
        

#####################################################
#                                                   #
# Pkgsrc package versions from pkgsrc.se            #
#                                                   #
#####################################################

# match upstream names with pkgsrc names
packages = ["atril",
        "caja",
        "caja-dropbox",
        "caja-extensions",
        "engrampa",
        "eom",
        "libmatekbd",
        "libmateweather",
        "marco",
        "mate-applets",
        "mate-backgrounds",
        "mate-calc",
        "mate-common",
        "mate-control-center",
        "mate-desktop",
        "mate-icon-theme",
        "mate-icon-theme-faenza",
        "mate-indicator-applet",
        "mate-media",
        "mate-menus",
        "mate-netbook",
        "mate-notification-daemon",
        "mate-panel",
        "mate-polkit",
        "mate-power-manager",
        "mate-screensaver",
        "mate-sensors-applet",
        "mate-session-manager",
        "mate-settings-daemon",
        "mate-system-monitor",
        "mate-terminal",
        "mate-themes",
        "mate-user-share",
        "mate-utils",
        "mozo",
        "pluma"]

pkgsrcse = 'http://pkgsrc.se/search.php?so='
def get_package_version(name):
        pars = BeautifulSoup(urllib.request.urlopen(pkgsrcse+name),
                features='lxml')
        # get package line
        try: link = pars.body.find('div', {'id':'main'}).find_all('em')
        except IndexError: return ''
        # get bold text
        try: pars2 = BeautifulSoup(str(link[1]), features='lxml')
        except IndexError: return ''
        end = None
        # remove 'version '
        version = pars2.body.find('b').text[8:end]
        return version

def get_packages_pkgsrc_version():
        versions = {}
        for name in packages:
            versions[name] = get_package_version(name)
        return versions



#####################################################
#                                                   #
# Compare pkgsrc and upstream package versions      #
#                                                   #
#####################################################

print('Checking upstream versions...', file=sys.stderr)
#upstream = get_upstream_versions()
#upstream = {'xfwm4': 'url/xfwm4-4.4.4.tar.gz',
#            'catfish': 'url/catfish-1.0.0.tar.gz',
#            'xfce4-screenshooter': 'url/xfce4-screenshooter-10.0.tar.bz2',
#            'orage': 'url/orage-4.tar.gz'}
print('Checking local pkgrsc versions...', file=sys.stderr)
print('package name , pkgsrc version , upstream version , needs update')
#versions = get_packages_pkgsrc_version()
#print(versions)

#for name,version in versions.items():
#   print(name + ' ' + version)
up_version = get_upstream_version('eom')

#    if up is not None:
#        local = get_package_version(name)
#        if local == '':
#            print(name + ' , / , / , /')
#        else:
#            # extract versions, we expect two extension archives
#            lv = re.sub(r'nb[0-9]+', ' ', local).strip()
#            tv = up.split('/')[-1].split('-')[-1].split('.')
#            uv = '.'.join(tv[:len(tv)-2])
#            try : needsupdated = StrictVersion(lv) < StrictVersion(uv)
#            except: needsupdated = False
#            print(name + ' , ' + lv + ' , ' + uv + ' , ' +
#                    ('yes' if needsupdated else 'no') + ',')
#    else:
#        print(name + ' , / , / , /')
print('Done...', file=sys.stderr)
