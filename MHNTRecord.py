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
    import pickle
    with open("metadata.dump", 'w') as f:
        pickle.dump(collection, f)
    #collection .post_process_collection(mapping)
    #values = collection.index_unique_metadata_values()
    values = collection.count_metadata_values()
    print values
    #print values.keys()
    #print len(values['keywords'])
    #collection.print_metadata_of_record(index)


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
