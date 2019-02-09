# import xml.etree.cElementTree as ET
#
#
# def parseXML(xml_file):
#     """
#     Парсинг XML используя ElementTree
#     """
#     tree = ET.ElementTree(file=xml_file)
#     print(tree.getroot())
#     root = tree.getroot()
#     print("tag=%s, attrib=%s" % (root.tag, root.attrib))
#
#     for child in root:
#         print(child.tag, child.attrib)
#         if child.tag == "appointment":
#             for step_child in child:
#                 print(step_child.tag)
#
#     # Парсинг всей XML структуры.
#     print("-" * 40)
#     print("Iterating using a tree iterator")
#     print("-" * 40)
#     iter_ = tree.iter()
#
#     for elem in iter_:
#         print(elem.tag, elem.)
#
#     # получаем данные используя дочерние элементы.
#     print("-" * 40)
#     print("Обрабатываем дочерние элементы getchildren()")
#     print("-" * 40)
#     appointments = root.getchildren()
#
#     for appointment in appointments:
#         appt_children = appointment.getchildren()
#         for appt_child in appt_children:
#             print("%s=%s" % (appt_child.tag, appt_child.text))
#
#
# if __name__ == "__main__":
#     parseXML("schedule.xml")

from lxml import etree

# def parseXML(xmlFile):
#     """
#     Парсинг XML
#     """
#
#     with open(xmlFile, "r", encoding="utf_8") as fobj:
#         xml = fobj.read()
#
#     print(xml)
#     root = etree.fromstring(xml)
#
#     for appt in root.getchildren():
#         for elem in appt.getchildren():
#             if not elem.text:
#                 text = "None"
#             else:
#                 text = elem.text
#
#             print(elem.tag + " => " + text)
#
#
# if __name__ == "__main__":
#     parseXML("schedule.xml")

from xml.dom import minidom


DAY_CNT = 6
LES_CNT = 7


def from_xml_to_text():
    xmldoc = minidom.parse('schedule.xml')
    daylist = xmldoc.getElementsByTagName('day')
    itemlist = xmldoc.getElementsByTagName('item')

    # print(len(itemlist))

    schedule = [[[] for les in range(LES_CNT + 1)] for day in range(DAY_CNT + 1)]
    day_of_the_week = 1

    for day in daylist:
        # print(day.attributes['title'].value)

        for lesson in day.childNodes:

            if lesson.nodeType == lesson.ELEMENT_NODE and lesson.tagName == "item":
                num_of_the_lesson = int(lesson.attributes['num'].value)
                schedule[day_of_the_week][num_of_the_lesson].append(lesson.attributes['name'].value)
                # print(lesson.attributes['name'].value)

        # print("-" * 40)
        day_of_the_week += 1
    return schedule


if __name__ == '__main__':
    print(from_xml_to_text())
