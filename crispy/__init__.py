# Register the resources directory. Is better to do it here rather than in the
# __main__.py file.
from silx.resources import register_resource_directory
register_resource_directory(name='crispy', package_name='crispy.resources')
