from Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Screens.TextBox import TextBox
from Components.Label import Label, MultiColorLabel
from Components.Button import Button
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.ConfigList import ConfigList
from Components.config import config, ConfigSelection, ConfigSlider, ConfigSubsection, ConfigYesNo, NoSave, ConfigText, getConfigListEntry, ConfigNothing, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.MenuList import MenuList
from Components.PluginList import *
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, pathExists, fileExists
from Tools.LoadPixmap import LoadPixmap
from Tools.HardwareInfo import HardwareInfo
from os import access, F_OK, R_OK, system, path, popen
import re, sys
from enigma import eTimer, eConsoleAppContainer
from xml.etree.cElementTree import ElementTree
from DE.DELibrary import Tool
t = Tool()
WAIT_READ = _('Please wait while reading status...')
WAIT_DOWNLOAD = _('Please wait while downloading drivers...')
WAIT_RESTART = _('Please wait while restarting usbtuner...')
WAIT_FOR_COMMAND = _('Please wait while executing command...')
GRAY = 0
RED = 1
GREEN = 2
NAME = 0
VID_PID = 1
STATE = 2
driver_list = []

class DEVSwap(Screen):
    skin = '\n\t<screen name="InputDeviceSelection" position="center,center" size="560,400" title="Select input device">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="280,0" size="140,40" alphatest="on"/>\n\t\t<widget name="key_red"  position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center"  transparent="1"/>\n\t\t<widget name="key_green"  position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center"  transparent="1"/>\n\t\t<widget name="key_blue"  position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center"  transparent="1"/>\n\t\t<widget name="list" position="5,50" size="550,280" zPosition="10" scrollbarMode="showOnDemand"/>\n\t\t<ePixmap pixmap="skin_default/div-h.png" position="0,340" zPosition="1" size="560,2"/>\n\t\t<widget name="introduction"  position="0,350" size="560,50" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1"/>\n\t</screen>'
    VERSION = '2.0'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.edittext = _('Press OK to edit the settings.')
        self['key_red'] = Label(_('Close'))
        self['key_green'] = Label(_('Activate'))
        self['key_blue'] = Label(_('Delete'))
        self['introduction'] = Label(self.edittext)
        self['actions'] = NumberActionMap(['ColorActions',
         'CiSelectionActions',
         'WizardActions',
         'SetupActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'blue': self.DeleteSwap,
         'green': self.CreateSwap,
         'red': self.close,
         'ok': self.CreateSwap,
         'back': self.close}, -1)
        self.currentIndex = 0
        self.swap_size = {'8 MB': 8192,
         '16 MB': 16384,
         '32 MB': 32768,
         '64 MB': 65536,
         '128 MB': 131072,
         '256 MB': 262144,
         '512 MB': 524288}
        self.list = []
        self.myswap = []
        self.mountpoints = []
        self.swappresent = False
        self['list'] = ConfigList(self.list)
        self.refresh()
        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.cleanup)

    def layoutFinished(self):
        self.setTitle(_('Swap file creation v. %s') % self.VERSION)

    def cleanup(self):
        print 'DEVSwap Closed'
        if fileExists('/tmp/mounts.log'):
            system('rm -r /tmp/mounts.log')

    def keyLeft(self):
        self['list'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['list'].handleKey(KEY_RIGHT)

    def refresh(self):
        self.readMount()
        self.readswap()
        self.updateList()

    def readswap(self):
        try:
            del self.myswap[:]
            self.swappresent = False
            f = open('/proc/swaps', 'r')
            for line in f.readlines():
                if line.find('/swap') != -1:
                    tempmyswap = line.split()

            f.close()
            if tempmyswap:
                self.myswap = [tempmyswap[0][:-5], tempmyswap[2]]
                self['key_green'].hide()
                self['key_blue'].show()
                self['introduction'].setText(_('Swap file founded on %s') % tempmyswap[0][:-5])
                self.swappresent = True
            else:
                self.myswap = ['None', 'None']
                self['introduction'].setText(_('Press OK to edit the settings.'))
                self['key_blue'].hide()
                self['key_green'].show()
        except:
            print 'Error in swap file reading'
            self.myswap = ['None', 'None']
            self['introduction'].setText(_('Press OK to edit the settings.'))
            self['key_blue'].hide()
            self['key_green'].show()

    def updateList(self):
        del self.list[:]
        if self.myswap[0] == 'None':
            path_cfg = ConfigSelection(default=_(self.myswap[0].strip()), choices=self.mountpoints)
            self.list.append(getConfigListEntry(_('Swap file path'), path_cfg))
        else:
            path_cfg = ConfigSelection(default=_(self.myswap[0].strip()), choices=[_(self.myswap[0].strip())])
            self.list.append(getConfigListEntry(_('Swap file path'), path_cfg))
        if self.swappresent:
            size_cfg = ConfigSelection(default=self.myswap[1], choices=[self.myswap[1]])
            self.list.append(getConfigListEntry(_('Swap file size'), size_cfg))
        elif self.myswap[1] == 'None':
            size_cfg = ConfigSelection(default='32 MB', choices=self.swap_size.keys())
            self.list.append(getConfigListEntry(_('Swap file size'), size_cfg))
        self['list'].list = self.list
        self['list'].l.setList(self.list)

    def CreateSwap(self):
        if not self.swappresent:
            selection = self['list'].getCurrent()
            self.currentIndex = self['list'].getCurrentIndex()
            self['list'].setCurrentIndex(0)
            if self['list'].getCurrent()[1].getText() != _('None'):
                swapfile = self['list'].getCurrent()[1].getText() + '/swap'
            else:
                self.myMsg(_('%s is not a valid path') % _(self['list'].getCurrent()[1].getText()))
                return
            self['list'].setCurrentIndex(1)
            size = self.swap_size[self['list'].getCurrent()[1].getText()]
            if fileExists('/etc/swapon'):
                system('rm -r /etc/swapon')
            system('echo ' + swapfile + ' > /etc/swapon')
            cmd = []
            cmd.append("echo 'Creating swap file...'")
            cmd.append('dd if=/dev/zero of=' + swapfile + ' bs=1024 count=' + str(size))
            cmd.append("echo 'Creating swap device...'")
            cmd.append('mkswap ' + swapfile)
            cmd.append("echo 'Activating swap device...'")
            cmd.append('swapon ' + swapfile)
            cmd.append('free')
            cmd.append("echo 'Press EXIT to come back'")
            self.session.openWithCallback(self.refresh, Console, title=_('Creating swap file...'), cmdlist=cmd)
        else:
            self.myMsg(_('Swap file already active'))

    def DeleteSwap(self):
        if self.swappresent:
            selection = self['list'].getCurrent()
            self.currentIndex = self['list'].getCurrentIndex()
            self['list'].setCurrentIndex(0)
            if self['list'].getCurrent()[1].getText() != _('None'):
                swapfile = self['list'].getCurrent()[1].getText() + '/swap'
            else:
                self.myMsg(_('%s is not a valid path') % _(self['list'].getCurrent()[1].getText()))
                return
            if fileExists('/etc/swapon'):
                system('rm -r /etc/swapon')
            cmd = []
            cmd.append("echo 'Dectivating swap device...'")
            cmd.append('swapoff ' + swapfile)
            cmd.append("echo 'Removing swap file...'")
            cmd.append('rm -f ' + swapfile)
            cmd.append("echo 'Press EXIT to come back'")
            self.session.openWithCallback(self.refresh, Console, title=_('Deleting swap file...'), cmdlist=cmd)
        else:
            self.myMsg(_('Swap file not found'))

    def readMount(self):
        del self.mountpoints[:]
        try:
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/') != -1:
                    linesplit = line.split()
                    self.mountpoints.append(linesplit[1].strip())

            f.close()
            self.mountpoints.append(_('None'))
        except:
            self.myMsg(_('Function get mount points failed'))

    def myMsg(self, entry):
        self.session.open(MessageBox, entry, MessageBox.TYPE_INFO)


class BootServices(Screen, ConfigListScreen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="conn" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" backgroundColor="#6565ff" />\n\t\t\t<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.initPath_S = ['/etc/rc2.d',
         '/etc/rc3.d',
         '/etc/rc4.d',
         '/etc/rc5.d']
        self.initPath_K = ['/etc/rc0.d', '/etc/rc1.d', '/etc/rc6.d']
        self.servicesList = [('nfsserver',
          'S20nfsserver',
          'K20nfsserver',
          _('Activate NFS Server at boot?'),
          '/etc/init.d/nfsserver'),
         ('samba',
          'S20samba',
          'K20samba',
          _('Activate Samba Server at boot?'),
          '/etc/init.d/samba'),
         ('openvpn',
          'S30openvpn',
          'K30openvpn',
          _('Activate OpenVPN at boot?'),
          '/etc/init.d/openvpn'),
         ('ipupdate',
          'S20ipupdate',
          'K20ipupdate',
          _('Activate IpUpdate at boot?'),
          '/etc/init.d/ipupdate'),
         ('inadyn',
          'S30inadyn',
          'K30inadyn',
          _('Activate InaDyn at boot?'),
          '/etc/init.d/inadyn'),
         ('sshd',
          'S09sshd',
          'K09sshd',
          _('Activate Openssh (SSHD) at boot?'),
          '/etc/init.d/sshd'),
         ('busybox-cron',
          'S99cron',
          'K99cron',
          _('Activate Crontab at boot?'),
          '/etc/init.d/busybox-cron'),
         ('pcscd',
          'S19pcscd',
          'K19pcscd',
          _('Activate Omnikey Support at boot?'),
          '/etc/init.d/pcscd'),
         ('noip2',
          'S90noip',
          'K90noip',
          _('Activate No IP Updater at boot?'),
          '/etc/init.d/noip2')]
        self.instService = []
        self.serviceconfig = {}
        ConfigListScreen.__init__(self, self.list)
        self['oktext'] = Label(_('Save'))
        self['canceltext'] = Label(_('Exit'))
        self['conn'] = Label('')
        self['conn'].hide()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'back': self.close,
         'green': self.saveSetting})
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.loadSetting)

    def setWindowTitle(self):
        self.setTitle(_('Boot services'))

    def loadSetting(self):
        del self.list[:]
        del self.instService[:]
        i = 0
        while i < len(self.servicesList):
            ser = self.servicesList[i][4]
            if fileExists(ser):
                self.instService.append(self.servicesList[i])
            i = i + 1

        for s in self.instService:
            self.serviceconfig[s[0]] = NoSave(ConfigYesNo(default=False))
            self.list.append(getConfigListEntry(s[3], self.serviceconfig[s[0]]))
            if fileExists('/etc/rc3.d/' + s[1]):
                self.serviceconfig[s[0]].value = True
            self['config'].list = self.list
            self['config'].l.setList(self.list)

    def saveSetting(self):
        self['conn'].show()
        self['conn'].setText(_('Saving Setting. Please wait...'))
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.saveConf)
        self.activityTimer.start(300, False)

    def saveConf(self):
        self.activityTimer.stop()
        for p in self.initPath_S:
            for s in self.instService:
                system({True: 'ln -s ../init.d/%s %s/%s' % (s[0], p, s[1]),
                 False: 'rm -f %s/%s' % (p, s[1])}[self.serviceconfig[s[0]].value])

        for q in self.initPath_K:
            for t in self.instService:
                system({True: 'ln -s ../init.d/%s %s/%s' % (t[0], q, t[2]),
                 False: 'rm -f %s/%s' % (q, t[2])}[self.serviceconfig[t[0]].value])

        self.close()


