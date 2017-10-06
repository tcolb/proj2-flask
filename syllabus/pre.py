"""
Pre-process a syllabus (class schedule) file.
"""
import arrow
import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)


base = arrow.now()

def process(raw):
    """
    Line by line processing of syllabus file.  Each line that needs
    processing is preceded by 'head: ' for some string 'head'.  Lines
    may be continued if they don't contain ':'.  If # is the first
    non-blank character on a line, it is a comment ad skipped.
    """
    field = None
    entry = { }
    cooked = [ ]
    for line in raw:
        log.debug("Line: {}".format(line))
        line = line.strip()
        if len(line) == 0 or line[0]=="#" :
            log.debug("Skipping")
            continue
        parts = line.split(':')
        if len(parts) == 1 and field:
            entry[field] = entry[field] + line + " "
            continue
        if len(parts) == 2:
            field = parts[0]
            content = parts[1]
        else:
            raise ValueError("Trouble with line: '{}'\n".format(line) +
                "Split into |{}|".format("|".join(parts)))

        if field == "begin":
            try:
                base = arrow.get(content, "MM/DD/YYYY")
                print("Base date {}".format(base.isoformat()))
            except:
                raise ValueError("Unable to parse date {}".format(content))

        elif field == "week":
            if entry:
                cooked.append(entry)
                entry = { }
            entry['topic'] = ""
            entry['project'] = ""
            entry['week'] = content

            # Gets the starting date of the week
            week_date = base.shift(weeks=int(content) - 1)
            # Adds the key val pair 'date':arrow date to the dict
            entry['date'] = week_date.format('MM-DD-YYYY')

            # Checks if the current date is more than the date start and less than the next weeks date starting
            # if true, this adds a key val pair 'current' with a boolean, indicating if its the current week or not
            now = arrow.now()
            if now >= week_date and now < week_date.shift(weeks=1):
                entry['current'] = True
            else:
                entry['current'] = False


        elif field == 'topic' or field == 'project':
            entry[field] = content

        else:
            raise ValueError("Syntax error in line: {}".format(line))

    if entry:
        cooked.append(entry)

    return cooked


def main():
    f = open("data/schedule.txt")
    parsed = process(f)
    print(parsed)

if __name__ == "__main__":
    main()
