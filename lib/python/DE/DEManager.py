from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.PluginBrowser import PluginBrowser
from Screens.Standby import TryQuitMainloop
from Screens.HelpMenu import HelpableScreen
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import config, ConfigSelection, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Input import Input
from Components.Harddisk import harddiskmanager
from Tools.HardwareInfo import HardwareInfo
from Tools.Directories import pathExists, fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, SCOPE_METADIR, SCOPE_MEDIA
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.PluginComponent import plugins
from Components.MenuList import MenuList
import gettext
from Components.Console import Console
from Screens.Console import Console as Console1
import os
import operator
import StringIO
import base64
from os import environ as os_environ, path as os_path, remove as os_remove, listdir, chdir, getcwd, statvfs, popen, system
from enigma import eTimer, eDVBDB, eDVBCI_UI, iServiceInformation, eConsoleAppContainer, eListboxPythonMultiContent, eListbox, gFont
from xml.etree.cElementTree import fromstring, ElementTree
from DownloadProgress import DownloadProgress
from Components.Sources.List import List
from DELibrary import parse_ecm
DEUpdate = []

class DETool():

    def xor_crypt(self, str1, pw):
        try:
            str2 = str1
            sr = StringIO.StringIO(str2)
            sw = StringIO.StringIO(str2)
            sr.seek(0)
            sw.seek(0)
            n = 0
            for k in range(len(str2)):
                if n >= len(pw) - 1:
                    n = 0
                p = ord(pw[n])
                n += 1
                c = sr.read(1)
                b = ord(c)
                t = operator.xor(b, p)
                z = chr(t)
                sw.seek(k)
                sw.write(z)

            sw.seek(0)
            str3 = sw.read()
            return base64.encodestring(str3)
        except:
            return 'None'

    def xor_decrypt(self, str1, pw):
        strdec = base64.b64decode(str1)
        str2 = strdec
        sr = StringIO.StringIO(str2)
        sw = StringIO.StringIO(str2)
        sr.seek(0)
        sw.seek(0)
        n = 0
        for k in range(len(str2)):
            if n >= len(pw) - 1:
                n = 0
            p = ord(pw[n])
            n += 1
            c = sr.read(1)
            b = ord(c)
            t = operator.xor(b, p)
            z = chr(t)
            sw.seek(k)
            sw.write(z)

        sw.seek(0)
        str3 = sw.read()
        return str3

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

    def getScriptName(self, script):
        try:
            f = open('/usr/script/' + script + '_user.sh', 'r')
            for line in f.readlines():
                if line.find('#scriptname=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return script
        except:
            return 'None'

    def getScriptCanDelete(self, script):
        try:
            f = open('/usr/script/' + script + '_user.sh', 'r')
            for line in f.readlines():
                if line.find('#candelete=') >= 0:
                    f.close()
                    return line.split('=')[1][:-1]

            f.close()
            return script
        except:
            return 'None'

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

    def readEcmInfo(self):
        emuActive = self.readEmuActive()
        info = parse_ecm(self.readEcmInfoFile(emuActive))
        if info != 0:
            caid = info[0]
            pid = info[1]
            provid = info[2]
            provider = info[3]
            txsystem = info[4]
            ecmtime = info[5]
            hops = info[6]
            using = info[7]
            protocol = info[8]
            source = info[9]
            addr = info[10]
            port = info[11]
            returnMsg = ''
            if provid != '':
                returnMsg += 'Provider: ' + provid + '\n'
            if txsystem != '':
                returnMsg += 'System: ' + txsystem + '\n'
            if provider != '':
                returnMsg += 'Provider: ' + provider + '\n'
            if caid != '':
                returnMsg += 'Ca ID: ' + caid + '\n'
            if pid != '':
                returnMsg += 'Pid: ' + pid + '\n'
            if addr != '':
                if addr.find('127.0.0.1') >= 0 or addr.find('local') >= 0:
                    returnMsg += 'Decode: Internal\n'
                elif addr.find('/dev/sci0') >= 0:
                    returnMsg += 'Decode: Slot 1\n'
                elif addr.find('/dev/sci1') >= 0:
                    returnMsg += 'Decode: Slot 2\n'
                elif addr.find('/dev/ttyUSB') >= 0:
                    returnMsg += 'Decode: USB Reader\n'
                else:
                    if port != '':
                        returnMsg += 'Source: ' + addr + ':' + str(port) + '\n'
                    else:
                        returnMsg += 'Source: ' + addr + '\n'
                    if hops > 0:
                        returnMsg += ' Hops: ' + str(hops) + '\n'
            if ecmtime > 0:
                returnMsg += 'ECM Time: ' + str(ecmtime) + ' msec\n'
            return returnMsg
        else:
            return 'No Info'

    def readAddonsUrl(self):
        try:
            f = open('/etc/DEServer', 'r')
            line = f.readline()
            f.close()
            return line[:-1]
        except:
            return 'http://feed.dream-elite.net/DE4/DEManager/'

    def readExtraUrl(self):
        try:
            f = open('/etc/DExtra', 'r')
            line = f.readline()
            f.close()
            if line[:2] == '#c':
                password = 'dktp84067ll'
                str8 = t.xor_decrypt(line[2:len(line)], password)
                return str8
            return line[:-1]
        except:
            return ''

    def getVarSpace(self, partition):
        free = 0
        try:
            if partition == '/usr/share/enigma2/' or partition == '/tmp/':
                stat = statvfs('/')
                return stat.f_bfree * stat.f_bsize / 1024
            readlist = popen('df | grep -e "/media" -e "/dev/root" -e "ubi0:rootfs" -e "/LowFAT"', 'r').readlines()
            if partition.endswith('/'):
                partition = partition[:-1]
            for line in readlist:
                x = line.strip().split()
                if x[0] == partition:
                    free = int(x[3])
                    return free
                if x[len(x) - 1] == partition:
                    free = int(x[len(x) - 3])
                    return free

            return 0
        except OSError:
            return 0


t = DETool()
linkAddons = t.readAddonsUrl()
linkExtra = t.readExtraUrl()

class util():
    pluginIndex = -1
    pluginType = ''
    typeDownload = 'A'
    addonsName = ''
    filename = ''
    dir = ''
    size = -1
    check = 0
    restart = '0'
    instpath = ''
    tmpchild = []
    previewPath = ''
    filedate = ''

    def removeSetting(self):
        print 'Remove settings'
        system('rm -f /etc/enigma2/*.radio')
        system('rm -f /etc/enigma2/*.tv')
        system('rm -f /etc/enigma2/lamedb')
        system('rm -f /etc/enigma2/blacklist')
        system('rm -f /etc/enigma2/whitelist')

    def reloadSetting(self):
        print 'Reload settings'
        self.eDVBDB = eDVBDB.getInstance()
        self.eDVBDB.reloadServicelist()
        self.eDVBDB.reloadBouquets()


u = util()

class ListboxE1(MenuList):
    __module__ = __name__

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 22))
        self.l.setItemHeight(36)


