<img align="right" src="https://github.com/MikeGawi/cryptocurrency_ePiframe/blob/master/assets/curr.gif" width="400">

# Cryptocurrency_ePiframe

Plugin that displays cryptocurrency price and percentage change on [ePiframe](https://github.com/MikeGawi/ePiframe)

This plugin has been created with [ePiframe_plugin](https://github.com/MikeGawi/ePiframe_plugin) template.

It uses free [CoinGecko Crypto API](https://www.coingecko.com/en/api).


## Requirements

* [ePiframe](https://github.com/MikeGawi/ePiframe) 2.0 or newer (Plugin API v2). For ePiframe 1.x use the version
  of this plugin from before ePiframe 2.0.

## How it works

* The price comes from the free CoinGecko API on every photo change (mind its rate limits with short intervals).
* Without network or price data the photo is shown without the price (a warning is logged).
* The text uses the font of ePiframe's weather stamp; position, size and color are configurable.

## Installation

On working ePiframe:

* Clone to ePiframe plugins path:
	```
	cd <ePiframe path>/plugins
	git clone https://github.com/MikeGawi/cryptocurrency_ePiframe cryptocurrency_ePiframe
	```

OR

* Download and extract:
	```
	cd <ePiframe path>/plugins
	wget -q https://github.com/MikeGawi/cryptocurrency_ePiframe/archive/master.zip -O cryptocurrency_ePiframe.zip
	unzip cryptocurrency_ePiframe.zip
	mv cryptocurrency_ePiframe-master cryptocurrency_ePiframe
	rm cryptocurrency_ePiframe.zip
	```

## Configuration

* Configure with the file [*config.cfg*](https://github.com/MikeGawi/cryptocurrency_ePiframe/blob/master/config.cfg) inside *ePiframe_path/plugins/cryptocurrency_ePiframe*

OR

* In ePiframe WebUI (if enabled) under *Plugins - Cryptocurrency*

Check the configuration with `./ePiframe.py --check-config` (in the ePiframe folder).

The plugin folder name must stay a valid Python name (letters, digits, `_`), e.g. `cryptocurrency_ePiframe`: ePiframe
skips plugins in folders with dashes or dots.
