"""Cryptocurrency_ePiframe: cryptocurrency price on the photo (ePiframe Plugin API v2).

The price (and its 24 h change) comes from the free CoinGecko API and is drawn in
a corner of the converted photo (``postprocess_photo``). Without the price (no
network, API limit) the photo is shown without it.
"""

from dataclasses import dataclass
from typing import Any

import requests
from PIL import Image, ImageColor, ImageDraw, ImageFont

from epiframe.config.property import ConfigProperty, PropertyType
from epiframe.plugins.base import PhotoFile
from epiframe.plugins.base import Plugin as PluginBase
from epiframe.weather.stamp import TEXT_FONT  # the font ePiframe uses for its stamps

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
TIMEOUT = 5  # seconds
MARGIN = 10  # pixels from the photo edge
STROKE_WIDTH = 2
POSITIONS = [0, 1, 2, 3]  # left-top, right-top, left-bottom, right-bottom
COLORS = ["white", "black"]  # the outline has the other one


@dataclass(frozen=True)
class Price:
    symbol: str
    price: float
    change: float | None  # percent in 24 h (CoinGecko may not know it)


def fetch_price(coin: str, currency: str) -> Price:
    """Current price of ``coin`` in ``currency``; raises on any problem."""
    response = requests.get(
        API_URL,
        params={"ids": coin.lower(), "vs_currency": currency.lower()},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    data: Any = response.json()
    if not data:
        raise ValueError(f"unknown cryptocurrency {coin!r} or currency {currency!r}")
    market = data[0]
    change = market.get("price_change_percentage_24h")
    return Price(
        str(market["symbol"]),
        float(market["current_price"]),
        None if change is None else float(change),
    )


def price_text(price: Price, show_change: bool) -> str:
    """E.g. ``BTC:43210.50 (+1.25%)``."""
    text = f"{price.symbol.upper()}:{price.price:.2f}"
    if show_change and price.change is not None:
        sign = "+" if price.change > 0 else ""  # negative values have their "-"
        text += f" ({sign}{price.change:.2f}%)"
    return text


class Plugin(PluginBase):
    name = "Cryptocurrency"
    author = "MikeGawi"
    description = "Displays cryptocurrency price and percentage change on frame"
    site = "https://github.com/MikeGawi/cryptocurrency_ePiframe"
    info = "Uses free API from https://www.coingecko.com/"

    def settings(self) -> list[ConfigProperty]:
        # all entries are used only when the plugin is enabled
        return [
            *super().settings(),  # is_enabled
            ConfigProperty("cryptocurrency", dependency="is_enabled"),
            ConfigProperty("target_currency", dependency="is_enabled"),
            ConfigProperty(
                "show_percentage", PropertyType.BOOLEAN, dependency="is_enabled"
            ),
            ConfigProperty(
                "position",
                PropertyType.INTEGER,
                possible=POSITIONS,
                dependency="is_enabled",
            ),
            ConfigProperty(
                "font", PropertyType.INTEGER, min_value=8, dependency="is_enabled"
            ),
            ConfigProperty("font_color", possible=COLORS, dependency="is_enabled"),
        ]

    def postprocess_photo(self, photo: PhotoFile) -> None:
        try:
            price = fetch_price(
                self.config.get("cryptocurrency"), self.config.get("target_currency")
            )
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            # the photo is still shown, just without the price
            self.logger.warning(f"No cryptocurrency price: {error}")
            return
        text = price_text(price, bool(self.config.getint("show_percentage")))
        with Image.open(photo.path) as source:
            image = source.copy()
        image = self.upright(image, photo, back=False)
        self.draw(image, text)
        self.upright(image, photo, back=True).save(photo.path)

    @staticmethod
    def upright(image: Image.Image, photo: PhotoFile, back: bool) -> Image.Image:
        # a vertical frame stores the photo turned: draw on the upright photo
        if photo.horizontal:
            return image
        turn_left = (photo.rotation == 90) != back
        return image.transpose(
            Image.Transpose.ROTATE_90 if turn_left else Image.Transpose.ROTATE_270
        )

    def draw(self, image: Image.Image, text: str) -> None:
        size = self.config.getint("font")
        position = self.config.getint("position")
        color = self.config.get("font_color")
        outline = COLORS[1 - COLORS.index(color)]
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(TEXT_FONT), size)
        width = draw.textlength(text, font=font)
        x = image.width - width - MARGIN if position in (1, 3) else MARGIN
        y = image.height - MARGIN - size if position in (2, 3) else MARGIN
        draw.text(
            (x, y),
            text,
            font=font,
            # colors in the photo's mode (a black & white photo has no RGB)
            fill=ImageColor.getcolor(color, image.mode),
            stroke_width=STROKE_WIDTH,
            stroke_fill=ImageColor.getcolor(outline, image.mode),
        )
