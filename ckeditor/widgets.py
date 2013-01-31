import json

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.functional import Promise


from django.core.exceptions import ImproperlyConfigured
from django.forms.util import flatatt


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)

json_encode = LazyEncoder().encode

DEFAULT_CONFIG = {
    'skin': 'v2',
    'toolbar': 'Full',
    'height': 291,
    'width': 618,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 747,
    'filebrowserBrowsePatternName': 'ckeditor_browse',
	'filebrowserUploadPatternName': 'ckeditor_upload',
	'filebrowserBrowseParams' : '',
	'filebrowserUploadParams' : ''
}

reverse_lazy = lazy(reverse, str)

class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.
    """
    class Media:
       js = (
                reverse_lazy("ckeditor_static", args=("ckeditor.js?v=4",)),
        )
       
    def __init__(self, config_name='default', *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG

        # Try to get valid config from settings.
        configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
        if configs != None:
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if configs.has_key(config_name):
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                                setting must be a dictionary type.' % \
                                config_name)
                    # Override defaults with settings config.
                    self.config.update(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' \
                            found in your CKEDITOR_CONFIGS setting." % \
                            config_name)
            else:
                raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                        dictionary type.')

    def render(self, name, value, attrs={}):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        
        self.config.setdefault('filebrowserUploadUrl', reverse(self.config['filebrowserUploadPatternName']) + self.config['filebrowserUploadParams'])
        
        self.config.setdefault('filebrowserBrowseUrl', reverse(self.config['filebrowserBrowsePatternName']) + self.config['filebrowserBrowseParams'])
        
        return mark_safe(render_to_string('ckeditor/widget.html', {
            'final_attrs': flatatt(final_attrs),
            'value': conditional_escape(force_unicode(value)),
            'id': final_attrs['id'],
            'config': json_encode(self.config)
            })
        )
