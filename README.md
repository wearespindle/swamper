# Janitor

Janitor is here for you to simplify cleaning input data and building python
objects from this data.

## Status

Currently actively used and watched.

## Usage

### Requirements

 * python 2.7
 * python 3.4

### Installation

Currently installing from github is the only way. Will be on PyPI in
the near future.

### Running

`models.py`
```python

# Pretend this is some model.
class Company(object):
    # name = fields.Str(ascii_only=True)
    # github_address = fields.Str()

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
```

`validate.py`
```python
import unicodedata

from janitor.base import BaseJanitor


class CompanyJanitor(BaseJanitor):
    fields = [
        'name',
        'github_address',
    ]

    def __init__(self, data):
        super(CompanyJanitor, self).__init__(self.fields, data)

    def clean_name(self, name, is_blank):
        if is_blank or len(name.strip()) == 0:
            raise ValueError('Field "name" is required.')

        # Keep only ascii characters.
        return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

    def clean_github_address(self, address, is_blank):
        if is_blank or len(address.strip()) == 0:
            raise ValueError('Field "github_address" cannot be empty.')

        return 'https://github.com/%s' % address
```

`app.py`
```python

from .models import Company
from .validate import CompanyJanitor


data = {
    'name': u'Devhouse Spindl\xe9',
    'github_address': 'wearespindle',
}
janitor = CompanyJanitor(data)
assert janitor.is_clean()
company = janitor.build_or_update(Company, ['name', 'github_address'])

assert company.name == 'Devhouse Spindle'
assert company.github_address == 'https://github.com/wearespindle'
```

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) file on how to contribute to this project.

## Contributors

See the [CONTRIBUTORS.md](CONTRIBUTORS.md) file for a list of contributors to the project.

## Roadmap

### Changelog

The changelog can be found in the [CHANGELOG.md](CHANGELOG.md) file.

### In progress

 * Publish on pypi

### Future

 * Nothing planned at the moment

## Get in touch with a developer

If you want to report an issue see the [CONTRIBUTING.md](CONTRIBUTING.md) file for more info.

We will be happy to answer your other questions at opensource@wearespindle.com