def GetSkinPath():
    cur_skin_path = resolveFilename(SCOPE_CURRENT_SKIN, '')
    if cur_skin_path == '/usr/share/enigma2/':
        cur_skin_path = '/usr/share/enigma2/skin_default/'
    return cur_skin_path


class loadTmpDir():
    tmp_list = []

    def load(self):
        del self.tmp_list[:]
        pkgs = listdir('/tmp')
        count = 0
        for fil in pkgs:
            if fil.find('.ipk') != -1 or fil.find('.tbz2') != -1 or fil.find('.zip') != -1 or fil.find('.rar') != -1:
                os.rename('/tmp/' + fil, '/tmp/' + fil.replace(' ', '_'))
                self.tmp_list.append([count, fil.replace(' ', '_')])
                count += 1


loadtmpdir = loadTmpDir()

class loadUniDir():
    uni_list = []

    def load(self):
        del self.uni_list[:]
        pkgs = listdir('/usr/uninstall')
        count = 0
        for fil in pkgs:
            if fil.find('_remove.sh') != -1 or fil.find('_delete.sh') != -1:
                self.uni_list.append([count, fil])
                count += 1


loadunidir = loadUniDir()

class DEManager(Screen):
    skin = '\n\t<screen name="DEManager" position="center,center" size="800,500">\n\t\t<widget name="info_use" position="33,10" zPosition="2" size="359,30" valign="center" halign="center" font="Regular;22" transparent="1" backgroundColor="#ffffffff" shadowColor="#1A58A6" shadowOffset="-2,-1" />\n\t\t<widget name="config" position="53,50" size="319,80" zPosition="2" transparent="1" />\n\t\t<widget name="key_blue" position="425,420" size="325,28" font="Regular;22" halign="center" foregroundColor="blue" zPosition="2" transparent="1" />\n\t\t<widget name="key_yellow" position="425,390" size="325,28" font="Regular;22" halign="center" foregroundColor="yellow" zPosition="2" transparent="1" />\n\t\t<widget name="key_red" position="425,360" size="325,28" font="Regular;22" halign="center" foregroundColor="red" zPosition="2" transparent="1" />\n\t\t<widget name="key_green" position="425,330" size="325,28" font="Regular;22" halign="center" foregroundColor="green" zPosition="2" transparent="1" />\n\t\t<widget name="ecmtext" position="53,150" size="340,300" font="Regular;18" zPosition="2" backgroundColor="#333333" transparent="1"/>\n\t</screen>'
    VERSION = '2.80'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['config'] = ConfigList(self.list)
        self['ecmtext'] = ScrollLabel('')
        self['key_blue'] = Label(_('Addons'))
        self['key_yellow'] = Label(_('Utility'))
        self['key_green'] = Label('')
        if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/CCcamInfo/plugin.py')):
            self['key_red'] = Label(_('CCCam Info'))
        else:
            self['key_red'] = Label(_('Exit'))
        self['info_use'] = Label(_('Use arrows < > to select'))
        self['actions'] = NumberActionMap(['ColorActions',
         'CiSelectionActions',
         'WizardActions',
         'SetupActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'blue': self.download,
         'green': self.DeEPG,
         'yellow': self.keyYellow,
         'red': self.ccinfo,
         'ok': self.ok_pressed,
         'back': self.cancel}, -1)
        self.activityTimer = eTimer()
        self.console = Console()
        self.ecmTimer = eTimer()
        self.ecmTimer.timeout.get().append(self.readEcmInfo)
        self.ecmTimer.start(10000, True)
        self.readEcmInfo()
        self.onLayoutFinish.append(self.loadEmuList)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.loadEmuList()
        self.setTitle('Dream Elite Manager v. ' + self.VERSION)

    def loadEmuList(self):
        emu = []
        crd = []
        emu.append('None')
        crd.append('None')
        self.emu_list = {}
        self.crd_list = {}
        self.emu_list['None'] = 'None'
        self.crd_list['None'] = 'None'
        emufilelist = FileList('/usr/script', matchingPattern='_em.*')
        srvfilelist = FileList('/usr/script', matchingPattern='_cs.*')
        for x in emufilelist.getFileList():
            if x[0][1] != True:
                emuName = t.readEmuName(x[0][0][:-6])
                emu.append(emuName)
                self.emu_list[emuName] = x[0][0][:-6]

        softcam = ConfigSelection(default=t.readEmuName(t.readEmuActive()), choices=emu)
        for x in srvfilelist.getFileList():
            if x[0][1] != True:
                srvName = t.readSrvName(x[0][0][:-6])
                crd.append(srvName)
                self.crd_list[srvName] = x[0][0][:-6]

        cardserver = ConfigSelection(default=t.readSrvName(t.readSrvActive()), choices=crd)
        del self.list[:]
        self.list.append(getConfigListEntry(_('SoftCam (%s) :') % str(len(emu) - 1), softcam))
        self.list.append(getConfigListEntry(_('CardServer (%s) :') % str(len(crd) - 1), cardserver))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyLeft(self):
        self['config'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['config'].handleKey(KEY_RIGHT)

    def ok_pressed(self):
        if self['config'].getCurrentIndex() == 0:
            self.newemu = self.emu_list[self['config'].getCurrent()[1].getText()]
            self.ss_sc()
        elif self['config'].getCurrentIndex() == 1:
            self.newsrv = self.crd_list[self['config'].getCurrent()[1].getText()]
            self.ss_srv()
        else:
            self.close()

    def cancel(self):
        for f in os.listdir('/tmp/'):
            if f.endswith('.png'):
                print '[DEManager] Cleaning temp picture:', f
                os.remove('/tmp/' + f)

        self.close()

    def download(self):
        self.session.open(AddonsPanel)

    def DeEPG(self):
        pass

    def keyYellow(self):
        self.session.open(UtilityPanel)

    def ccinfo(self):
        if fileExists(resolveFilename(SCOPE_PLUGINS, 'Extensions/CCcamInfo/plugin.py')):
            from Plugins.Extensions.CCcamInfo.plugin import *
            self.session.open(CCcamInfoMain)
        else:
            self.close()

    def ss_sc(self):
        self.emuactive = t.readEmuActive()
        self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
        if self.emuactive != 'None' and self.newemu != 'None' and self.emuactive != self.newemu:
            self.mbox = self.session.open(MessageBox, _('Stopping %s and starting %s.') % (t.readEmuName(self.emuactive), t.readEmuName(self.newemu)), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.restart_emu)
            self.activityTimer.start(250, False)
            return
        if self.emuactive != 'None' and self.newemu != 'None' and self.emuactive == self.newemu:
            self.mbox = self.session.open(MessageBox, _('Restarting %s.') % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.restart_emu)
            self.activityTimer.start(250, False)
            return
        if self.emuactive != 'None':
            self.mbox = self.session.open(MessageBox, _('Stopping %s.') % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.stop_emu)
            self.activityTimer.start(250, False)
            return
        if self.newemu != 'None':
            self.session.nav.stopService()
            self.mbox = self.session.open(MessageBox, _('Starting %s.') % t.readEmuName(self.newemu), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.start_emu)
            self.activityTimer.start(250, False)

    def restart_emu(self):
        self.activityTimer.stop()
        os.system('/usr/script/' + self.emuactive + '_em.sh stop')
        self.session.nav.stopService()
        os.system('/usr/script/' + self.newemu + '_em.sh start')
        os.system('echo ' + self.newemu + ' > /usr/bin/emuactive')
        self.session.nav.playService(self.oldref)
        self.mbox.close()
        self.close()

    def stop_emu(self):
        self.activityTimer.stop()
        os.system('/usr/script/' + self.emuactive + '_em.sh stop')
        os.system('rm -f /usr/bin/emuactive')
        self.mbox.close()

    def start_emu(self):
        self.activityTimer.stop()
        self.session.nav.stopService()
        os.system('/usr/script/' + self.newemu + '_em.sh start')
        os.system('echo ' + self.newemu + ' > /usr/bin/emuactive')
        self.session.nav.playService(self.oldref)
        self.mbox.close()
        self.close()

    def ss_srv(self):
        self.serveractive = t.readSrvActive()
        if self.serveractive == 'None' and self.newsrv == 'None':
            return
        self.emuactive = t.readEmuActive()
        if self.emuactive != 'None' and self.serveractive == 'None':
            msg = _('Please stop %s\nbefore start cardserver!') % t.readEmuName(self.emuactive)
            self.box = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
            self.box.setTitle(_('Start Cardserver'))
            return
        if self.serveractive != 'None' and self.newsrv != 'None' and self.serveractive == self.newsrv:
            self.mbox = self.session.open(MessageBox, _('Restarting %s.') % t.readSrvName(self.serveractive), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.restart_cs)
            self.activityTimer.start(250, False)
            return
        if self.serveractive != 'None' and self.newsrv != 'None' and self.serveractive != self.newsrv:
            self.mbox = self.session.open(MessageBox, _('Stopping %s and starting %s.') % (t.readSrvName(self.serveractive), t.readSrvName(self.newsrv)), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.restart_cs)
            self.activityTimer.start(250, False)
            return
        if self.serveractive != 'None':
            self.mbox = self.session.open(MessageBox, _('Stopping %s.') % t.readSrvName(self.serveractive), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.stop_cs)
            self.activityTimer.start(250, False)
            return
        if self.newsrv != 'None':
            self.mbox = self.session.open(MessageBox, _('Starting  %s.') % t.readSrvName(self.newsrv), MessageBox.TYPE_INFO)
            self.mbox.setTitle(_('Running..'))
            self.activityTimer.timeout.get().append(self.start_cs)
            self.activityTimer.start(250, False)

    def restart_cs(self):
        self.activityTimer.stop()
        os.system('/usr/script/' + self.serveractive + '_cs.sh stop')
        os.system('/usr/script/' + self.newsrv + '_cs.sh start')
        os.system('echo ' + self.newsrv + ' > /usr/bin/csactive')
        self.mbox.close()

    def stop_cs(self):
        self.activityTimer.stop()
        os.system('/usr/script/' + self.serveractive + '_cs.sh stop')
        os.system('rm -f /usr/bin/csactive')
        self.mbox.close()

    def start_cs(self):
        self.activityTimer.stop()
        os.system('/usr/script/' + self.newsrv + '_cs.sh start')
        os.system('echo ' + self.newsrv + ' > /usr/bin/csactive')
        self.mbox.close()

    def readEcmInfo(self):
        service = self.session.nav.getCurrentService()
        info = service and service.info()
        if info is not None:
            if info.getInfo(iServiceInformation.sIsCrypted):
                self['ecmtext'].setText(t.readEcmInfo())
            else:
                self['ecmtext'].setText('Free To Air')
        else:
            self['ecmtext'].setText('')
        return


class AddonsPanel(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('DE Addons Manager'))
        self['list'] = ListboxE1(self.list)
        self['conn'] = Label('')
        self['key_red'] = Label(_('Cancel'))
        self['conn'].hide()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.MenuList = [('AddonsPanel',
          _('Download Addons'),
          'icons/network.png',
          True),
         ('NExtra',
          _('Download Extra'),
          'icons/network.png',
          fileExists('/etc/DExtra')),
         ('NManual',
          _('Manual Package Install'),
          'icons/manual.png',
          True),
         ('NRemove',
          _('Remove Addons'),
          'icons/remove.png',
          True)]
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.cancel,
         'back': self.cancel})
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('DE Addons Manager'))

    def KeyOk(self):
        if not self.container.running():
            self['conn'].setText(_('Connecting to addons server.\nPlease wait...'))
            sel = self['list'].getCurrent()[0]
            if sel == 'AddonsPanel':
                self['conn'].show()
                u.typeDownload = 'A'
                self.container.execute('wget ' + linkAddons + 'addons.xml -O /tmp/addons.xml')
            elif sel == 'NExtra':
                self['conn'].show()
                u.typeDownload = 'E'
                self.container.execute('wget ' + linkExtra + 'addons_extra.xml -O /tmp/addons.xml')
            elif sel == 'NManual':
                self.session.open(ManualInstall)
            elif sel == 'NRemove':
                self.session.open(AddonsRemove)

    def runFinished(self, retval):
        if fileExists('/tmp/addons.xml'):
            self['conn'].hide()
            self.session.open(ReadAddons)
        else:
            self['conn'].setText(_('Server not found!\nPlease check internet connection.'))

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            if fileExists('/tmp/addons.xml'):
                system('rm -f /tmp/addons.xml')
            self['conn'].setText(_('Process Killed by user\nServer Not Connected!'))

    def updateList(self):
        del self.list[:]
        for i in self.MenuList:
            if i[3]:
                res = [i[0]]
                res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=i[1]))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/' + i[2]))))
                self.list.append(res)

        self['list'].l.setList(self.list)


