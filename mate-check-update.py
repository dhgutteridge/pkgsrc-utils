#!/usr/bin/env python3.7


#####################################################
#                                                   #
# This script is used to check for MATE packages to #
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
# Upstream Versions from the official MATE Mirrors  #
#                                                   #
#####################################################

base_url = 'http://pub.mate-desktop.org/releases/'
extension = '.tar.xz'
mate_release = 26

def get_links(link):
        req = urllib.request.Request(base_url+link,
            headers={'User-Agent' : "Magic Browser"})
        pars = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        link = pars.body.find_all('a', href=True)
        return link
    
def get_most_recent(link, name):
        links = get_links(link)
        l = list(filter(lambda x: 
            x['href'] not in ['?C=N&O=D', '?C=S&O=D', '?C=M&O=D', '?C=N&O=D',
                '?C=N&O=A', '?C=M&O=A', '?C=S&O=A', 'SHA1SUMS', '../'] and
            x.text.startswith(name) and
            x.text.count('-') - 1 == name.count('-') and not
            x.text.endswith('.sha256sum'), links))
        l.sort(key=lambda x: x.text)
        if len(l) == 0:
            return ''
        return l[-1].text.replace(extension, '').replace(name + '-', '')

def get_upstream_version(v, project):
        s = get_most_recent('1.' + str(v) + '/', project)
        if s == '':
            s = get_upstream_version(v-1, project)
        return s
        

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

def get_pkgsrc_version():
        versions = {}
        for name in packages:
            versions[name] = get_package_version(name)
        return versions



#####################################################
#                                                   #
# Compare pkgsrc and upstream package versions      #
#                                                   #
#####################################################

print('package name , pkgsrc version , upstream version , needs update')
versions = get_pkgsrc_version()
for name,uv in versions.items():
    lv = get_upstream_version(mate_release, name)
    # extract versions, we expect two extension archives
    uv = re.sub(r'nb[0-9]+', ' ', uv).strip()
    try : needsupdated = StrictVersion(lv) > StrictVersion(uv)
    except: needsupdated = False
    print(name + ' , ' + uv + ' , ' + lv + ' , ' +
            ('yes' if needsupdated else 'no'))
print('Done...', file=sys.stderr)
print('Don\'t forget to check mate-themes: http://pub.mate-desktop.org/releases/themes/, pkgsrc version is ' + get_package_version('mate-theme'), file=sys.stderr)
