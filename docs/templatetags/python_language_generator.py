# Developed by Mark Barrett
# https://markbarrettdesign.com
# https://github.com/mark-barrett
from django import template

from core.models import ResourceParameter, ResourceHeader, ResourceDataBind

register = template.Library()

@register.simple_tag()
def python_authentication_example(request):
    return "<pre><code class='python'>import requests<br/><br/>response = requests.get('https://"+request.META['HTTP_HOST']+"/api'," \
            "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; auth=('rb_nrm_key_examplekey', ''))</code></pre>"

@register.simple_tag()
def python_resource_request_example(request):
    return "<pre><code class='python'>import requests<br/><br/>headers = {'Resource': 'Resource'}<br/><br/>response = "\
            "requests.get('https://"+request.META['HTTP_HOST']+"/api',<br/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"\
            "&nbsp;&nbsp;&nbsp; auth=('rb_nrm_key_examplekey', ''), <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; headers=headers)</code></pre>"


@register.simple_tag()
def python_generate_resource(request, resource):
    url = 'https://' + request.META["HTTP_HOST"] + '/api'

    if resource.request_type == 'GET':
        # Get the get parameters
        resource_parameters = ResourceParameter.objects.all().filter(resource=resource)

        if resource_parameters:
            # Append the question mark
            url += '?'

            # Loop through all resource parameters
            for index, parameter in enumerate(resource_parameters):
                # If the index is greater than 0, i.e more than one parameter
                if index > 0:
                    url += '&'

                url += parameter.key + '=your_value'

    html_to_return = '<pre><code class="python">import requests<br/><br/>'

    # Get the headers
    resource_headers = ResourceHeader.objects.all().filter(resource=resource)

    # Check if there are headers
    if resource_headers:

        # Add the Resource header
        html_to_return += 'headers = {<br/>&nbsp;&nbsp;\'Resource\': \'' + resource.name + '\','

        for index, header in enumerate(resource_headers):
            html_to_return += '<br/>&nbsp;&nbsp;\''+header.key+'\': your_value'

            # Check for the last value. If we aren't there then add a comma
            if index < len(resource_headers)-1:
                html_to_return += ','

        # Add the last bracket
        html_to_return += '<br/>}'
    else:
        html_to_return += 'headers = {\'Resource\': \'' + resource.name + '\'}'

    if resource.request_type == 'GET':
        type = 'get'
    elif resource.request_type == 'POST':
        type = 'post'

        # While we are here we can add the required parameters for posting
        data_binds = ResourceDataBind.objects.all().filter(resource=resource)

        if data_binds:
            html_to_return += '<br/>data = {<br/>'
            for index, data_bind in enumerate(data_binds):

                html_to_return += '&nbsp;&nbsp;\''+data_bind.key+'\': \'your_value\''

                # Check for the last value. If we aren't there then add a comma
                if index < len(data_binds) - 1:
                    html_to_return += ','

                html_to_return += '<br/>'

            html_to_return += '}'
    else:
        type = 'err'

    # Now do the request part
    html_to_return += "<br/><br/>response = requests."+type+"('"+url+"',<br/> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
                        "&nbsp;&nbsp;&nbsp; auth=('rb_nrm_key_examplekey', ''), <br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

    html_to_return += ' headers=headers'

    if resource.request_type == 'POST':
        html_to_return += ', data=data)'
    else:
        html_to_return += ')'

    html_to_return += '</code></pre>'

    return html_to_return