class UtilityPanel(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="center,center" size="560,430" title="Utility">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('DE Utility panel'))
        self['list'] = ListboxE1(self.list)
        self['key_red'] = Label(_('Cancel'))
        self.MenuList = [('Scriptexe',
          _('Script Executor'),
          'icons/user.png',
          True), ('URLCrypt',
          _('URL Crypt'),
          'icons/lock.png',
          True)]
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.cancel,
         'back': self.cancel})
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('DE Utility Panel'))

    def KeyOk(self):
        sel = self['list'].getCurrent()[0]
        if sel == 'Scriptexe':
            self.session.open(ScriptExecuter)
        elif sel == 'URLCrypt':
            self.session.open(URLInput)

    def cancel(self):
        self.close()

    def updateList(self):
        del self.list[:]
        for i in self.MenuList:
            if i[3]:
                res = [i[0]]
                res.append(MultiContentEntryText(pos=(50, 5), size=(300, 32), font=0, text=i[1]))
                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/' + i[2]))))
                self.list.append(res)

        self['list'].l.setList(self.list)


class ReadAddons(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="center,center" size="700,500">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget source="conn" render="Label" position="10,450" size="680,50" font="Regular;20" halign="center" valign="center"  />\n\t\t<widget source="menu" render="Listbox" position="20,45" size="660,380" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\tMultiContentEntryText(pos = (50, 3), size = (590, 28), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\tMultiContentEntryText(pos = (50, 33), size = (590, 24), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 28), gFont("Regular", 19)],\n\t\t\t\t\t"itemHeight": 60\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t</screen> '

    def __init__(self, session, partial = None):
        Screen.__init__(self, session)
        self.partial = partial
        self.list = []
        self.appt_list = []
        self.outlist = []
        self['menu'] = List(list())
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['conn'] = StaticText(' ')
        self['conn'].setText(_('Building menu...please wait...'))
        self['key_red'] = Button(_('Exit'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.close,
         'cancel': self.back}, -2)
        self.onShown.append(self.setWindowTitle)
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.parsexml)
        self.activityTimer.start(300, False)

    def parsexml(self):
        self.activityTimer.stop()
        try:
            if not self.partial:
                self.get_list('/tmp/addons.xml', '0')
                self.error = False
            else:
                self.get_list('/tmp/addons.xml', self.partial)
                self.error = False
        except:
            self['conn'].setText(_('File xml is not correctly formatted!.'))
            self.error = True

        if not self.partial:
            self.drawList()
        else:
            self.redrawList(self.appt_list)
        if fileExists('/tmp/addons.xml'):
            system('rm -f /tmp/addons.xml')

    def get_list(self, filename, filter):
        tree = ElementTree()
        tree.parse(filename)
        for channel in tree.findall('line'):
            text = channel.findtext('text')
            level = channel.findtext('level')
            comment = channel.findtext('comment')
            file = channel.findtext('file')
            size = channel.findtext('size')
            parent = channel.findtext('parent')
            directory = channel.findtext('directory')
            type = channel.findtext('type')
            restart = channel.findtext('restart')
            chksize = channel.findtext('chksize')
            filedate = channel.findtext('filedate')
            if filter != '0':
                if level == '3' and filter == parent:
                    chan_tulpe = [text,
                     comment,
                     parent,
                     file,
                     size,
                     directory,
                     level,
                     type,
                     restart,
                     chksize,
                     filedate]
                    self.appt_list.append(chan_tulpe)
            else:
                chan_tulpe = [text,
                 comment,
                 parent,
                 file,
                 size,
                 directory,
                 level,
                 type,
                 restart,
                 chksize,
                 filedate]
                self.appt_list.append(chan_tulpe)

    def setWindowTitle(self):
        self.varspace = t.getVarSpace('/usr/share/enigma2/')
        self.wtitle = {'A': _('Download Addons   (Available flash: %s )') % self.varspace,
         'E': _('Download Extra   (Available flash: %s )') % self.varspace}[u.typeDownload]
        self.setTitle(self.wtitle)

    def selectionChanged(self):
        pass

    def KeyOk(self):
        del self.outlist[:]
        self['conn'].text = ' '
        u.instpath = '/tmp/'
        try:
            if self['menu'].count() > 0:
                selection = self['menu'].getCurrent()[0]
                for item in self.searchselection(selection):
                    if item[6] == '3':
                        u.size = int(item[4])
                        u.addonsName = str(item[0])
                        u.filename = str(item[3])
                        u.dir = str(item[5])
                        u.restart = item[8]
                        u.pluginType = item[7]
                        u.check = item[9]
                        u.filedate = item[10]
                        if item[7] == 'picon' or item[7] == 'picon_oled' or item[7] == 'piconlcd':
                            self.session.openWithCallback(self.downloadAddons, SelectPaths)
                        else:
                            u.instpath = '/tmp/'
                            self.downloadAddons(True)
                    elif item[6] == '1' and item[7] == 'bootlogo' and self.searchild(selection, 3) != 'notfound':
                        u.tmpchild = self.searchild(selection, 3)
                        u.pluginType = item[7]
                        self.session.openWithCallback(self.downloadAddons, BootlogoDE)
                    elif item[6] == '1' and item[7] == 'skin' and self.searchild(selection, 3) != 'notfound':
                        u.tmpchild = self.searchild(selection, 3)
                        u.pluginType = item[7]
                        self.session.openWithCallback(self.downloadAddons, SkinDE)
                    else:
                        a = int(item[6]) + 1
                        while a < 4:
                            childlist = self.searchild(selection, a)
                            if childlist != 'notfound':
                                self.redrawList(childlist)
                                break
                            else:
                                a = a + 1

            else:
                self.drawList()
        except:
            self.drawList()

    def back(self):
        if self.partial:
            self.close()
        if self.error == False:
            a = 0
            try:
                if self['menu'].count() > 0:
                    selection = self['menu'].getCurrent()[0]
                    for item in self.searchselection(selection):
                        if item[6] == '1':
                            self.drawList()
                        elif item[6] == '0':
                            self.close()
                        else:
                            a = int(item[6]) - 1
                            while a >= 0:
                                parentlist = self.searchparent(item[2], a)
                                if parentlist != 'notfound':
                                    self.redrawList(self.getsamemenu(parentlist[0][2], parentlist[0][6]))
                                    break
                                a = a - 1

                else:
                    self.drawList()
            except:
                self.drawList()

        else:
            self.close()

    def searchselection(self, selection):
        self.tmplist = []
        for entry in self.appt_list:
            if entry[0] == selection:
                self.tmplist.append(entry)

        return self.tmplist

    def searchild(self, parent, level):
        tmplist = []
        outlist = []
        counter = 0
        for entry in self.appt_list:
            if entry[6] == str(level):
                if entry[2] == parent:
                    tmplist.append(entry)
                    counter = counter + 1

        if counter > 0:
            return tmplist
        else:
            return 'notfound'

    def searchparent(self, child, level):
        tmplist = []
        for entry in self.appt_list:
            if entry[6] == str(level):
                if entry[0] == child:
                    tmplist.append(entry)
                    return tmplist

        return 'notfound'

    def getsamemenu(self, parent, level):
        tmplist = []
        for entry in self.appt_list:
            if entry[6] == str(level):
                if entry[2] == parent:
                    tmplist.append(entry)

        return tmplist

    def drawList(self):
        llist = []
        for entry in self.appt_list:
            if entry[6] == '0':
                llist.append(self.menubuild(entry[0], entry[1]))

        self['menu'].setList(llist)
        self['conn'].text = _('Select addons to install')

    def redrawList(self, list):
        llist = []
        print list
        for entry in list:
            if entry[6] == '3':
                tmpmess = _('%s Size: %s Kb Date: %s') % (entry[1], entry[4], entry[10])
                llist.append(self.menubuild(entry[0], tmpmess))
            else:
                llist.append(self.menubuild(entry[0], entry[1]))

        self['menu'].setList(llist)
        self['conn'].text = _('Select addons to install')

    def menubuild(self, mess1, mess2):
        return (str(mess1), str(mess2))

    def downloadAddons(self, answer):
        if answer is True:
            url = {'E': linkExtra,
             'A': linkAddons}[u.typeDownload] + u.dir + '/' + u.filename
            self.session.openWithCallback(self.executedScript, DownloadProgress, url, u.instpath, u.filename)
        elif u.pluginType != 'bootlogo' and u.pluginType != 'skin':
            msg = _('Process Killed by user.\nAddon not installed correctly!')
            self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR)

    def executedScript(self, *answer):
        if fileExists(u.instpath + u.filename):
            if u.size < t.getVarSpace(u.instpath) or u.check == 0:
                msg = _('Do you want install the addon:\n%s?') % u.addonsName
                box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Install Addon'))
            else:
                msg = _('Not enough space!\nPlease delete addons before install new.')
                self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR)
                self.clearfile()
                return
        else:
            msg = _('File: %s not found!\nPlease check your internet connection.') % u.filename
            self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR)

    def installAddons(self, answer):
        if answer is True:
            try:
                self['conn'].text = _('Installing addons.\nPlease Wait...')
                if u.filename.find('.ipk') != -1:
                    cmd = ['opkg install --force-overwrite /tmp/' + u.filename]
                    self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                elif u.filename.find('.tbz2') != -1:
                    if u.pluginType == 'setting' or u.pluginType == 'e2setting':
                        self['conn'].text = _('Remove old Settings\nPlease wait...')
                        u.removeSetting()
                        cmd = ['tar -jxvf /tmp/' + u.filename + ' -C /']
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                    elif u.pluginType == 'bootlogo':
                        try:
                            machine = HardwareInfo().get_device_name()
                            cmd = ['mount -o rw,remount /boot',
                             'tar -jxvf /tmp/' + u.filename + ' -C /',
                             'mv /tmp/bootlogo.jpg /boot/bootlogo-' + machine + '.jpg',
                             'mount -o ro,remount /boot']
                            self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                        except:
                            self['conn'].text = _('File: %s\ninstallation failed!') % u.filename

                    elif u.pluginType == 'picon' or u.pluginType == 'picon_oled' or u.pluginType == 'piconlcd':
                        cmd = ['tar -jxvf ' + u.instpath + u.filename + ' -C ' + u.instpath]
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                    else:
                        cmd = ['tar -jxvf /tmp/' + u.filename + ' -C /']
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                elif u.filename.find('.zip') != -1:
                    if u.pluginType == 'setting' or u.pluginType == 'e2setting':
                        self['conn'].text = _('Remove old Settings\nPlease wait...')
                        u.removeSetting()
                        cmd = ['unzip -o /tmp/' + u.filename + ' -d /etc/enigma2']
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                    elif u.pluginType == 'picon' or u.pluginType == 'picon_oled' or u.pluginType == 'piconlcd':
                        if not os_path.isdir(u.instpath + u.pluginType + u.pluginType):
                            system('mkdir ' + u.instpath + u.pluginType)
                        cmd = ['unzip -o ' + u.instpath + u.filename + ' -d ' + u.instpath + u.pluginType]
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                elif u.filename.find('.rar') != -1:
                    if u.pluginType == 'setting' or u.pluginType == 'e2setting':
                        self['conn'].text = _('Remove old Settings\nPlease wait...')
                        u.removeSetting()
                        cmd = ['unrar e -o+ /tmp/' + u.filename + ' /etc/enigma2/']
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                    elif u.pluginType == 'picon' or u.pluginType == 'picon_oled' or u.pluginType == 'piconlcd':
                        if not os_path.isdir(u.instpath + u.pluginType + u.pluginType):
                            system('mkdir ' + u.instpath + u.pluginType)
                        cmd = ['unrar e -o+ ' + u.instpath + u.filename + ' ' + u.instpath + u.pluginType + '/']
                        self.session.openWithCallback(self.runFinished, Console1, title=_('Installing: %s') % u.filename, cmdlist=cmd, closeOnSuccess=True)
                else:
                    self['conn'].text = _('File: %s\nis not a valid package!') % u.filename
            except:
                self.clearfile()
                self['conn'].text = _('File: %s\ninstallation failed!') % u.filename

        else:
            self.clearfile()

    def clearfile(self):
        if fileExists(u.instpath + u.filename):
            system('rm -f ' + u.instpath + u.filename)
        if fileExists('/tmp/mem.tmp'):
            system('rm -f /tmp/mem.tmp')

    def runFinished(self):
        self.clearfile()
        if u.pluginType == 'setting' or u.pluginType == 'e2setting':
            self['conn'].text = _('Reload new Settings\nPlease wait...')
            u.reloadSetting()
        elif u.pluginType == 'plugin' or u.pluginType == 'e2plugin':
            self['conn'].text = _('Reload Plugins list\nPlease Wait...')
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        elif u.pluginType == 'picon' or u.pluginType == 'picon_oled' or u.pluginType == 'piconlcd':
            if u.instpath == '/usr/share/enigma2/':
                dpath = 'flash'
            else:
                device = u.instpath.split('/')
                if len(device) > 1:
                    dpath = str(device[len(device) - 2])
                else:
                    dpath = 'Unknow'
            if u.pluginType == 'picon':
                script = 'rm -rf %spicon\nrm -rf /usr/uninstall/picon_%s_remove.sh\nexit 0' % (u.instpath, dpath)
                filename = '/usr/uninstall/picon_%s_remove.sh' % dpath
            elif u.pluginType == 'picon_oled':
                script = 'rm -rf %spicon_oled\nrm -rf /usr/uninstall/picon_oled_%s_remove.sh\nexit 0' % (u.instpath, dpath)
                filename = '/usr/uninstall/picon_oled_%s_remove.sh' % dpath
            elif u.pluginType == 'piconlcd':
                script = 'rm -rf %spiconlcd\nrm -rf /usr/uninstall/piconlcd_%s_remove.sh\nexit 0' % (u.instpath, dpath)
                filename = '/usr/uninstall/piconlcd_%s_remove.sh' % dpath
            if fileExists(filename):
                system('rm -rf ' + filename)
            out_file = open(filename, 'w')
            out_file.write(script)
            out_file.close()
            if fileExists(filename):
                system('chmod 755 %s' % filename)
            if config.usage.picon_path.value != u.instpath[:-1]:
                msg = _('Do you want to set default picon path on %s?') % u.instpath
                box = self.session.openWithCallback(self.setPiconPath, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Default picon path'))
        self['conn'].text = _('Addon installed succesfully!')
        self.setWindowTitle()
        if u.restart == '1':
            if fileExists('/tmp/.restartE2'):
                system('rm -f /tmp/.restartE2')
            msg = _('Enigma2 will be now hard restarted to complete package installation.\nDo You want restart enigma2 now?')
            box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle(_('Restart Enigma2'))

    def setPiconPath(self, answer):
        if answer is True:
            config.usage.picon_path.value = u.instpath
            config.usage.picon_path.save()

    def restartEnigma2(self, answer):
        if answer:
            self.session.open(TryQuitMainloop, 3)


class BootlogoDE(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="center,170" size="750,400" title="Choose your Bootlogo">\n\t\t<widget name="BootlogoList" position="20,10" size="325,300" scrollbarMode="showOnDemand" selectionPixmap="skin_default/DEInfo/menu/sel_595x25.png" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/div-v.png" position="360,15" zPosition="10" size="3,300" transparent="1" alphatest="on" />\n\t\t<widget name="Preview" position="410,45" size="280,210" alphatest="on" />\n\t\t<widget source="comment" render="Label" position="10,370" size="730,30" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.listbootlogo = u.tmpchild
        self.skinlist = []
        self.previewPath = ''
        self['key_red'] = StaticText(_('Close'))
        self['comment'] = StaticText('')
        self['BootlogoList'] = MenuList(self.loadlist())
        self['Preview'] = Pixmap()
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions', 'EPGSelectActions'], {'ok': self.ok,
         'back': self.cancel,
         'red': self.cancel,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right}, -1)
        self.container = eConsoleAppContainer()
        self.onLayoutFinish.append(self.loadPreview)

    def loadlist(self):
        skinlist = []
        if len(self.listbootlogo) > 0:
            for x in self.listbootlogo:
                skinlist.append(str(x[0]))

        else:
            skinlist = ['No bootlogo available']
        return skinlist

    def up(self):
        self['BootlogoList'].up()
        self.loadPreview()

    def down(self):
        self['BootlogoList'].down()
        self.loadPreview()

    def left(self):
        self['BootlogoList'].pageUp()
        self.loadPreview()

    def right(self):
        self['BootlogoList'].pageDown()
        self.loadPreview()

    def ok(self):
        for items in self.listbootlogo:
            if items[0] == self['BootlogoList'].getCurrent():
                u.size = int(items[4])
                u.addonsName = str(items[0])
                u.filename = str(items[3])
                u.dir = str(items[5])
                u.restart = items[8]
                u.pluginType = items[7]
                u.check = items[9]
                break

        self.close(True)

    def loadPreview(self):
        pngpath = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SkinSelector/noprev.png')
        if self['BootlogoList'].getCurrent() != 'No bootlogo available':
            for items in self.listbootlogo:
                if items[0] == self['BootlogoList'].getCurrent():
                    self['comment'].setText(items[1])
                    filename = items[3].replace('.tbz2', '') + '.png'
                    if fileExists('/tmp/' + filename) and self['BootlogoList'].getCurrent() is not None:
                        pngpath = '/tmp/' + filename
                    else:
                        try:
                            prova = 'wget ' + linkAddons + str(items[5]) + '/preview/' + filename + ' -O /tmp/' + filename
                            system(prova)
                            if fileExists('/tmp/' + filename):
                                pngpath = '/tmp/' + filename
                        except:
                            print 'Preview icon load error'

        self.previewPath = pngpath
        self['Preview'].instance.setPixmapFromFile(self.previewPath)
        return

    def cancel(self):
        self.close(False)


