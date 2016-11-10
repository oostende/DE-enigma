from Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Sources.List import List
from Components.Button import Button
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.About import about
from Tools.Directories import fileExists
from os import system, popen, path
from Screens.Console import Console
from enigma import eConsoleAppContainer, eServiceReference
from Components.ProgressBar import ProgressBar
from Components.Harddisk import harddiskmanager
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE
from Components.config import config, configfile, ConfigYesNo, ConfigText, getConfigListEntry, ConfigNothing, NoSave
from Components.ConfigList import ConfigListScreen
from Screens.HelpMenu import HelpableScreen
from Screens.HarddiskSetup import HarddiskDriveSelection
from Screens.RecordPaths import RecordPathsSettings
from Screens.InfoBar import MoviePlayer
from DE.DELibrary import Tool
from DE.DEManager import ReadAddons
from xml.etree.cElementTree import fromstring, ElementTree
t = Tool()

def getUnit(val):
    if val >= 1048576:
        return '%.1f%s' % (float(val) / 1048576, ' Gb')
    return '%.1f%s' % (float(val) / 1024, ' Mb')


def getSize(a, b, c):
    return (getUnit(a), getUnit(b), getUnit(c))


class AboutDE(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Label(_('Exit'))
        self['Disclaimer'] = StaticText(_('DISCLAIMER'))
        disclamer = _('IN ACCORDANCE WITH THE LAW THIS SOFTWARE CONTAINS ONLY SYSTEM ADDITIONS & GRAPHIC CHANGES.\n')
        disclamer += _('THE DREAM-ELITE IMAGE DOES NOT CONTAIN ANY EMULATORS, KEYS, SOFTCAMS OR OTHER SYSTEM FOR VIEWING PAY-TV WITH OR WITHOUT A PAID SUBSCRIPTION.\n')
        disclamer += _('THE DREAM-ELITE IMAGE DOES NOT CONTAIN ANY FEEDS TO DOWNLOAD PLUGINS OR EMULATORS FROM EXTERNAL SERVERS OR SOFTWARE THAT MAY BE USED FOR ILLEGAL PURPOSES SUCH AS CARD SHARING.\n\n')
        disclamer += _('LICENSE (TERM OF USE)\n\n')
        disclamer += _('THE DREAM-ELITE IMAGE IS ISSUED FOR THE FREE USE FOR ALL USERS PROVIDED THAT IT WILL NOT BE CHANGED IN ANY WAY AND THAT IT WILL ONLY BE USED FOR LAWFUL PURPOSES.\n')
        disclamer += _('SKIN AND ALL OTHER CONTENT INSIDE THIS IMAGE IS PROPERTY OF DREAM-ELITE AND IT IS NOT ALLOWED TO MODIFY OR TO COPY WITHOUT PERMISSION OF DREAM-ELITE\n')
        disclamer += _('ANY CHANGES OR ADDITIONS TO DREAM-ELITE IMAGE THAT INVOLVE UNLAWFUL USE OF THE IMAGE SUCH AS CARD-SHARING AND EMULATORS ARE NOT ALLOWED AND CAUSE THE REVOKE OF THIS LICENSE\n')
        self['Dissociation'] = StaticText(_(disclamer))
        self['Line1'] = StaticText(_('BEST REGARDS'))
        self['Line2'] = StaticText(_('Ferrari3005 Admin of www.dream-elite.net '))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close,
         'red': self.close,
         'ok': self.close})


