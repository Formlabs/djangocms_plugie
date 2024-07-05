# Django CMS Plugin Importer/Exporter

This project extends the functionality of the Django CMS framework by providing a way to import and export plugins from one page to another, across different projects, or even between different Django CMS installations. This is useful when your page exists in a development environment and you want to move it to a production environment, or when you have multiple verticals that share the same content but use different databases.

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
    url(r'^admin/', include('djangocms_plugie.urls')),
    ...
]
```

DONE! You can now import and export plugins from the Django CMS plugin editor.


## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Formlabs/djangocms_plugie/blob/main/LICENSE.md) file for details.


## Brought to you by
[![Formlabs logo](https://github.com/Formlabs/hackathon-slicer/blob/master/logo.png)](http://formlabs.com/)