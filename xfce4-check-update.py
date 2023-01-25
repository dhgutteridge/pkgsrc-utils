#!/usr/bin/env python3.10


#####################################################
#                                                   #
# This script is used to check for xfce packages to #
# update in pkgsrc.                                 #
# Written by youri@NetBSD.org, Jan 17 2019          #
#                                                   #
#####################################################


import urllib.request
import re
import pprint
import sys
from bs4 import BeautifulSoup
from packaging.version import Version
from looseversion import LooseVersion

#####################################################
#                                                   #
# Upstream Versions from the official Xfce Mirrors  #
#                                                   #
#####################################################

categories = ['apps/', 'panel-plugins/', 'thunar-plugins/', 'xfce/']
base_url = 'https://archive.xfce.org/src/'

def get_links(link):
        pars = BeautifulSoup(urllib.request.urlopen(base_url+link),
                features='lxml')
        link = pars.body.find_all('a', href=True)
        return link
    
def filter_links(links):
        l = list(filter(lambda x: 
            x['href'] not in ['/src/', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '../']
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

def get_project_last_version(project):
        project_versions = get_sublinks(project)

        # filter non folders
        pv = list(filter(lambda x: x[-1] == '/', project_versions))

        # sort by project version
        pv.sort(key=lambda x: Version(x.split("/")[2]))

        try: last_version = pv[-1]
        except IndexError: return # empty project

        files_versions = get_sublinks(last_version)
        # Version doesn't handle version strings with four separate parts.
        files_versions.sort(key=lambda x: LooseVersion(re.search('\-([\d\.]+)\.',
                                                                 x.split("/")[3])[1]))
        return files_versions[-1]

def get_upstream_versions():
        upstream =  {}
        for category in categories:
            projects = get_sublinks(category)
            for project in projects:
                last_version = get_project_last_version(project)
                # get version without pkgrevision?
                upstream[project.split("/")[1]] = last_version
        return upstream

#####################################################
#                                                   #
# Pkgsrc package versions from pkgsrc.se            #
#                                                   #
#####################################################

# match upstream names with pkgsrc names
match = {'thunar':'xfce4-thunar',
        'thunar-archive-plugin': 'xfce4-thunar-archive',
        'thunar-media-tags': 'xfce4-thunar-media-tags',
        'thunar-vcs-plugin': 'xfce4-thunar-vcs',
        'xfconf': 'xfce4-conf',
        'xfdashboard': 'xfce4-dashboard',
        'xfdesktop': 'xfce4-desktop',
        'xfwm4': 'xfce4-wm',
        'orage': 'xfce4-orage',
        'tumbler': 'xfce4-tumbler',
        'sion': 'xfce4-sion',
        'squeeze': 'xfce4-squeeze',
        'garcon': 'xfce4-garcon',
        'exo': 'xfce4-exo'
        }
pkgsrcse = 'http://pkgsrc.se/search.php?so='
def get_package_version(name):
        if name in match:
            name = match[name]
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


#####################################################
#                                                   #
# Compare pkgsrc and upstream package versions      #
#                                                   #
#####################################################

print('Checking upstream versions...', file=sys.stderr)
upstream = get_upstream_versions()
#upstream = {'xfwm4': 'url/xfwm4-4.4.4.tar.gz',
#            'catfish': 'url/catfish-1.0.0.tar.gz',
#            'xfce4-screenshooter': 'url/xfce4-screenshooter-10.0.tar.bz2',
#            'orage': 'url/orage-4.tar.gz'}
print('Checking local pkgrsc versions...', file=sys.stderr)
print('package name , pkgsrc version , upstream version , needs update')
for name,up in upstream.items():
    if up is not None:
        local = get_package_version(name)
        if local == '':
            print(name + ' , / , / , /')
        else:
            # extract versions, we expect two extension archives
            lv = re.sub(r'nb[0-9]+', ' ', local).strip()
            tv = up.split('/')[-1].split('-')[-1].split('.')
            uv = '.'.join(tv[:len(tv)-2])
            # Version doesn't handle version strings with four separate parts.
            try : needsupdated = LooseVersion(lv) < LooseVersion(uv)
            except: needsupdated = False
            print(name + ' , ' + lv + ' , ' + uv + ' , ' +
                    ('yes' if needsupdated else 'no') + ',')
    else:
        print(name + ' , / , / , /')
print('Done...', file=sys.stderr)
print('Don\'t forget to check elementary-xfce-icon-theme: https://github.com/shimmerproject/elementary-xfce, pkgsrc version is ' + get_package_version('elementary-xfce-icon-theme'), file=sys.stderr)