class DevInfo(Screen, HelpableScreen):
    skin = '\n\t<screen name="DevInfo" position="154,89" size="948,582" title="DE Infomation">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="10,0" size="200,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="260,0" size="200,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="505,0" size="200,40" alphatest="on"/>\n\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="735,0" size="200,40" alphatest="on"/>\n\t\t<widget source="key_red" render="Label" position="10,-4" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>\n\t\t<widget source="key_green" render="Label" position="260,0" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>\n\t\t<widget source="key_yellow" render="Label" position="505,0" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1"/>\n\t\t<widget source="key_blue" render="Label" position="735,0" zPosition="1" size="200,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1"/>\n\t\t<widget source="hddlist" render="Listbox" position="14,49" size="923,500" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (80, 6), size = (900, 28), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0), # index 0 is the hdd_description\n\t\t\t\t\t\tMultiContentEntryText(pos = (80, 42), size = (800, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_BOTTOM, text = 2), # index 2 is the device info\n\t\t\t\t\t\tMultiContentEntryText(pos = (80, 68), size = (800, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_BOTTOM, text = 12), # index 2 is the device info\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (2, 8), size = (55, 55), png = 7), # index 3 is the device pixmap\n\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (0, 96), size = (1000, 2), png = 9), # index 3 is the div pixmap\n\t\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 28),gFont("Regular", 20)],\n\t\t\t\t"itemHeight": 100\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget source="introduction" render="Label" position="10,545" size="980,50" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t</screen> '
    VIEW_HARDDISK = 1
    VIEW_PARTITION = 2

    def __init__(self, session):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self['key_red'] = StaticText()
        self['key_green'] = StaticText()
        self['key_yellow'] = StaticText()
        self['key_blue'] = StaticText()
        self['introduction'] = StaticText()
        self['CancelActions'] = HelpableActionMap(self, 'OkCancelActions', {'cancel': (self.keyCancel, _('Exit'))}, -2)
        self['RedColorActions'] = HelpableActionMap(self, 'ColorActions', {'red': (self.keyRed, _('Exit'))}, -2)
        self['GreenColorActions'] = HelpableActionMap(self, 'ColorActions', {'green': (self.keyGreen, _('Not used'))}, -2)
        self['YellowColorActions'] = HelpableActionMap(self, 'ColorActions', {'yellow': (self.keyYellow, _('Not used'))}, -2)
        self['BlueColorActions'] = HelpableActionMap(self, 'ColorActions', {'blue': (self.keyBlue, _('Not used'))}, -2)
        self['RedColorActions'].setEnabled(False)
        self['GreenColorActions'].setEnabled(False)
        self['YellowColorActions'].setEnabled(False)
        self['BlueColorActions'].setEnabled(False)
        self.view = self.VIEW_HARDDISK
        self.selectedHDD = None
        self.currentIndex = 0
        self.currentlyUpdating = False
        self.list = []
        self.memory = []
        self.dfmounts = []
        self['hddlist'] = List(self.list)
        self.onLayoutFinish.append(self.layoutFinished)
        return

    def layoutFinished(self):
        self.setTitle(_('DE device info panel'))
        self.currentlyUpdating = True
        self.setButtons()
        self.readmemory()
        self.updateList()

    def readmemory(self):
        try:
            self.memory = popen('free', 'r').readlines()
            self.dfmounts = popen('df | grep -e "/media" -e "/dev/root" -e "ubi0:rootfs"', 'r').readlines()
        except:
            print 'Error getting free output'

    def memoryRamScan(self):
        rampng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/ram.png'))
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        if len(self.memory) > 0:
            for line in self.memory:
                x = line.strip().split()
                if x[0] == 'Mem:':
                    Ram1 = 'Ram in use: '
                    if int(x[1]) > 1:
                        Ramperc = '%d%%' % int(int(x[2]) * 100 / int(x[1]))
                    else:
                        Ramperc = '0%'
                    Ram1 += Ramperc
                    s = getSize(int(x[1]), int(x[2]), int(x[3]))
                    Ram2 = 'Ram: %s  Used: %s  Free: %s  Shared: %s  Buf: %s' % (s[0],
                     s[1],
                     s[2],
                     getUnit(int(x[4])),
                     getUnit(int(x[5])))
                    return (Ram1,
                     0,
                     Ram2,
                     None,
                     None,
                     None,
                     'Extra line',
                     rampng,
                     None,
                     divpng,
                     None,
                     False,
                     '',
                     int(x[1]),
                     int(x[2]),
                     int(x[3]),
                     Ramperc)

        else:
            return ('No ram info available',
             0,
             '- - - -',
             None,
             None,
             None,
             'Extra line',
             rampng,
             None,
             divpng,
             None,
             False,
             '',
             0,
             0,
             0,
             0)
        return None

    def memorySwapScan(self):
        rampng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/swap.png'))
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        if len(self.memory) > 0:
            for line in self.memory:
                x = line.strip().split()
                if x[0] == 'Swap:':
                    Swap1 = 'Swap in use: '
                    if int(x[1]) > 1:
                        Swapperc = '%d%%' % int(int(x[2]) * 100 / int(x[1]))
                    else:
                        Swapperc = '0%'
                    Swap1 += Swapperc
                    s = getSize(int(x[1]), int(x[2]), int(x[3]))
                    Swap2 = 'Swap: %s  Used: %s  Free: %s' % (s[0], s[1], s[2])
                    return (Swap1,
                     0,
                     Swap2,
                     None,
                     None,
                     None,
                     'Extra line',
                     rampng,
                     None,
                     divpng,
                     None,
                     False,
                     '',
                     int(x[1]),
                     int(x[2]),
                     int(x[3]),
                     Swapperc)

        else:
            return ('No swap info available',
             0,
             '- - - -',
             None,
             None,
             None,
             'Extra line',
             rampng,
             None,
             divpng,
             None,
             False,
             '',
             0,
             0,
             0,
             0)
        return None

    def flashscan(self):
        rampng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/flash.png'))
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        for line in self.dfmounts:
            line = line.replace('part1', ' ')
            x = line.strip().split()
            if len(x) > 1:
                if x[0] == '/dev/root' or x[0].upper().find('UBI0:ROOTFS') != -1:
                    flash1 = 'Flash in use: %s' % x[4]
                    s = getSize(int(x[1]), int(x[2]), int(x[3]))
                    flash2 = 'Flash: %s Used: %s Free: %s' % (s[0], s[1], s[2])
                    return (flash1,
                     0,
                     flash2,
                     None,
                     None,
                     None,
                     '',
                     rampng,
                     None,
                     divpng,
                     None,
                     False,
                     '',
                     int(x[1]),
                     int(x[2]),
                     int(x[3]),
                     x[4])

        return ('No flash info available',
         0,
         '- - - -',
         None,
         None,
         None,
         'Extra line',
         rampng,
         None,
         divpng,
         None,
         False,
         '',
         0,
         0,
         0,
         0)

    def buildHDDList(self, hd, isOfflineStorage = False, partitionNum = False):
        tot = used = free = 0
        usedprc = '0%'
        devicedata = 'Capacity: 0  Used: 0  Free: 0 '
        divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/div-h-extended.png'))
        devicepng = onlinepng = None
        isOfflineStorageDevice = isOfflineStorage
        isConfiguredStorageDevice = isMountedPartition = isReadable = False
        uuid = currentMountpoint = partitionPath = partitionType = devicename = None
        hdd_description = device_info = ''
        numpart = 0
        onlinepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/buttons/button_green_off.png'))
        hdd_description = hd.model()
        numpart = hd.numPartitions()
        if partitionNum is False:
            if numpart == 0:
                devicename = hd.device
                uuid = harddiskmanager.getPartitionUUID(devicename)
                partitionPath = hd.dev_path
            if numpart == 1:
                devicename = hd.device + str(numpart)
                uuid = harddiskmanager.getPartitionUUID(devicename)
                partitionPath = hd.partitionPath(str(numpart))
        else:
            devicename = hd.device + str(partitionNum)
            uuid = harddiskmanager.getPartitionUUID(devicename)
            partitionPath = hd.partitionPath(str(partitionNum))
        partitionType = harddiskmanager.getBlkidPartitionType(partitionPath)
        devicepng = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/internal_hdd.png'))
        if hd.isRemovable:
            devicepng = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/removable_dev.png'))
            device_info += hd.bus_description() + ' ' + _('Storage device')
        else:
            device_info += hd.bus_description() + ' ' + _('Hard disk')
        if uuid is not None:
            cfg_uuid = config.storage.get(uuid, None)
            if cfg_uuid is not None:
                if cfg_uuid['mountpoint'].value != '':
                    currentMountpoint = cfg_uuid['mountpoint'].value
                if cfg_uuid['enabled'].value:
                    isConfiguredStorageDevice = True
                    p = harddiskmanager.getPartitionbyMountpoint(currentMountpoint)
                    if p is not None:
                        if p.mounted():
                            isMountedPartition = True
            if isMountedPartition:
                isReadable = True
                devicepng = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/internal_hdd_mounted.png'))
                if hd.isRemovable:
                    devicepng = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/DEInfo/removable_dev_mounted.png'))
                device_info += ' - ' + currentMountpoint
            else:
                device_info += ' - not mounted'
            if currentMountpoint:
                for line in self.dfmounts:
                    line = line.replace('part1', ' ')
                    x = line.strip().split()
                    if x[len(x) - 1].find(currentMountpoint.strip()) >= 0 and len(x) > 1:
                        tot = int(x[0])
                        used = int(x[1])
                        free = int(x[2])
                        usedprc = x[3]
                        devicedata = 'Capacity: %s  Used: %s  Free: %s ' % (getUnit(tot), x[len(x) - 2], getUnit(free))
                        if usedprc:
                            hdd_description += ' in use: %s' % usedprc

        return (hdd_description,
         hd,
         device_info,
         numpart,
         isOfflineStorageDevice,
         isMountedPartition,
         currentMountpoint,
         devicepng,
         onlinepng,
         divpng,
         partitionNum,
         isReadable,
         devicedata,
         tot,
         used,
         free,
         usedprc)

    def updateList(self):
        self['introduction'].setText(_('Device list summary report'))
        total = 0
        i = 0
        self.view = self.VIEW_HARDDISK
        self.selectedHDD = None
        self.list = []
        self.list.append(self.memoryRamScan())
        self.list.append(self.memorySwapScan())
        self.list.append(self.flashscan())
        for hd in harddiskmanager.hdd:
            if not hd.isRemovable:
                self.list.append(self.buildHDDList(hd, isOfflineStorage=False))

        for hd in harddiskmanager.hdd:
            if hd.isRemovable:
                self.list.append(self.buildHDDList(hd, isOfflineStorage=False))

        if not self.list:
            self.list.append((_('no storage devices found'),
             0,
             None,
             None,
             None,
             None,
             None,
             None,
             None,
             None,
             False,
             0,
             0,
             0,
             0))
            self['introduction'].setText(_('No installed or configured storage devices found!'))
        else:
            for lines in self.list:
                if i > 1:
                    total = total + lines[15]
                i += 1

            self['introduction'].setText(_('Total space available: %s' % getUnit(total)))
        self['hddlist'].setList(self.list)
        self['hddlist'].setIndex(self.currentIndex)
        self.currentlyUpdating = False
        return

    def setButtons(self):
        self['key_red'].setText(_('Exit'))
        self['key_green'].setText(_('System paths'))
        self['key_yellow'].setText(_('Storage Device'))
        self['key_blue'].setText(_('Reload'))
        self['RedColorActions'].setEnabled(True)
        self['GreenColorActions'].setEnabled(True)
        self['YellowColorActions'].setEnabled(True)
        self['BlueColorActions'].setEnabled(True)

    def keyCancel(self):
        self.close()

    def keyRed(self):
        self.close()

    def keyGreen(self):
        self.session.openWithCallback(self.updateList, RecordPathsSettings)

    def keyYellow(self):
        self.session.openWithCallback(self.updateList, HarddiskDriveSelection)

    def keyBlue(self):
        self.updateList()


