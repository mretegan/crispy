# Register the resources directory. Is better to do it here rather than in the
# __main__.py file.
from silx.resources import register_resource_directory
register_resource_directory(name='icons', package_name='crispy.gui.icons')
register_resource_directory(name='uis', package_name='crispy.gui.uis')
register_resource_directory(name='quanty', package_name='crispy.modules.quanty')
