activate_this = '/home/shampoo/Documents/fullstack_python6/full_stack_store/flask_log/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))
from my_app import app as application
import sys, logging
logging.basicConfig(stream = sys.stderr)