class ListPacket(Screen):
    skin = '\n\t\t<screen name="ListPacket" position="center,center" size="750,560" title="Upgradable packet">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="160,0" size="140,40" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="320,0" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_green" position="160,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget name="key_yellow" position="320,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t<widget source="status" render="Label" position="10,490" size="730,40" font="Regular;20" halign="center" valign="bottom" />\n\t\t<eLabel text="http://www.dream-elite.net" position="10,520" size="730,28" font="Regular;24" halign="center" />\n\t\t<widget source="menu" render="Listbox" position="20,45" size="710,400" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\tMultiContentEntryText(pos = (50, 3), size = (590, 23), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 0),\n\t\t\t\t\tMultiContentEntryText(pos = (50, 33), size = (590, 20), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 24), gFont("Regular", 16)],\n\t\t\t\t\t"itemHeight": 60\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t</screen> '

    def __init__(self, session):
        Screen.__init__(self, session)
        self['menu'] = List(list())
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Refresh'))
        self['key_yellow'] = Button(_('Update'))
        self['status'] = StaticText(_(''))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.close,
         'cancel': self.close,
         'green': self.update,
         'yellow': self.openUpdate}, -2)
        self.upgradable = []
        self.onLayoutFinish.append(self.get_list)

    def get_list(self):
        self.text = ''
        del self.upgradable[:]
        readlist = popen('opkg list-upgradable', 'r').readlines()
        for x in readlist:
            self.upgradable.append(x.split('\n'))

        if len(self.upgradable) > 0:
            self.text = _('There are at least ') + str(len(self.upgradable)) + _(' updates available.')
        else:
            self.text = _('There are no updates available.')
        self['status'].setText(self.text)
        self.drawList()

    def update(self):
        cmd = 'opkg update'
        self.session.openWithCallback(self.get_list, Console, title=_('Update'), cmdlist=[cmd], closeOnSuccess=True)

    def openUpdate(self):
        if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftwareManager/plugin.py')):
            from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
            self.session.openWithCallback(self.PluginDownloadBrowserClosed, UpdatePlugin)
        else:
            self.session.open(MessageBox, _('The Softwaremanagement extension is not installed!\nPlease install it.'), type=MessageBox.TYPE_INFO, timeout=10)

    def PluginDownloadBrowserClosed(self):
        pass

    def drawList(self):
        llist = []
        print 'SelfUpgradable:', self.upgradable
        if self.upgradable:
            for entry in self.upgradable:
                print 'Entry:', entry
                tmp = entry[0].split(' - ')
                tmp1 = [tmp[0], tmp[1] + ' ==> ' + tmp[2]]
                llist.append(tmp1)

        self['menu'].setList(llist)
