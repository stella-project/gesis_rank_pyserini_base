import os
from pyserini.index.__main__ import JIndexCollection
from pyserini.search import SimpleSearcher
import jsonlines
from multiprocessing import Pool
import shutil

CHUNKSIZE = 100000000

ARGS = ["-collection", "JsonCollection",
        "-generator", "DefaultLuceneDocumentGenerator",
        "-threads", "6",
        "-input", "./index/convert/",
        "-index", "./index/",
        "-storePositions",
        "-storeDocvectors",
        "-storeRaw"]


class Ranker(object):

    def __init__(self):
        self.idx = None
        self.searcher = None

    def _make_chuncks(self, dir):
        for file in os.listdir(dir):
            if file.endswith(".jsonl"):
                with open(os.path.join(dir, file), 'r') as f:
                    cnt = 0
                    while True:
                        lines = f.readlines(CHUNKSIZE)
                        if not lines:
                            break
                        with open(''.join(['./index/chunks/', file[:-6], '_', str(cnt), '.jsonl']), 'w') as _chunk_out:
                            for line in lines:
                                _chunk_out.write(line)
                        cnt += 1

    def _convert_chunks(self, file):
        with jsonlines.open(os.path.join('./index/convert/', file), mode='w') as writer:
            with jsonlines.open(os.path.join("./index/chunks/", file)) as reader:
                for obj in reader:
                    title = obj.get('title') or ''
                    title = title[0] if type(title) is list else title

                    abstract = obj.get('abstract') or ''
                    abstract = abstract[0] if type(abstract) is list else abstract

                    author = obj.get('person') or ''
                    author = ' '.join(author) if type(author) is list else author

                    topic = obj.get('topic') or ''
                    topic = ' '.join(topic) if type(topic) is list else topic

                    try:
                        doc = {'id': obj.get('id'),
                               'contents': ' '.join([title,
                                                     abstract,
                                                     author,
                                                     topic])}
                        writer.write(doc)
                    except Exception as e:
                        print(e)

    def _mkdir(self, dir):
        try:
            os.mkdir(dir)
        except OSError as error:
            print(error)

    def index(self):
        self._mkdir('./index/')
        self._mkdir('./index/convert/')
        self._mkdir('./index/chunks/')
        self._make_chuncks("./data/gesis-search/documents/")
        p = Pool()
        p.map(self._convert_chunks, os.listdir("./index/chunks/"))
        p.close()
        shutil.rmtree('./index/chunks')
        JIndexCollection.main(ARGS)
        self.searcher = SimpleSearcher('./index/')
        shutil.rmtree('./index/convert/')

    def rank_publications(self, query, page, rpp): 
        hits = []
        itemlist = []

        if query is not None:
            if self.idx is None:
                try:
                    self.searcher = SimpleSearcher('./index/')
                    self.searcher.set_rm3(10, 10, 0.5)
                except Exception as e:
                    print('No index available: ', e)

            if self.searcher is not None:
                hits = self.searcher.search(query, k=100)
                itemlist = [hit.docid for hit in hits[page*rpp:(page+1)*rpp]]

        return {
            'page': page,
            'rpp': rpp,
            'query': query,
            'itemlist': itemlist,
            'num_found': len(hits)
        }


class Recommender(object):

    def __init__(self):
        self.idx = None

    def index(self):
        pass

    def recommend_datasets(self, item_id, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }

    def recommend_publications(self, item_id, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }
