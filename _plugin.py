from modules.base.pluginbase import PluginBase
from modules.base.configbase import ConfigBase
from misc.configproperty import ConfigProperty
from misc.constants import Constants
from PIL import Image, ImageDraw, ImageFont, ImageColor
from misc.logs import Logs
from modules.convertmanager import ConvertManager
from modules.pidmanager import PIDManager
import requests


class Plugin(PluginBase):

    name = "Cryptocurrency"
    author = "MikeGawi"
    description = "Displays cryptocurrency price and percentage change on frame"
    site = "https://github.com/MikeGawi/Cryptocurrency_ePiframe"
    info = "Uses free API from https://www.coingecko.com/"

    __MARGIN = 10
    __POSITION_VALUES = [0, 1, 2, 3]
    __COLORS = {"WHITE": 255, "BLACK": 0}
    __BASE_URL = "https://api.coingecko.com/api/v3/coins/markets?ids={}&vs_currency={}"

    class PluginConfigManager(ConfigBase):
        # building settings according to config.default file
        # notice that referring to plugin class is done with self.main_class
        def load_settings(self):
            self.SETTINGS = [
                ConfigProperty(
                    "is_enabled", self, prop_type=ConfigProperty.BOOLEAN_TYPE
                ),
                ConfigProperty("cryptocurrency", self, dependency="is_enabled"),
                ConfigProperty("target_currency", self, dependency="is_enabled"),
                ConfigProperty(
                    "show_percentage",
                    self,
                    prop_type=ConfigProperty.BOOLEAN_TYPE,
                    dependency="is_enabled",
                ),
                ConfigProperty(
                    "position",
                    self,
                    dependency="is_enabled",
                    prop_type=ConfigProperty.INTEGER_TYPE,
                    possible=self.main_class.get_positions(),
                ),
                ConfigProperty(
                    "font",
                    self,
                    dependency="is_enabled",
                    minvalue=8,
                    prop_type=ConfigProperty.INTEGER_TYPE,
                ),
                ConfigProperty(
                    "font_color",
                    self,
                    dependency="is_enabled",
                    possible=self.main_class.get_colors(),
                ),
            ]

    def __init__(
        self,
        path: str,
        pid_manager: PIDManager,
        logging: Logs,
        global_config: ConfigBase,
    ):

        super().__init__(
            path, pid_manager, logging, global_config
        )  # default constructor

    # config possible values methods
    def get_positions(self):
        return self.__POSITION_VALUES

    def get_colors(self):
        return [key.lower() for key in self.__COLORS.keys()]

    @staticmethod
    def __get_response_json(url: str, timeout: int):
        try:
            return_value = requests.get(url, timeout=timeout)
            return_value.raise_for_status()
        except requests.ConnectionError:
            return_value = None

        return return_value.json() if return_value else None

    def __send_request(self, baseurl, timeout):
        url = baseurl.format(
            self.config.get("cryptocurrency").lower(),
            self.config.get("target_currency").lower(),
        )
        self.__data = self.__get_response_json(url, timeout)

    # Overwriting only postprocess method
    def postprocess_photo(
        self,
        final_photo: str,
        width: int,
        height: int,
        is_horizontal: bool,
        convert_manager: ConvertManager,
        photo,
        id_label: str,
        creation_label: str,
        source_label: str,
    ):
        self.__send_request(
            self.__BASE_URL, Constants.CHECK_CONNECTION_TIMEOUT
        )  # getting request from API with timeout
        if self.__data:
            name = self.__data[0]["symbol"]  # parsing JSON data
            price = format(float(self.__data[0]["current_price"]), ".2f")
            percentage = format(
                float(self.__data[0]["price_change_percentage_24h"]), ".2f"
            )

            image = Image.open(final_photo)
            if not is_horizontal:
                image = image.transpose(
                    Image.ROTATE_90
                    if self.global_config.getint("rotation") == 90
                    else Image.ROTATE_270
                )  # rotating image if frame not in horizontal position
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(
                "static/fonts/NotoSans-SemiCondensed.ttf", self.config.getint("font")
            )  # existing ePiframe font is loaded

            image_width, image_height = image.size

            text = "{}:{}{}".format(
                name.upper(),
                price,
                (" (" + ("+" if float(percentage) > 0 else "") + percentage + "%)")
                if bool(self.config.getint("show_percentage"))
                else "",
            )
            size = draw.textlength(text, font=font)  # calculating text width

            x = self.__MARGIN
            y = self.__MARGIN

            if self.config.getint("position") in [1, 3]:
                x = image_width - size - self.__MARGIN

            if self.config.getint("position") in [2, 3]:
                y = image_height - self.__MARGIN - self.config.getint("font")

            fill_color = self.__COLORS[
                self.config.get("font_color").upper()
            ]  # getting fill and stroke colors...
            stroke_color = (
                self.__COLORS["WHITE"] + self.__COLORS["BLACK"]
            ) - fill_color

            stroke = ImageColor.getcolor(
                {value: key for key, value in self.__COLORS.items()}[stroke_color],
                image.mode,
            )  # ...according to the image mode (can be black & white)
            fill = ImageColor.getcolor(self.config.get("font_color"), image.mode)

            draw.text(
                (x, y), text, font=font, fill=fill, stroke_width=2, stroke_fill=stroke
            )  # drawing text

            if not is_horizontal:
                image = image.transpose(
                    Image.ROTATE_270
                    if self.global_config.getint("rotation") == 90
                    else Image.ROTATE_90
                )  # rotating back if in vertical position

            image.save(final_photo)  # saving as final photo
