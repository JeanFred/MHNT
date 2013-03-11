# -*- coding: latin-1 -*-

"""Partnership with the MHNT."""

__authors__ = 'User:Jean-Frédéric'


import sys
import os
from uploadlibrary.metadata import MetadataCollection, MetadataRecord
from uploadlibrary.UploadBot import DataIngestionBot
from iptcinfo import IPTCInfo, IPTCData
reload(sys)
sys.setdefaultencoding('utf-8')


class MHNTMetadataCollection(MetadataCollection):

    """Handling a Mundaneum metadata collection."""

    def handle_record(self, image):
        """Handle a record.

        Read metadata from IPTC fields, decodes latin-1 encoding.
        Return a new MHNTRecord

        """
        info = IPTCInfo(image)
        metadata = {}
        for key, value in info.getData().items():
            key = IPTCData.keyAsStr(key)
            try:
                metadata[key] = value.decode('utf-8').strip()
            except:
                try:
                    metadata[key] = value.decode('latin-1').strip()
                except:
                    metadata[key] = value
        return MetadataRecord(image, metadata)


def main(args):
    """Main method."""
    collection = MHNTMetadataCollection()
    files_path = os.path.abspath('./images/')
    collection.retrieve_metadata_from_files(files_path)

    alignment_template = 'User:Jean-Frédéric/AlignmentRow'.encode('utf-8')

    if args.make_alignment:
        for key, value in collection.count_metadata_values().items():
            collection.write_dict_as_wiki(value, key, 'wiki',
                                          alignment_template)

    if args.post_process:
        collection.retrieve_metadata_alignments(None,
                                                alignment_template)
        mapping = {}
        reader = collection.post_process_collection(mapping)
        template_name = 'User:Jean-Frédéric/Trutat/Ingestion'.encode('utf-8')
        titlefmt = "%(headline)s - Fonds Trutat - %(object name)s"
        uploadBot = DataIngestionBot(reader=iter(collection.records),
                                     titlefmt=titlefmt,
                                     pagefmt=template_name)
        if args.upload:
            uploadBot.doSingle()
        elif args.dry_run:
            uploadBot.dry_run()


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Process metadata and upload to Commons")
    parser.add_argument('--make-alignment', action="store_true",
                        help='')
    parser.add_argument('--post-process', action="store_true",
                        help='')
    parser.add_argument('--dry-run', action="store_true",
                        help='')
    parser.add_argument('--upload', action="store_true",
                        help='')
    args = parser.parse_args()
    main(args)
