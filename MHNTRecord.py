# -*- coding: latin-1 -*-

"""Partnership with the MHNT."""

__authors__ = 'User:Jean-Frédéric'

import sys
sys.path.append('../MassUploadLibrary')
import os
from uploadlibrary import metadata
from iptcinfo import IPTCInfo, IPTCData


class MHNTRecord(metadata.MetadataRecord):

    """Represent a record, with its associated metadata."""

    def get_title(self):
        """Return the title for the file."""
        name = None
        ID = None
        return "%s - %s - MHNT" % (name, ID)


class MHNTMetadataCollection(metadata.MetadataCollection):

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
                metadata[key] = value.decode('latin-1')
            except:
                metadata[key] = value
        return MHNTRecord(**metadata)


def main(index):
    """Main method."""
    print "main()"
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
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main(0)