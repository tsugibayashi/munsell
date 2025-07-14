# munsell
Munsell is used to adjust the backlight brightness using xbacklight, light, or brightnessctl based on the Munsell color system.

## How to build
Builds this software as follows:
```
$ python -m build
```

## How to install
Installs this software as follows:
```
$ pip install dist/*.whl
```

## Creating a configuration file
Creates a configuration file.
```
$ munsell
```
Edits the "method" in the configuration file to match the command you use:
```
$ vi ~/.config/munsell/config.toml
-----
method = "light"   #xbacklight, light, or brightnessctl
-----
```

## How to execute
(1) Specifies the brightness as <Number>:
```
$ munsell s <Number>
```
(2) Increases the brightess:
```
$ munsell p
```
(3) Decreases the brightness:
```
$ munsell m
```