class RunServices(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440">\n\t\t\t<widget name="list" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.servicesList = [('nfs', '/etc/init.d/nfsserver', '[nfsd]', 'NFS Server'),
         ('smb', '/etc/init.d/samba', '/usr/sbin/smbd', 'Samba'),
         ('vpn', '/etc/init.d/openvpn', '/usr/sbin/openvpn', 'OpenVPN'),
         ('ipudate', '/etc/init.d/ipupdate', '/usr/bin/ez-ipupdate', 'IpUpdate'),
         ('inadyn', '/etc/init.d/inadyn', 'inadyn', 'InaDyn'),
         ('sshd', '/etc/init.d/sshd', 'sshd', 'Openssh (SSHD)'),
         ('crond', '/etc/init.d/busybox-cron', '/usr/sbin/crond', 'Crontab'),
         ('pcscd', '/etc/init.d/pcscd', '/usr/sbin/pcscd', 'Omnikey Smart Card'),
         ('noip2', '/etc/init.d/noip2', '/usr/bin/noip2', 'No IP Updater')]
        self['list'] = ConfigList(self.list)
        self.instService = []
        self.servicestatus = {}
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label(_('Setup'))
        self['actions'] = NumberActionMap(['ColorActions',
         'CiSelectionActions',
         'WizardActions',
         'SetupActions'], {'ok': self.KeyOk,
         'yellow': self.openSetting,
         'red': self.close,
         'left': self.keyLeft,
         'right': self.keyRight,
         'back': self.close}, -1)
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateList)

    def keyLeft(self):
        self['list'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['list'].handleKey(KEY_RIGHT)

    def setWindowTitle(self):
        self.setTitle(_('Start/Stop services'))

    def openSetting(self):
        self.session.open(BootServices)

    def KeyOk(self):
        ser = self['list'].getCurrent()[0]
        if ser:
            for s in self.servicesList:
                if s[3] == ser:
                    cmd = {'Running': s[1] + ' stop',
                     'Stopped': s[1] + ' start'}[self.servicestatus.get(s[0])]

            self.session.openWithCallback(self.executedScript, Console, title=_('Execute command: ') + cmd, cmdlist=[cmd])

    def executedScript(self, *answer):
        self.updateList()

    def readStatus(self):
        for ser in self.servicesList:
            self.servicestatus[ser[0]] = 'Stopped'

        system('ps -ef > /tmp/status.log')
        f = open('/tmp/status.log', 'r')
        for line in f.readlines():
            for ser in self.servicesList:
                if line.find(ser[2]) != -1 or line.find(ser[0]) != -1:
                    self.servicestatus[ser[0]] = 'Running'

        f.close()

    def updateList(self):
        self.readStatus()
        del self.list[:]
        del self.instService[:]
        runstatus = [_('Running'), _('Stopped')]
        i = 0
        while i < len(self.servicesList):
            ser = self.servicesList[i][1]
            if fileExists(ser):
                self.instService.append(self.servicesList[i])
            i = i + 1

        for s in self.instService:
            if self.servicestatus[s[0]] == 'Running':
                path_cfg = ConfigSelection(default=_('Running'), choices=runstatus)
                self.list.append(getConfigListEntry(s[3], path_cfg))
            else:
                path_cfg = ConfigSelection(default=_('Stopped'), choices=runstatus)
                self.list.append(getConfigListEntry(s[3], path_cfg))

        self['list'].list = self.list
        self['list'].l.setList(self.list)


class DttPanel(Screen, HelpableScreen):
    skin = '\n\t<screen name="DttPanel" position="center,center" size="948,582" title="DVB-T Panel">\n\t\t\t<widget source="newslist" render="Listbox" position="14,49" size="923,500" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (60, 0), size = (520, 20), font=0,color=0xCC0000, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0), # index 0 is the title\n\t\t\t\t\t\tMultiContentEntryText(pos = (60, 30), size = (700, 30), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_BOTTOM, text = 1), # index 2 is the device info\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (55, 55), png = 2), # index 3 is the device pixmap\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (0, 96), size = (1000, 2), png = 3), # index 3 is the div pixmap\n\t\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 20),gFont("Regular", 16)],\n\t\t\t\t"itemHeight": 50\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget name="conn" position="0,600" size="600,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" />\n\t</screen> '

    def __init__(self, session):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self['conn'] = Label('')
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label(_('Install'))
        self['key_blue'] = Label(_('Clean all'))
        self['key_green'] = Label(_('Available driver'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.ok,
         'cancel': self.exit,
         'blue': self.cleanAll,
         'red': self.exit,
         'yellow': self.install,
         'green': self.listMode}, -1)
        self['conn'].hide()
        self['key_yellow'].hide()
        self.list = []
        self.boxID = ''
        self.fullList = 'N'
        self.container_download = eConsoleAppContainer()
        self.container_download.appClosed.append(self.runAfterDownload)
        self['newslist'] = List(self.list)
        self['newslist'].onSelectionChanged.append(self.selectionChanged)
        self.onLayoutFinish.append(self.layoutFinished)

    def ok(self):
        pass

    def cleanAll(self):
        msg = _('Do you really want to erase config file and drivers?')
        box = self.session.openWithCallback(self.cleanConfig, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('Clean all'))

    def cleanConfig(self, answer):
        if answer is True:
            if fileExists('/usr/bin/Dtt.sh'):
                system('rm -f /usr/bin/Dtt.sh')
            if path.isdir('/lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb' % self.boxID):
                system('rm -rf /lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb' % self.boxID)
            runServices = popen('ps -e', 'r').readlines()
            for entry in runServices:
                if entry.find('usbtuner') != -1:
                    system('killall -9 usbtuner')

            del self.list[:]
            self.parseUsbBus()
            self.MsgInfo(_('Configuration cleaned'))

    def install(self):
        if self['newslist'].getCurrent()[4] == 'Y' or self.fullList == 'Y':
            msg = _('Do you want install the driver for:\n%s?') % self['newslist'].getCurrent()[0]
            box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle(_('Install Driver'))
        else:
            self.MsgError(_('Nothing to install'))

    def installAddons(self, answer):
        if answer is True:
            id = self['newslist'].getCurrent()[1]
            self.buildScript(id[4:])

    def selectionChanged(self):
        if len(self['newslist'].list) > 0:
            if self['newslist'].getCurrent()[4] == 'Y' or self.fullList == 'Y':
                self['key_yellow'].show()
            else:
                self['key_yellow'].hide()
        else:
            self['key_yellow'].hide()

    def layoutFinished(self):
        self.setTitle(_('Dream Elite DVB-T Panel - Beta 1.2'))
        self.boxID = self.getBoxType()
        self.container_download.execute('wget ' + t.readAddonsUrl() + 'DTT/DTT.xml -O /tmp/DTT.xml')

    def buildScript(self, serial):
        global driver_list
        scriptext = []
        scriptext.append('#!/bin/sh \n')
        for findid in driver_list:
            if findid[1].find(serial) != -1:
                scriptext.append('#ID:' + serial + ' \n')
                instDriver = findid[3].split(';')
                instFirmware = findid[2].split(';')
                for ndriver in instDriver:
                    if ndriver.find('sleep') == -1:
                        scriptext.append('insmod /lib/modules/3.2-' + self.boxID + '/kernel/drivers/media/dvb/dvb-usb/' + ndriver + ' \n')
                    else:
                        scriptext.append(ndriver + ' \n')

                scriptext.append('usbtuner &>/dev/null & \n')

        if len(scriptext) > 0:
            try:
                thefile = open('/usr/bin/Dtt.sh', 'w')
                for item in scriptext:
                    thefile.write('%s' % item)

                thefile.close()
                system('chmod 0755 /usr/bin/Dtt.sh')
            except:
                self.MsgError(_('Config script building failed'))

            self.downloadDriver(instDriver, instFirmware)
        else:
            self.MsgError(_('Nothing to write'))

    def downloadDriver(self, drvlist, frwlist):
        fileError = False
        if not path.isdir('/lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb' % self.boxID):
            system('mkdir /lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb' % self.boxID)
        try:
            for item in drvlist:
                if item.find('sleep') == -1:
                    print 'wget ' + t.readAddonsUrl() + 'DTT/%s/driver/%s -O /lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb/%s' % (self.boxID,
                     item,
                     self.boxID,
                     item)
                    system('wget ' + t.readAddonsUrl() + 'DTT/%s/driver/%s -O /lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb/%s' % (self.boxID,
                     item,
                     self.boxID,
                     item))

            for fitem in frwlist:
                if fitem.find('none') == -1:
                    print 'wget ' + t.readAddonsUrl() + 'DTT/firmware/%s -O /lib/firmware/%s' % (fitem, fitem)
                    system('wget ' + t.readAddonsUrl() + 'DTT/firmware/%s -O /lib/firmware/%s' % (fitem, fitem))

            for item in drvlist:
                if item.find('sleep') == -1:
                    if not fileExists('/lib/modules/3.2-%s/kernel/drivers/media/dvb/dvb-usb/%s' % (self.boxID, item)):
                        self.MsgError(_('Driver %s not available for %s') % (item, self.boxID))
                        fileError = True
                        break

            for item in frwlist:
                if fitem.find('none') == -1:
                    if not fileExists('/lib/firmware/%s' % item):
                        self.MsgError(_('Firmware %s not available') % item)
                        fileError = True
                        break

            if not fileExists('/usr/bin/Dtt.sh'):
                fileError = True
            if not fileError:
                msg = _('Config script and download succeed\nEnigma2 will be restarted to complete DVB-T tuner startup.\nDo You want restart enigma2 now?')
                box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Restart Enigma2'))
            else:
                if fileExists('/usr/bin/Dtt.sh'):
                    system('rm -f /usr/bin/Dtt.sh')
                self.MsgError(_('Download failed'))
        except:
            if fileExists('/usr/bin/Dtt.sh'):
                system('rm -f /usr/bin/Dtt.sh')
            self.MsgError(_('Download failed'))

    def parseUsbBus(self):
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        try:
            catOutput = popen('cat /proc/bus/usb/devices', 'r').readlines()
            i = 0
            DttIsPresent = False
            while i < len(catOutput):
                piconstate = self.buildListEntry('NO')
                canInstall = 'N'
                if catOutput[i].find('Vendor=') != -1:
                    if catOutput[i + 1].find(self.boxID) == -1:
                        parts = catOutput[i].split(' ')
                        for part in parts:
                            if part.find('Vendor=') != -1:
                                id1 = part[7:]
                            elif part.find('ProdID=') != -1:
                                id2 = part[7:]

                        id = id1 + ':' + id2
                        if catOutput[i + 2].find('Product=') != -1:
                            d1 = catOutput[i + 2]
                            description1 = d1[12:].rstrip('\n')
                        if catOutput[i + 1].find('Manufacturer=') != -1:
                            d2 = catOutput[i + 1]
                            if not d2:
                                d2 = 'S:  Manufacturer= '
                            description = description1 + ' ' + d2[17:]
                        for findid in driver_list:
                            if findid[1].find(id) != -1:
                                piconstate = self.buildListEntry('NODRV')
                                canInstall = 'Y'
                                if self.chkDttScript(id) == 'Y':
                                    piconstate = self.buildListEntry('OK')
                                    canInstall = 'N'
                                    DttIsPresent = True
                                elif findid[3].find('none') != -1:
                                    piconstate = self.buildListEntry('NO')
                                    canInstall = 'N'
                                tmplist = [description.strip(),
                                 'ID: ' + id,
                                 piconstate,
                                 divpng,
                                 canInstall]
                                self.list.append(tmplist)
                                break

                i += 1

            if not DttIsPresent and fileExists('/usr/bin/Dtt.sh'):
                system('rm -rf /usr/bin/Dtt.sh')
        except:
            self['conn'].show()
            self['conn'].setText(_('Usb bus scan error'))

        if len(self.list) == 0:
            self.list.append([_('No device found'),
             'ID: 0000:0000',
             self.buildListEntry('NO'),
             divpng,
             'N'])
        self['newslist'].setList(self.list)

    def buildListEntry(self, state):
        if state == 'OK':
            image_name = 'button_green.png'
        elif state == 'NODRV':
            image_name = 'button_yellow.png'
        else:
            image_name = 'button_red.png'
        pixmap = LoadPixmap(cached=True, path='/usr/share/enigma2/skin_default/buttons/' + image_name)
        return pixmap

    def chkDttScript(self, serial):
        if fileExists('/usr/bin/Dtt.sh'):
            f = open('/usr/bin/Dtt.sh', 'r')
            for line in f.readlines():
                if line.strip() == '#ID:' + serial:
                    f.close()
                    return 'Y'

            f.close()
            return 'ERR'
        return 'N'

    def runAfterDownload(self, retval):
        if fileExists('/tmp/DTT.xml'):
            try:
                self.get_list('/tmp/DTT.xml')
                self.parseUsbBus()
            except:
                self['conn'].show()
                self['conn'].setText(_('Driver index file not correctly formatted!'))

        else:
            self['conn'].show()
            self['conn'].setText(_('Server not found!\nPlease check internet connection.'))

    def get_list(self, filename):
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        del driver_list[:]
        tree = ElementTree()
        tree.parse(filename)
        for channel in tree.findall('line'):
            id = channel.findtext('ID')
            name = channel.findtext('name')
            firmware = channel.findtext('firmware')
            driver = channel.findtext('driver')
            date = channel.findtext('date')
            chan_tulpe = [name,
             id,
             firmware,
             driver,
             date]
            driver_list.append(chan_tulpe)

    def getBoxType(self):
        return HardwareInfo().get_device_name().strip()

    def MsgInfo(self, entry):
        self.session.open(MessageBox, entry, MessageBox.TYPE_INFO)

    def MsgError(self, entry):
        self.session.open(MessageBox, entry, MessageBox.TYPE_ERROR)

    def restartEnigma2(self, answer):
        if answer:
            self.session.open(TryQuitMainloop, 3)
        else:
            del self.list[:]
            self.parseUsbBus()

    def exit(self):
        if fileExists('/tmp/DTT.xml'):
            system('rm -f /tmp/DTT.xml')
        self.close()

    def listMode(self):
        self.list = []
        self['newslist'].setList(self.list)
        if self.fullList == 'N':
            self.fullList = 'Y'
            self['key_green'].setText(_('Detected driver'))
            self.fullDriversList()
        else:
            self.fullList = 'N'
            self['key_green'].setText(_('Available driver'))
            self.layoutFinished()

    def fullDriversList(self):
        self.setTitle(_('DVB-T Available Driver'))
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        for entry in driver_list:
            if entry[3].find('none') == -1:
                tmplist = [entry[0],
                 'ID: ' + entry[1],
                 entry[2],
                 entry[3],
                 entry[4],
                 divpng]
                self.list.append(tmplist)

        self['newslist'].setList(self.list)
