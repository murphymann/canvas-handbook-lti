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
    Loads keys from environment variables in production,
    falls back to files in development.
    """
    import os
    from pylti1p3.registration import Registration
    
    config_path = get_lti_config_path()
    
    # Check if we have keys in environment variables (production)
    private_key_env = os.environ.get('LTI_PRIVATE_KEY')
    public_key_env = os.environ.get('LTI_PUBLIC_KEY')
    
    if private_key_env and public_key_env:
        # Production: use environment variables
        # Load config and manually set keys
        tool_conf = ToolConfJsonFile(config_path)
        # Override the file paths with actual key content
        tool_conf._private_key = private_key_env
        tool_conf._public_key = public_key_env
        return tool_conf
    else:
        # Development: use key files
        return ToolConfJsonFile(config_path)


def get_launch_url(request):
    """
    Get the launch URL for this tool.
    """
    return 'https://web-production-7b97e.up.railway.app/handbook/launch/'