class SkinDE(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="center,170" size="750,400" title="Choose your Skin">\n\t\t<widget name="BootlogoList" position="20,10" size="325,200" scrollbarMode="showOnDemand" selectionPixmap="skin_default/DEInfo/menu/sel_595x25.png" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/div-v.png" position="260,15" zPosition="10" size="3,300" transparent="1" alphatest="on" />\n\t\t<widget name="Preview" position="410,45" size="280,210" alphatest="on" />\n\t\t<widget source="comment" render="Label" position="10,370" size="730,30" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.listbootlogo = u.tmpchild
        self.skinlist = []
        self.previewPath = ''
        self['key_red'] = Label(_('Close'))
        self['key_green'] = Label(_('Preview'))
        self['comment'] = StaticText('')
        self['BootlogoList'] = MenuList(self.loadlist())
        self['Preview'] = Pixmap()
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions', 'ColorActions'], {'ok': self.ok,
         'back': self.cancel,
         'red': self.cancel,
         'green': self.showPreview,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right}, -1)
        self.container = eConsoleAppContainer()
        self.onLayoutFinish.append(self.loadPreview)

    def loadlist(self):
        skinlist = []
        if len(self.listbootlogo) > 0:
            for x in self.listbootlogo:
                skinlist.append(str(x[0]))

        else:
            skinlist = [_('No bootlogo available')]
        return skinlist

    def up(self):
        self['BootlogoList'].up()
        self.loadPreview()

    def down(self):
        self['BootlogoList'].down()
        self.loadPreview()

    def left(self):
        self['BootlogoList'].pageUp()
        self.loadPreview()

    def right(self):
        self['BootlogoList'].pageDown()
        self.loadPreview()

    def showPreview(self):
        self.session.open(SkinFullPreview)

    def ok(self):
        for items in self.listbootlogo:
            if items[0] == self['BootlogoList'].getCurrent():
                u.size = int(items[4])
                u.addonsName = str(items[0])
                u.filename = str(items[3])
                u.dir = str(items[5])
                u.restart = items[8]
                u.pluginType = items[7]
                u.check = items[9]
                break

        self.close(True)

    def loadPreview(self):
        pngpath = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SkinSelector/noprev.png')
        if self['BootlogoList'].getCurrent() != 'No bootlogo available':
            for items in self.listbootlogo:
                if items[0] == self['BootlogoList'].getCurrent():
                    self['comment'].setText(items[1])
                    u.previewPath = items[3].replace('.tbz2', '').replace('.ipk', '') + '.png'
                    if fileExists('/tmp/' + u.previewPath) and self['BootlogoList'].getCurrent() is not None:
                        pngpath = '/tmp/' + u.previewPath
                    else:
                        try:
                            prova = 'wget ' + linkAddons + str(items[5]) + '/preview/' + u.previewPath + ' -O /tmp/' + u.previewPath
                            system(prova)
                            if fileExists('/tmp/' + u.previewPath):
                                pngpath = '/tmp/' + u.previewPath
                        except:
                            print 'Skin preview icon load error'

        self.previewPath = pngpath
        self['Preview'].instance.setPixmapFromFile(self.previewPath)
        return

    def cancel(self):
        self.close(False)


