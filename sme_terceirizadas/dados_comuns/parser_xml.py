from rest_framework_xml.parsers import XMLParser


class ListXMLParser(XMLParser):
    def _check_xml_list(self, element):
        return len(element) > 1 and len(set([child.tag for child in element])) <= 1

    def _xml_convert(self, element):
        children = list(element)

        if len(children) == 0:
            return self._type_convert(element.text)
        else:
            # if the fist child tag is list-item means all children are list-item
            if self._check_xml_list(element):
                data = []
                for child in children:
                    data.append(self._xml_convert(child))
            else:
                data = {}
                for child in children:
                    data[child.tag] = self._xml_convert(child)

        return data
