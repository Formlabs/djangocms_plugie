# Django CMS Plugin Importer/Exporter - Plugie

[![PyPI version](https://badge.fury.io/py/djangocms-plugie.svg)](https://badge.fury.io/py/djangocms-plugie)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![wheel](https://img.shields.io/pypi/wheel/djangocms-plugie)](https://pypi.org/project/djangocms-plugie/)

This project extends the functionality of the Django CMS framework by providing a way to import and export plugins from one page to another, across different projects, or even between different Django CMS installations. This is useful when your page exists in a development environment and you want to move it to a production environment, or when you have multiple CMS that uses the same content.

## Contributing

If you would like to contribute to this project, please read our [CONTRIBUTING](https://github.com/Formlabs/djangocms_plugie/blob/main/CONTRIBUTING.md) file for guidelines.


## Features 

- Export / import plugins into / from a JSON file
- Add custom serializers / deserializers to export /import custom types used in your plugins

## Requirements

See the Python/Django/Django CMS for the current release version in the [setup](https://github.com/Formlabs/djangocms_plugie/blob/main/setup.py) file or in our [documentation](https://github.com/Formlabs/djangocms_plugie/wiki).

## Installation

1. Install the package using [pip](https://pypi.org/project/djangocms_plugie/):

```bash
pip install djangocms_plugie
```

2. Add `djangocms_plugie` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'djangocms_plugie',
    ...
]
```

3. Add the following to your `urls.py`:

```python
urlpatterns = [
    ...
    path('admin/', include('djangocms_plugie.urls')),
    ...
]
```

4. Setup 'plugie' from your terminal with the following command:

```bash
plugie <project_dir>
```

This will create a 'plugie_config.json' file and a 'plugie/custom_methods' folder in your project directory, including some default methods. 
- The 'plugie_config.py' file is where you can customize some functionalities of the app. 
- The 'custom_methods' folder is where you can add custom methods that can be used in your custom serializers and deserializers. You also get a 'default.py' file with some default methods that you can use as a reference or that you might want to override.

You can find more information about this in the [documentation](https://github.com/Formlabs/djangocms_plugie/wiki).


## Using Plugie

### Exporting Plugins

![How to Export Plugins](https://github.com/Formlabs/djangocms_plugie/blob/main/media/plugie_export.gif?raw=true)

1. Go to the Django CMS admin and select the page where you want to export the plugins.

2. Open the structure sidebar and click the hamburger icon on the right side of the placeholder or plugin tree that you want to export.

3. Click the 'Export plugins' option.

4. Check the downloaded JSON file to see the exported plugins.

### Importing Plugins

![How to Import Plugins](https://github.com/Formlabs/djangocms_plugie/blob/main/media/plugie_import.gif?raw=true)

1. Go to the page where you want to import the plugins.

2. Open the structure sidebar and click the hamburger icon on the right side of the placeholder or plugin tree where you want to import the plugins.

3. Click the 'Import plugins' option.

4. A modal will open where you can select the JSON file previously exported.

5. Click the 'Import' button.

6. The plugins will be imported to the selected placeholder or plugin tree.

## Documentation

The documentation is available [here](https://github.com/Formlabs/djangocms_plugie/wiki).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Formlabs/djangocms_plugie/blob/main/LICENSE.md) file for details.


## Brought to you by
[![Formlabs logo](https://github.com/Formlabs/djangocms_plugie/blob/main/media/logo.png?raw=true)](http://formlabs.com/)