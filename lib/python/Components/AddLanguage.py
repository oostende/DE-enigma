from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import fileExists
from os import system
import os, sys
from DE.DownloadProgress import DownloadProgress
from enigma import  eConsoleAppContainer
###########################################################################
installed_lang=[]
trans_patch=[]
lang_to_inst=""
label_list=""
lang_to_inst_desc=""
Translation = [
				["en","English","EN"],
				["de","German","DE"],
				["ar","Arabic","AE"],
				["br","Brasilian","BR"],
				["ca","Catalan","AD"],
				["hr","Croatian","HR"],
				["cs","Czech","CZ"],
				["da","Danish","DK"],
				["nl","Dutch","NL"],
				["et","Estonian","EE"],
				["fi","Finnish","FI"],
				["fr","French","FR"],
				["el","Greek","GR"],
				["hu","Hungarian","HU"],
				["lt","Lithuanian","LT"],
				["lv","Latvian","LV"],
				["is","IceLanding","IS"],
				["it","Italian","IT"],
				["no","Norwegian","NO"],
				["pl","Polish","PL"],
				["pt","Portoguese","PT"],
				["ru","Russian","RU"],
				["sr","Serbian","YU"],
				["sk","Slovakian","SK"],
				["es","Spanish","ES"],
				["sv","Swedish","SE"],
				["tr","Turkish","TR"],
				["uk","Ukrainian","UA"],
				["fy","Frisian","x-FY"],
				]
###########################################################################
class MyMenu(Screen):
	skin = """
		<screen position="center,center" size="460,480" title="DE Language Manager" >
			<widget name="myMenu" position="10,70" size="420,400" scrollbarMode="showOnDemand" />
			<widget name="info_label" position="10,5" zPosition="2" size="440,50" valign="center" halign="left" font="Regular;22" transparent="1" backgroundColor="#ffffffff" shadowColor="#1A58A6" shadowOffset="-2,-1" />
		</screen>"""

	def __init__(self, session, args = 0):
		self.session = session
		global label_list
		list = []
		self.find_lang()
		label_list=""
		#self.get_language()
		for line in Translation:
			print "Line:",line
			if not line in installed_lang:
				addlng= ('(_("' + line[1] + '"), "' + line[0] + '")')
				list.append((_(line[1]), line[0], line[2]))
			else:	
				label_list=(label_list +(_(line[1])) + ",")

		Screen.__init__(self, session)
		self["myMenu"] = MenuList(list)	
		self["info_label"] = Label((_("Installed language: "))+ label_list[0:(len(label_list)-1)])
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		#self["myActionMap"] = ActionMap(["SetupActions"],
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.go,
			#"blue": self.cancel,
			"cancel": self.cancel
		}, -1)
		#self["key_blue"] = Button(_("Install"))
		#self["key_blue"].hide()
		
	def go(self):
		global lang_to_inst
		global lang_to_inst_desc
		lang_to_inst = (self["myMenu"].l.getCurrentSelection()[1] + "_" + self["myMenu"].l.getCurrentSelection()[2])
		lang_to_inst_desc= self["myMenu"].l.getCurrentSelection()[0]
		print "\n[MyMenu] returnValue: " + lang_to_inst + "\n"
		
		for line1 in Translation:
				if self["myMenu"].l.getCurrentSelection()[1]==line1[0]:
					installed_lang.append([line1[0],line1[1],line1[2]])
		print "Installed lang after selection: ",installed_lang
		if lang_to_inst is not None:
			print "Download language"
			self.downloadAddons()
			
	def myMsg(self, entry):
			self.session.open(MessageBox, entry , MessageBox.TYPE_INFO)
			
	def cancel(self):
		print "\n[MyMenu] cancel\n"
		self.close(None)

	def restart(self):
			msg = 'Enigma2 will be now restarted to complete language installation.\nDo You want restart enigma2 now?'
			box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg , MessageBox.TYPE_YESNO)
			box.setTitle('Restart enigma')
	def restartEnigma2(self, answer):
		if (answer is True):
			system('killall -9 enigma2')
			
	def find_lang(self):
		global installed_lang
		installed_lang=[]
		list_dir=os.listdir("/usr/share/enigma2/po")
		print "Lista directory:",list_dir
		for line in list_dir:
			for line1 in Translation:
				if line==line1[0]:
					installed_lang.append([line1[0],line1[1],line1[2]])
		print "Installed_lang:", installed_lang

	def downloadAddons(self):
			filename=lang_to_inst + ".tbz2"
			url = "http://www.dream-elite.net/DreamElite/e2Language/" + filename
			#print "URL:",url
			self.session.openWithCallback(self.executedScript, DownloadProgress, url, "/tmp/", filename)
		
	def executedScript(self, *answer):
		print "Executed script: ",lang_to_inst_desc
		if fileExists('/tmp/' + lang_to_inst + ".tbz2"):
			msg = _('Do you want install :\n%s?') % lang_to_inst_desc
			box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
			box.setTitle(_('Install %s Language')% lang_to_inst_desc)
		
		else:
			msg = _('File: %s not found!\nPlease check your internet connection.') % lang_to_inst
			self.session.open(MessageBox, msg , MessageBox.TYPE_INFO)
		
	def installAddons(self, answer):
		if (answer is True):
			#self['conn'].text = _('Installing addons.\nPlease Wait...')
				self.container.execute("tar -jxvf /tmp/" + lang_to_inst + ".tbz2" + " -C /")
				print "System restart"
				self.restart()
				#system("tar -jxvf /tmp/" + lang_to_inst + ".tbz2" + " -C /")
				if fileExists('/tmp/' + lang_to_inst + ".tbz2"):
					system("rm -f /tmp/"  + lang_to_inst + ".tbz2")
		
		else:
			if fileExists('/tmp/' + lang_to_inst + ".tbz2"):
				system("rm -f /tmp/"  + lang_to_inst + ".tbz2")
	def runFinished(self, retval):
			global label_list
			global installed_lang
			print "Run finished"
			if fileExists('/tmp/' + lang_to_inst + ".tbz2"):
				system("rm -f /tmp/"  + lang_to_inst + ".tbz2")
				
			label_list=""
			installed_lang=[]
			self.find_lang()
			for line in Translation:
				print "Line:",line
				if  line in installed_lang:	
					label_list=(label_list +(_(line[1])) + ",")
			self["info_label"].setText((_("Installed language: "))+ label_list[0:(len(label_list)-1)])
		
###########################################################################

