# -*- coding: utf-8 -*-

"""Partnership with the MHNT."""

__authors__ = 'User:Jean-Frédéric'


import sys
import os
import re
from uploadlibrary.UploadBot import DataIngestionBot, UploadBotArgumentParser
from uploadlibrary import metadata
import uploadlibrary.PostProcessing as commonprocessors
from iptcinfo import IPTCInfo, IPTCData
reload(sys)
sys.setdefaultencoding('utf-8')


class MHNTMetadataCollection(metadata.MetadataCollection):

    """Handling a MHNT metadata collection."""

    def handle_record(self, image):
        """Handle a record.

        Read metadata from IPTC fields, decodes latin-1 encoding.
        Return a new MHNTRecord

        """
        info = IPTCInfo(image)
        image_metadata = {}
        for key, value in info.getData().items():
            key = IPTCData.keyAsStr(key)
            try:
                image_metadata[key] = self.decode_strip_encode(value)
            except AttributeError:
                image_metadata[key] = [self.decode_strip_encode(x) for x in value]
        image_metadata['original_name'] = search_original_name(image_metadata['caption/abstract'])
        if 'headline' in image_metadata:
            image_metadata['title'] = image_metadata['headline']
        elif image_metadata['original_name']:
            image_metadata['title'] = image_metadata['original_name']
        else:
            image_metadata['title'] = "NONE"
        image_metadata['nonstandard_231'] = "REDACTED"
        return metadata.MetadataRecord(image, image_metadata)

    @staticmethod
    def decode_strip_encode(value):
        res = None
        try:
            res = value.decode('utf-8').strip()
        except UnicodeDecodeError:
            res = value.decode('latin-1').strip()
        return res

def main(args):
    """Main method."""
    collection = MHNTMetadataCollection()
    files_path = os.path.abspath('./images/')
    collection.retrieve_metadata_from_files(files_path)
    #collection.write_metadata_to_csv(open("toto.csv", 'w'))
    
    alignment_template = 'User:Jean-Frédéric/AlignmentRow'.encode('utf-8')
    #
    #if args.make_alignment:
    #    for key, value in collection.count_metadata_values().items():
    #        collection.write_dict_as_wiki(value, key, 'wiki',
    #                                      alignment_template)

    if args.post_process:
        mapping_fields = ['by-line', 'keywords']
        mapper = commonprocessors.retrieve_metadata_alignments(mapping_fields,
                                                               alignment_template)
        mapping_methods = {
            'by-line': (commonprocessors.process_with_alignment, {'mapper': mapper}),
            'keywords': (commonprocessors.process_with_alignment_on_list, {'mapper': mapper}),
            'caption/abstract': (process_caption, {}),
            

        }
        categories_counter, categories_count_per_file = collection.post_process_collection(mapping_methods)
        metadata.categorisation_statistics(categories_counter, categories_count_per_file)

        template_name = 'User:Jean-Frédéric/MHNT/Ingestion'.encode('utf-8')
        front_titlefmt = ""
        variable_titlefmt = "%(title)s"
        rear_titlefmt = " - Fonds Trutat - %(object name)s"

        reader = iter(collection.records)
        uploadBot = DataIngestionBot(reader=iter(reader),
                                     front_titlefmt=front_titlefmt,
                                     rear_titlefmt=rear_titlefmt,
                                     variable_titlefmt=variable_titlefmt,
                                     pagefmt=template_name,
                                     subst=True,
                                     verifyDescription=False
                                     )

    if args.upload:
        uploadBot.run()
    elif args.dry_run:
        #for record in collection.records:
        #    record.to_disk('%(Cote)s', 'toto')
        #s = open('filename.xml', 'w')
        #collection.write_metadata_to_xml(s)
        uploadBot.dry_run()

def process_caption(field, old_field_value):
    result = {field: old_field_value}
    (date, year) = commonprocessors.look_for_date_unwrapped(old_field_value)
    if date:
        result['date'] = date
    if year:
        result['year'] = year
    parsed_format = _parse_format(old_field_value)
    if parsed_format:
        result['parsed_format'] = parsed_format
    parsed_technique = _parse_technique(old_field_value)
    if parsed_technique:
        result['parsed_technique'] = parsed_technique
    return result


def search_original_name(text):
    name_pattern = re.compile(r"""
        "(?P<name>.*?)"
    """, re.X + re.S)
    match = re.search(name_pattern, text)
    if match:
        new_value = match.group('name').strip()
        return new_value
    else:
        #print text
        return ""



def _parse_technique(text):
    values = [
    "plaque négative au gélatino-bromure d'argent",
    "plaque négative au gélatino bromure d'argent",
    "plaque négative au collodion au tanin",
    "plaque négative au collodion albuminé",
    "plaque négative au collodion",
    "plaque négative stéréoscopique au gélatino-bromure d'argent",
    "plaque négative stéréoscopique au gélatino bromure d'argent",
    "plaque négative stéréoscopique au collodion albuminé",
    "plaque négative stéréoscopique au collodion au tanin",
    "plaque négative stéréoscopique au collodion humide",
    "plaque négative stéréoscopique au collodion",
    "plaque de projection positive"
    ]
    for item in values:
        match = text.find(item)
        if match >= 0:
            return item
    return None

def _parse_format(text):
    """Parse stuff like format 6,5x9 cm"""
    format_pattern = re.compile(r"""
        (format)\s
        (?P<a>[\d,\.]+?)   # Digits, comma or dot, captured as group
        x                  # x
        (?P<b>[\d,\.]+?)   # Same
        \s?cm              # Whitespace, cm
        """, re.X)
    match = re.search(format_pattern, text)
    if match:
        new_value = commonprocessors._pattern_to_size(match).strip()
        return new_value
    else:
        return None


if __name__ == "__main__":
    parser = UploadBotArgumentParser()
    arguments = parser.parse_args()
    if not any(arguments.__dict__.values()):
        parser.print_help()
    else:
        main(arguments)
