# Taken from: https://gist.github.com/dwinston/59c0a6ae40eb04c7c4a7816943e14941
from pymatgen import MPRester

try:
    from pydash import chunk as get_chunks
except ImportError:
    from math import ceil

    def get_chunks(array, size=1):
        chunks = int(ceil(len(array) / float(size)))
        return [array[i * size : (i + 1) * size] for i in range(chunks)]


try:
    # import `tqdm_notebook` for prettier output in Jupyter Notebook
    from tqdm import tqdm as PBar
except ImportError:

    class PBar:
        def __init__(self, total):
            self.total = total
            self.done = 0
            self.report()

        def update(self, amount):
            self.done += amount
            self.report()

        def report(self):
            print(
                "{} of {} done {:.1%}".format(
                    self.done, self.total, self.done / self.total
                )
            )


def bulk_query(self, criteria, properties, chunk_size=100, **kwargs):
    data = []
    mids = [d["material_id"] for d in self.query(criteria, ["material_id"])]
    chunks = get_chunks(mids, size=chunk_size)
    progress_bar = PBar(total=len(mids))
    if not isinstance(criteria, dict):
        criteria = self.parse_criteria(criteria)
    for chunk in chunks:
        chunk_criteria = criteria.copy()
        chunk_criteria.update({"material_id": {"$in": chunk}})
        data.extend(self.query(chunk_criteria, properties, **kwargs))
        progress_bar.update(len(chunk))
    return data


MPRester.bulk_query = bulk_query

# Now, instantiate an MPRester object and use `bulk_query` as you would `query`.
#
# Example usage:

mpr = MPRester()
# Download strutures for all lithium oxide ternaries (>1000 structures):
data = mpr.bulk_query("Li-O-*", ["structure", "material_id"])

# Finally, you can save to a local MongoDB.
# Queries to MPRester.query use MongoDB syntax.
# However, interacting with MongoDB is not the same as MPRester.
# Some example usage follows. Consult the MongoDB docuemntation for more info.
#
# Example usage:


from monty.json import MontyDecoder  # installed with pymatgen
from pymongo import MongoClient

client = MongoClient()
db = client["whatever_database_name_you_want"]

# Re-fetch data here to illustrate that you cannot import e.g. pymatgen Structure
# objects directly into MongoDB.
data = mpr.bulk_query("Li-O-*", ["structure", "material_id"], mp_decode=False)

# Comment out below to *not* clean out your local database's "materials" collection
# before inserting new documents.
db.materials.delete_many({})

db.materials.insert_many(data)

# Now, all data is saved to your disk, accessible anytime without using our API.
# Depending on your use case, be sure to periodically query our API for updated data.

decoder = MontyDecoder()

doc = db.materials.find_one({"material_id": "mp-1020014"})
print(type(doc["structure"]))  # <class 'dict'>
doc = decoder.process_decoded(doc)
print(type(doc["structure"]))  # <class 'pymatgen.core.structure.Structure'>

docs = list(
    db.materials.find(
        {"material_id": {"$in": ["mp-1020014", "mp-1098011"]}}, ["structure"]
    )
)