class SkinFullPreview(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="center,center" size="1280,720">\n\t\t<widget name="Preview" position="0,0" size="1280,720" alphatest="on" />\n\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['Preview'] = Pixmap()
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions', 'EPGSelectActions'], {'ok': self.cancel,
         'back': self.cancel}, -1)
        self.fullpreview = ''
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        pngpath = resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SkinSelector/noprev.png')
        self.fullpreview = u.previewPath.replace('.png', '_full.png')
        if fileExists('/tmp/' + self.fullpreview):
            pngpath = '/tmp/' + self.fullpreview
        else:
            try:
                prova = 'wget ' + linkAddons + 'DESkin/preview/' + self.fullpreview + ' -O /tmp/' + self.fullpreview
                system(prova)
                if fileExists('/tmp/' + self.fullpreview):
                    pngpath = '/tmp/' + self.fullpreview
            except:
                print 'Preview icon load error'

        self.previewPath = pngpath
        self['Preview'].instance.setPixmapFromFile(self.previewPath)

    def cancel(self):
        for f in os.listdir('/tmp/'):
            if f.endswith('_full.png'):
                print 'Cleaning skin full preview:', f
                os.remove('/tmp/' + self.fullpreview)

        self.close(False)


class ManualInstall(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t\t\t<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = ListboxE1(self.list)
        self['conn'] = Label('')
        self['title'] = Label(_('Manual Installation'))
        self['key_red'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Reload /tmp'))
        self['conn'].hide()
        self.isSettings = False
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'yellow': self.readTmp,
         'red': self.cancel,
         'back': self.cancel})
        self.onLayoutFinish.append(self.readTmp)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Manual Installation'))

    def readTmp(self):
        del self.list[:]
        loadtmpdir.load()
        if len(loadtmpdir.tmp_list) > 0:
            for fil in loadtmpdir.tmp_list:
                res = [fil]
                res.append(MultiContentEntryText(pos=(0, 5), size=(340, 32), font=0, text=fil[1]))
                self.list.append(res)

        else:
            self['conn'].show()
            self['conn'].setText(_('Copy a file .tbz2|.ipk|.zip|.rar\nvia FTP in /tmp.'))
        self['list'].l.setList(self.list)

    def KeyOk(self):
        if not self.container.running():
            if len(loadtmpdir.tmp_list) > 0:
                self.sel = self['list'].getSelectionIndex()
                for p in loadtmpdir.tmp_list:
                    if p[0] == self.sel:
                        u.filename = p[1]

                msg = _('Do you want install the addon:\n%s?') % u.filename
                box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Install Addon'))
            else:
                self.close()

    def installAddons(self, answer):
        if answer is True:
            self['conn'].show()
            self['conn'].setText(_('Installing: %s.\nPlease wait...') % u.filename)
            if u.filename.find('.ipk') != -1:
                self.container.execute('opkg install --force-overwrite /tmp/' + u.filename)
            elif u.filename.find('.tbz2') != -1:
                self.container.execute('tar -jxvf /tmp/' + u.filename + ' -C /')
            elif u.filename.find('.zip') != -1:
                if self.CheckIfSettings('zip') == 'settings':
                    msg = _('Settings file detected: do you want to clean old settings?')
                    box = self.session.openWithCallback(self.ManualZipSettingsInstall, MessageBox, msg, MessageBox.TYPE_YESNO)
                    box.setTitle(_('Manual settings install'))
                else:
                    self.session.openWithCallback(self.DirectoryBrowserClosed, ManualSelection)
            elif u.filename.find('.rar') != -1:
                if self.CheckIfSettings('rar') == 'settings':
                    msg = _('Settings file detected: do you want to clean old settings?')
                    box = self.session.openWithCallback(self.ManualRarSettingsInstall, MessageBox, msg, MessageBox.TYPE_YESNO)
                    box.setTitle(_('Manual settings install'))
                else:
                    self.session.openWithCallback(self.DirectoryBrowserClosed, ManualSelection)
            else:
                self['conn'].setText(_('File: %s\nis not a valid package!') % u.filename)

    def CheckIfSettings(self, compression):
        if compression == 'zip':
            print 'Check if it is zip settings'
            zipfiletype = popen('unzip -l /tmp/' + u.filename, 'r').readlines()
            for item in zipfiletype:
                if item.find('lamedb') != -1:
                    self.isSettings = True
                    return 'settings'

        elif compression == 'rar':
            print 'Check if it is rar settings'
            rarfiletype = popen('unrar l /tmp/' + u.filename, 'r').readlines()
            for item in rarfiletype:
                if item.find('lamedb') != -1:
                    self.isSettings = True
                    return 'settings'

        else:
            return 'Other'

    def DirectoryBrowserClosed(self, path):
        print 'PathBrowserClosed:' + str(path)
        if path != False:
            if u.filename.find('.zip') != -1:
                print 'unzip -o /tmp/' + u.filename + ' -d ' + str(path)
                self.container.execute('unzip -o /tmp/' + u.filename + ' -d ' + str(path))
            elif u.filename.find('.rar') != -1:
                self.container.execute('unrar e -o+ /tmp/' + u.filename + ' ' + str(path) + '/')

    def ManualZipSettingsInstall(self, answer):
        if answer:
            u.removeSetting()
        self['conn'].setText(_('Installing new settings...'))
        self.container.execute('unzip -o /tmp/' + u.filename + ' -d /etc/enigma2/')

    def ManualRarSettingsInstall(self, answer):
        if answer:
            u.removeSetting()
        self['conn'].setText(_('Installing new settings...'))
        self.container.execute('unrar e -o+ /tmp/' + u.filename + ' /etc/enigma2/')

    def runFinished(self, retval):
        if self.isSettings:
            u.reloadSetting()
        else:
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        system('rm -f /tmp/' + u.filename)
        self['conn'].setText(_('Addon: %s\ninstalled succesfully!') % u.filename)
        self.readTmp()
        if fileExists('/tmp/.restartE2'):
            system('rm -f /tmp/.restartE2')
            msg = 'Enigma2 will be now hard restarted to complete package installation.\nDo You want restart enigma2 now?'
            box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle('Restart enigma')

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].setText(_('Process Killed by user.\nAddon not installed correctly!'))

    def restartEnigma2(self, answer):
        if answer:
            self.session.open(TryQuitMainloop, 3)


