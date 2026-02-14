from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from pylti1p3.contrib.django import DjangoOIDCLogin, DjangoMessageLaunch

from .utils import load_handbook_json, parse_handbook_data
from .lti_helper import get_tool_conf, get_launch_data_storage, get_launch_url


def test_view(request):
    """
    A simple view to test Django is working.
    
    Args:
        request: Django's HttpRequest object containing info about the web request
        
    Returns:
        HttpResponse: HTML content to display in the browser
    """
    return HttpResponse("<h1>Hello from Django!</h1><p>Your handbook app is working.</p>")


@csrf_exempt
@require_POST
def lti_login(request):
    """
    Handle LTI 1.3 OIDC login.
    This is the first step when Canvas launches your tool.
    """
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    
    oidc_login = DjangoOIDCLogin(
        request,
        tool_conf,
        launch_data_storage=launch_data_storage
    )
    
    target_link_uri = get_launch_url(request)
    
    return oidc_login.redirect(target_link_uri)


@csrf_exempt
@require_POST
def lti_launch(request):
    """
    Handle LTI 1.3 launch from Canvas.
    Extract course code and display handbook.
    """
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    
    message_launch = DjangoMessageLaunch(
        request,
        tool_conf,
        launch_data_storage=launch_data_storage
    )
    
    # Validate the launch request
    message_launch_data = message_launch.get_launch_data()
    
    # Extract user and course information from Canvas
    user_name = message_launch_data.get('name', 'Student')
    
    # Canvas sends course code in 'context_label' 
    # e.g., "EDET100" or "NRSG264"
    course_code = message_launch_data.get('https://purl.imsglobal.org/spec/lti/claim/context', {}).get('label', 'UNKNOWN')
    
    # Load the JSON data
    json_data = load_handbook_json(course_code)
    
    # Parse it into a usable format
    handbook_data = parse_handbook_data(json_data)
    
    # Prepare context for template
    context = {
        'user_name': user_name,
        'course_code': course_code,
        'handbook': handbook_data,
    }
    
    return render(request, 'handbook/launch.html', context)