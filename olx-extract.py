import sys, os, shutil
import os.path as path
import lxml.etree as et


# print helpful message
if len(sys.argv) != 4:
    print "[info] usage: python olxextract.py [unzipped course folder] [new course partial folder] [chapter/sequential/vertical]"
    sys.exit(0)


# grab the directory of course and update
course = sys.argv[1]
update = sys.argv[2]
section = sys.argv[3]


if not path.exists(course) or not path.isdir(course):
    print "Course folder [" + course + "] does not exist"
    sys.exit(0)
elif path.exists(update):
    print "Update folder [" + update + "] already exist, please choose a new name"
    sys.exit(0)
os.mkdir(update)


# test if @section is valid
sections = { "chapter", "sequential", "vertical" }
if section not in sections:
    print "[info] please choose among chapter, sequential and vertical"
    sys.exit(0)


def list_xml(directory):
    """ List all the xml files in this @directory """
    return filter(lambda f: f[0] != "." and f[-4:] == ".xml", os.listdir(directory))


def scan(document):
    """ Scan the xml @document and return a tuple of its directory and display_name """
    result = ""
    with open(document, "r") as f:
        root = et.fromstring(f.read())
        result = root.get("display_name")
    return (document, result)


def scan_xml(directory):
    """ Use @scan and @list_xml to scan all the xml files in this @directory and return a list of tuple """
    return [scan(path.join(directory, document)) for document in list_xml(directory)]


# list all the sections
section_tuples = scan_xml(path.join(course, section))
print "please choose a (or multiple)", section, "to be extracted; separate multiple", section, "by ','"
for i, sec in enumerate(section_tuples):
    print i, ":", sec[1], "@", sec[0]


# let the user choose sections to export
def choose():
    raw = raw_input("choose> ")
    try:
        raw = map(lambda s: int(s.strip()), raw.split(","))
    except Exception as e:
        print "invalid input: ", e
        return choose()
    return raw
raw = choose()


class FileExistsError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg + " already exists; there might be two upper section referring to the same lower section"

copies = 0
base_sections = { "html", "discussion", "problem", "video" }
def recursive_copy(filename, section):
    if path.exists(path.join(update, section, filename)):
        raise FileExistsError(filename)
    if not path.exists(path.join(update, section)):
        os.mkdir(path.join(update, section))
    parent = path.join(course, section, filename)
    global copies
    copies += 1
    shutil.copyfile(parent, path.join(update, section, filename))
    if section not in base_sections:  
        children = []
        with open(parent, "r") as f:
            root = et.fromstring(f.read())
            for child in root:
                children.append( (child.get("url_name") + ".xml", child.tag) )
        for child in children:
            recursive_copy(child[0], child[1])


raw = sorted(raw, reverse=True)
for i in raw:
    section_tuple = section_tuples.pop(i)
    recursive_copy(path.basename(section_tuple[0]), section)


print "[info] course partials in olx-format generated in", update
print "[info]", copies, "files copied"

