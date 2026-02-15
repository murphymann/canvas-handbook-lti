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
    creates temp files if needed.
    """
    import os
    import tempfile
    
    config_path = get_lti_config_path()
    
    # Check if we have keys in environment variables (production)
    private_key_env = os.environ.get('LTI_PRIVATE_KEY')
    public_key_env = os.environ.get('LTI_PUBLIC_KEY')
    
    if private_key_env and public_key_env:
        # Production: create temporary key files from environment variables
        # Create temp directory if it doesn't exist
        temp_dir = '/tmp/lti_keys'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Write keys to temp files
        private_key_path = os.path.join(temp_dir, 'private.key')
        public_key_path = os.path.join(temp_dir, 'public.key')
        
        with open(private_key_path, 'w') as f:
            f.write(private_key_env)
        
        with open(public_key_path, 'w') as f:
            f.write(public_key_env)
        
        # Now load config normally - it will find the temp files
        return ToolConfJsonFile(config_path)
    else:
        # Development: use key files from repo
        return ToolConfJsonFile(config_path)


def get_launch_url(request):
    """
    Get the launch URL for this tool.
    """
    return 'https://web-production-7b97e.up.railway.app/handbook/launch/'