class ManualSelection(Screen, HelpableScreen):
    skin = '\n\t\t<screen name="FileBrowser" position="0,0" size="1280,720" backgroundColor="transparent" flags="wfNoBorder" >\n\t\t<widget source="Title" render="Label" zPosition="2" position="150,31" size="500,40" halign="center" font="Regular;24" foregroundColor="yellow" transparent="1" backgroundColor="transpBlack" />\n\t\t<widget name="filelist" position="110,100" size="580,400" scrollbarMode="showOnDemand" transparent="1" />\n\t\t<widget source="key_red"    render="Label" position="55,659"  zPosition="1" size="165,21" font="Regular;20" halign="center" valign="center" backgroundColor="red" />\n\t\t<widget source="key_green"  render="Label" position="263,659" zPosition="1" size="165,21" font="Regular;19" halign="center" valign="center" backgroundColor="green" foregroundColor="black" />\n\t</screen> '

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skin = ManualSelection.skin
        HelpableScreen.__init__(self)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Select'))
        self.filelist = FileList('/', matchingPattern='')
        self['filelist'] = self.filelist
        self['FilelistActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.use,
         'red': self.exit,
         'ok': self.ok,
         'cancel': self.exit})
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_('Select target path'))

    def ok(self):
        if self.filelist.canDescent():
            self.filelist.descent()

    def use(self):
        print '[ManualSelection]:', self['filelist'].getCurrentDirectory()
        if self['filelist'].getCurrentDirectory() is not None:
            u.instpath = self['filelist'].getCurrentDirectory()
            print '[ManualSelection]:', u.instpath
            self.close(self['filelist'].getCurrentDirectory())
        else:
            print '[ManualSelection]:Error in getting directory'
        return

    def exit(self):
        self.close(False)


