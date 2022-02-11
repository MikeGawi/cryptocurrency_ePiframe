from modules.base.pluginbase import pluginbase
from modules.base.configbase import configbase
from misc.configprop import configprop
from misc.constants import constants
from misc.connection import connection
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os, requests

class plugin(pluginbase):
	
	name = 'Cryptocurrency'
	author = 'MikeGawi'
	description = 'Displays cryptocurrency price and percentage change on frame'
	site = 'https://github.com/MikeGawi/Cryptocurrency-ePiframe'
	info = 'Uses free API from https://www.coingecko.com/'
	
	__MARGIN = 10
	
	__POSITION_VALUES = [0, 1, 2, 3]
	
	__COLORS = {
		'WHITE' : 		255,
		'BLACK' : 		0
	}
		
	__ERROR_VALUE_TEXT = 'Configuration position should be one of {}'
	__ERROR_CVALUE_TEXT = 'Configuration font_color should be one of {}'
	
	__BASE_URL = "https://api.coingecko.com/api/v3/coins/markets?ids={}&vs_currency={}"
	
	class configmgr (configbase):
		#building settings according to config.default file
		#notice that referring to plugin class is done with self.main_class
		def load_settings(self):
			self.SETTINGS = [
				configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE),
				configprop('crtyptocurrency', self, dependency='is_enabled'),
				configprop('target_currency', self, dependency='is_enabled'),
				configprop('show_percentage', self, prop_type=configprop.BOOLEAN_TYPE, dependency='is_enabled'),
				configprop('position', self, dependency='is_enabled', prop_type=configprop.INTEGER_TYPE, possible=self.main_class.get_positions()),
				configprop('font', self, dependency='is_enabled', minvalue=8, prop_type=configprop.INTEGER_TYPE),
				configprop('font_color', self, dependency='is_enabled', possible=self.main_class.get_colors()),
			]
	
	def __init__ (self, path, pidmgr, logging, globalconfig):
		super().__init__(path, pidmgr, logging, globalconfig) #default constructor
	
	#config possible values methods
	def get_positions (self):
		return self.__POSITION_VALUES
			
	def get_colors (self):
		return [k.lower() for k in self.__COLORS.keys()]
	
	def __get_response_json (self, url:str, timeout:int):
		try:
			ret = requests.get(url, timeout=timeout)
			ret.raise_for_status()		
		except requests.ConnectionError as exc:
			ret = None
		
		return ret.json() if ret else None
		
	def __send_request (self, baseurl, timeout):
		url = baseurl.format(self.config.get('crtyptocurrency').lower(), self.config.get('target_currency').lower())
		self.__data = self.__get_response_json(url, timeout)
	
	#Overwriting only postprocess method
	def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr):
		self.__send_request(self.__BASE_URL, constants.CHECK_CONNECTION_TIMEOUT) #getting request from API with timeout
		if self.__data:
			try:
				name = self.__data[0]['symbol']	#parsing JSON data
				price = format(float(self.__data[0]['current_price']), '.2f')
				perc = format(float(self.__data[0]['price_change_percentage_24h']), '.2f')

				image = Image.open(finalphoto)
				if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_270) #rotating image if frame not in horizontal position
				draw = ImageDraw.Draw(image)
				font = ImageFont.truetype('static/fonts/NotoSans-SemiCondensed.ttf', self.config.getint('font')) #existing ePiframe font is loaded

				wid, hei = image.size

				text = "{}:{}{}".format(name.upper(), price, (' (' + ('+' if float(perc) > 0 else '') + perc + "%)") if bool(self.config.getint('show_percentage')) else '')
				size = draw.textlength(text, font = font) #calculating text width

				x = self.__MARGIN
				y = self.__MARGIN

				if self.config.getint('position') in [1, 3]:
					x = wid - size - self.__MARGIN

				if self.config.getint('position') in [2, 3]:
					y = hei - self.__MARGIN - self.config.getint('font')

				fillcolor = self.__COLORS[self.config.get('font_color').upper()] #getting fill and stroke colors...
				strokecolor = (self.__COLORS['WHITE'] + self.__COLORS['BLACK']) - fillcolor

				stroke = ImageColor.getcolor({value:key for key, value in self.__COLORS.items()}[strokecolor], image.mode) #...according to the timage mode (can be black & white)
				fill = ImageColor.getcolor(self.config.get('font_color'), image.mode)

				draw.text((x, y), text, font = font, fill = fill, stroke_width=2, stroke_fill=stroke) #drawing text

				if not is_horizontal: image = image.transpose(Image.ROTATE_270 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_90) #rotating back if in vertical position

				image.save(finalphoto) #saving as final photo
			except Exception:
				pass