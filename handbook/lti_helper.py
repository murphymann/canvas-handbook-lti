import json
import os
from django.conf import settings
from pylti1p3.contrib.django import DjangoOIDCLogin, DjangoMessageLaunch
from pylti1p3.tool_config import ToolConfJsonFile


def get_lti_config_path():
    """
    Get the path to the LTI configuration file.
    """
    return os.path.join(
        settings.BASE_DIR,
        'handbook',
        'lti_configs',
        'canvas_config.json'
    )


def get_launch_data_storage():
    """
    Get the session storage for LTI launch data.
    Uses Django's cache framework.
    """
    from pylti1p3.contrib.django import DjangoCacheDataStorage
    
    return DjangoCacheDataStorage(cache_name='default')


def get_tool_conf():
    """
    Get the LTI tool configuration.
    """
    config_path = get_lti_config_path()
    return ToolConfJsonFile(config_path)


def get_launch_url(request):
    """
    Get the launch URL for this tool.
    """
    return 'https://web-production-7b97e.up.railway.app/handbook/launch/'