class AddonsRemove(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="conn" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = ListboxE1(self.list)
        self['conn'] = Label('')
        self['title'] = Label(_('Remove Addons'))
        self['key_red'] = Label(_('Cancel'))
        self['conn'].hide()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.cancel,
         'back': self.cancel})
        self.onLayoutFinish.append(self.readTmp)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Remove Addons'))

    def readTmp(self):
        loadunidir.load()
        del self.list[:]
        if len(loadunidir.uni_list) > 0:
            for fil in loadunidir.uni_list:
                res = [fil]
                res.append(MultiContentEntryText(pos=(0, 5), size=(340, 32), font=0, text=fil[1][:-10]))
                self.list.append(res)

        else:
            self['conn'].show()
            self['conn'].setText(_('Nothing to uninstall!'))
        self['list'].l.setList(self.list)

    def KeyOk(self):
        if not self.container.running():
            if len(loadunidir.uni_list) > 0:
                self.sel = self['list'].getSelectionIndex()
                for p in loadunidir.uni_list:
                    if p[0] == self.sel:
                        u.filename = p[1]

                msg = _('Do you want remove the addon:\n%s?') % u.filename[:-10]
                box = self.session.openWithCallback(self.removeAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle('Remove Addon')
            else:
                self.close()

    def removeAddons(self, answer):
        if answer is True:
            self['conn'].show()
            self['conn'].setText(_('Removing: %s.\nPlease wait...') % u.filename[:-10])
            self.container.execute('/usr/uninstall/' + u.filename)

    def runFinished(self, retval):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.readTmp()
        self['conn'].setText(_('Addons: %s\nremoved succeffully.') % u.filename[:-10])

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].setText(_('Process Killed by user.\nAddon not removed completly!'))


