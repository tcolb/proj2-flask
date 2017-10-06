"""
Very simple Flask web site, with one page
displaying a course schedule.  We pre-process the
input file to set correct dates and highlight the
current week (if the academic term is in session).

"""



import flask
import logging
import arrow      # Replacement for datetime, based on moment.js

# Our own modules
import pre        # Preprocess schedule file
import config     # Configure from configuration files or command line


###
# Globals
###
app = flask.Flask(__name__)
if __name__ == "__main__":
    configuration = config.configuration()
else:
    # If we aren't main, the command line doesn't belong to us
    configuration = config.configuration(proxied=True)

# Pre-processed schedule is global, so be careful to update
# it atomically in the view functions.
#
schedule = pre.process(open(configuration.SYLLABUS))


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
  """Main application page; most users see only this"""
  app.logger.debug("Main page entry")
  flask.g.schedule = schedule  # To be accessible in Jinja2 on page
  return flask.render_template('syllabus.html')

@app.route("/refresh")
def refresh():
    """Admin user (or debugger) can use this to reload the schedule."""
    app.logger.debug("Refreshing schedule")
    global schedule
    schedule = pre.process(open(configuration.SYLLABUS))
    return flask.redirect(flask.url_for("index"))

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404

#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try:
        normal = arrow.get( date )
        return normal.format("ddd MM/DD/YYYY")
    except:
        return "(bad date)"


#############
#
# Set up to run from cgi-bin script, from
# gunicorn, or stand-alone.
#
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.run(port=configuration.PORT, host="127.0.0.1")
