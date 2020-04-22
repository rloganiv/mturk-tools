"""
For programatic construction of QuestionForm objects.
"""
import string
import xml.etree.ElementTree as xml

DEFAULT_NAMESPACE = 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2017-11-06/QuestionForm.xsd'


class QuestionForm:
    def __init__(self):
        root = xml.Element('QuestionForm', xmlns=DEFAULT_NAMESPACE)
        self.etree = xml.ElementTree(root)

    def add_overview(self, title, text):
        overview = xml.SubElement(self.etree.getroot(), 'Overview')
        title_element = xml.SubElement(overview, 'Title')
        title_element.text = title
        text_element = xml.SubElement(overview, 'Text')
        text_element.text = text

    def add_multiple_choice_question(self, question_identifier, choices):
        question = xml.SubElement(self.etree.getroot(), 'Question')

        question_identifier_element = xml.SubElement(question, 'QuestionIdentifier')
        question_identifier_element.text = question_identifier

        is_required = xml.SubElement(question, 'IsRequired')
        is_required.text = 'true'

        question_content = xml.SubElement(question, 'QuestionContent')
        question_content_text = xml.SubElement(question_content, 'Text')
        question_content_text.text = 'Choose one:'

        answer_specification = xml.SubElement(question, 'AnswerSpecification')
        selection_answer = xml.SubElement(answer_specification, 'SelectionAnswer')
        style_suggestion = xml.SubElement(selection_answer, 'StyleSuggestion')
        style_suggestion.text = 'radiobutton'
        selections = xml.SubElement(selection_answer, 'Selections')
        for i, choice in enumerate(choices):
            selection = xml.SubElement(selections, 'Selection')
            identifier = xml.SubElement(selection, 'SelectionIdentifier')
            identifier.text = string.ascii_lowercase[i]
            selection_text = xml.SubElement(selection, 'Text')
            selection_text.text = choice

    def tostring(self):
        return xml.tostring(self.etree.getroot(), encoding='unicode')