class ScriptExecuter(Screen):
    skin = '\n\t<screen position="150,100" size="420,400" title="Script Executer" >\n\t\t<widget name="list" position="0,0" size="420,400" scrollbarMode="showOnDemand" />\n\t</screen>'

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self['list'] = MenuList([])
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.run,
         'cancel': self.close}, -1)
        self.onLayoutFinish.append(self.loadScriptList)

    def loadScriptList(self):
        try:
            list = listdir('/usr/script/executor')
            list = [ x[:-3] for x in list if x.endswith('.sh') ]
        except:
            list = []

        self['list'].setList(list)

    def run(self):
        try:
            script = self['list'].getCurrent()
        except:
            script = None

        if script is not None:
            title = script
            script = '/usr/script/executor/%s.sh' % script
            self.session.open(Console1, title, cmdlist=[script])
        return


class URLInput(Screen):
    skin = '\n\t\t<screen position="130,150" size="600,200" title="URL Crypt Panel" >\n\t\t\t<widget name="myLabel" position="10,60" size="400,40" font="Regular;20"/>\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self['myLabel'] = Label(_('please press OK to insert an URL to crypt'))
        self['myActionMap'] = ActionMap(['SetupActions'], {'ok': self.myInput,
         'cancel': self.cancel}, -1)

    def myInput(self):
        self.session.openWithCallback(self.askForWord, InputBox, title=_('Please enter an URL'), text=' ' * 100, maxSize=100, type=Input.TEXT)

    def askForWord(self, word):
        if word is None:
            pass
        else:
            str2 = 'None'
            password = 'dktp84067ll'
            str2 = t.xor_crypt(word, password)
            if str2 != 'None':
                if fileExists('/tmp/URLcrypted'):
                    system('rm -f /tmp/URLcrypted')
                os.system('echo "#c' + str2 + '" > /tmp/URLCrypted')
                msg = _('URLCrypted successfully created in in /tmp')
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
            else:
                msg = _('"Crypt Failed"')
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
        return

    def cancel(self):
        self.close(None)
        return


class SelectPaths(Screen, ConfigListScreen):
    skin = '\n\t\t<screen position="center,center" size="640,460">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="10,0" size="140,40" alphatest="on"/>\n\t\t<widget source="key_red" render="Label" position="10,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" \t\ttransparent="1"/>\n\t\t<widget name="config" position="10,50" size="620,200" scrollbarMode="showOnDemand" />\n\t\t<widget source="freespace" render="Label" position="10,350" size="620,100" zPosition="10" font="Regular;21" halign="left" valign="bottom" backgroundColor="#25062748" transparent="1" />\n\t\t</screen> '

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = StaticText(_('Cancel'))
        self['freespace'] = StaticText()
        ConfigListScreen.__init__(self, [])
        self.list = []
        self.initConfigList()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'red': self.cancel,
         'cancel': self.cancel,
         'ok': self.ok}, -2)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Select paths'))

    def initConfigList(self):
        list_device = _('Available device: \n')
        mountpoints = [ p.mountpoint for p in harddiskmanager.getConfiguredStorageDevices() ]
        mountpoints.sort(reverse=True)
        self.default = ['/usr/share/enigma2']
        self.default += mountpoints
        for x in self.default:
            path = x + '/'
            list_device += x + ' : ' + str(t.getVarSpace(path)) + '\n'

        if config.usage.picon_path.value not in (x for x in self.default):
            print 'Wrong picon path in default config....reset to /usr/share/enigma2'
            config.usage.picon_path.value = '/usr/share/enigma2'
            config.usage.picon_path.save()
        self.piconpath = ConfigSelection(default=config.usage.picon_path.value, choices=self.default)
        self.piconpath_entry = getConfigListEntry(_('Select path'), self.piconpath)
        self.list.append(self.piconpath_entry)
        self['config'].setList(self.list)
        self['freespace'].setText(list_device)

    def ok(self):
        u.instpath = self.piconpath.value + '/'
        self.close(True)

    def cancel(self):
        self.close(False)


class DEManagerOpen():
    __module__ = __name__

    def __init__(self):
        self['DEManagerOpen'] = ActionMap(['InfobarExtensions'], {'DEManager': self.DEManagerPanelOpen})

    def DEManagerPanelOpen(self):
        self.session.open(DEManager)


class DEPluginsPanelOpen():
    __module__ = __name__

    def __init__(self):
        self['DEPluginsPanelOpen'] = ActionMap(['InfobarSubserviceSelectionActions'], {'DEPlugins': self.DEPluginsOpen})

    def DEPluginsOpen(self):
        self.session.open(PluginBrowser)
