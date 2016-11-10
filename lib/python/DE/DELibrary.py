from Components.MenuList import MenuList
from Tools.Directories import fileExists
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from enigma import eListboxPythonMultiContent, eListbox, gFont
from Components.config import config
from os import system, statvfs, popen
from Tools.HardwareInfo import HardwareInfo
from Tools.LoadPixmap import LoadPixmap

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)

    return text


def parse_ecm(filename):
    addr = caid = pid = provid = port = provider = txsystem = using = source = reader = ''
    ecmtime = hops = 0
    try:
        file = open(filename)
        for line in file.readlines():
            line = line.strip()
            if line.find('CaID') >= 0:
                x = line.split(' ')
                caid = x[x.index('CaID') + 1].split(',')[0].strip()
            elif line.find('caid') >= 0:
                x = line.split(':', 1)
                caid = x[1].strip()
            if line.find('pid:') >= 0:
                x = line.split(':', 1)
                pid = x[1].strip()
            elif line.find('pid') >= 0:
                x = line.split(' ')
                pid = x[x.index('pid') + 1].strip()
            if line.find('prov:') >= 0:
                x = line.split(':', 1)
                provid = x[1].strip().split(',')[0]
            elif line.find('provid:') >= 0:
                x = line.split(':', 1)
                provid = x[1].strip()
            if line.find('provider:') >= 0:
                x = line.split(':', 1)
                provider = x[1].strip()
            if line.find('system:') >= 0:
                x = line.split(':', 1)
                txsystem = x[1].strip()
            if line.find('msec') >= 0:
                x = line.split(' ', 1)
                ecmtime = int(x[0].strip())
            elif line.find('ecm time:') >= 0:
                x = line.split(':', 1)
                ecmtime = int(float(x[1].strip()) * 1000)
            if line.find('hops:') >= 0:
                x = line.split(':', 1)
                hops = int(x[1].strip())
            if line.find('using:') >= 0:
                x = line.split(':', 1)
                using = x[1].strip()
            elif line.find('system:') >= 0:
                x = line.split(':', 1)
                protocol = x[1].strip()
            if line.find('address:') >= 0:
                x = line.split(':')
                try:
                    addr = x[1].strip()
                    port = x[2].strip()
                except:
                    addr = x[1].strip()

            elif line.find('source:') >= 0:
                x = line.split(':')
                if x[1].find('net') >= 0:
                    try:
                        addr = x[1].strip()
                        port = x[2].strip().replace(')', '')
                    except:
                        addr = x[1].strip()

                else:
                    addr = x[1].strip()
            elif line.find('from:') >= 0:
                x = line.split(':', 1)
                addr = x[1].strip()
            if line.find('reader') >= 0:
                x = line.split(':')
                reader = x[1].strip()

        file.close()
        return (caid,
         pid,
         provid,
         provider,
         txsystem,
         ecmtime,
         hops,
         using,
         source,
         addr,
         port,
         reader)
    except:
        return 0


class Tool:

    def readEmuName(self, emu):
        try:
            f = open('/usr/script/' + emu + '_em.sh', 'r')
            for line in f.readlines():
                if line.find('#emuname=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return emu
        except:
            return 'None'

    def readSrvName(self, srv):
        try:
            f = open('/usr/script/' + srv + '_cs.sh', 'r')
            for line in f.readlines():
                if line.find('#srvname=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return srv
        except:
            return 'None'

    def reverse_date(self, date):
        return date[len(date) - 2:] + '-' + date[4:6] + '-' + date[:4]

    def enigma_version(self):
        try:
            return popen('opkg list | grep "enigma2 - 3."| cut -d"-" -f2,3,4', 'r').read()
        except:
            return 'Unknow'

    def driver_version(self):
        try:
            return popen('opkg list | grep dreambox-dvb-module | cut -d"-" -f6,7', 'r').read()
        except:
            return 'Unknow'

    def readEcmInfoFile(self, emu):
        try:
            f = open('/usr/script/' + emu + '_em.sh', 'r')
            for line in f.readlines():
                if line.find('#ecminfofile=') >= 0:
                    f.close()
                    return '/tmp/' + line.split('=')[1][:-1]

            f.close()
        except:
            return '/tmp/ecm.info'

    def readEmuActive(self):
        try:
            f = open('/usr/bin/emuactive', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'None'

    def readSrvActive(self):
        try:
            f = open('/usr/bin/csactive', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'None'

    def readAddonsUrl(self):
        try:
            f = open('/etc/DEServer', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'http://feed.dream-elite.net/DE4/DEManager/'


class DTT:

    def TunerEntry(self, name, module, started):
        if started:
            picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/lock_on.png'))
        else:
            picture = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/lock_off.png'))
        return (name, module, picture)
