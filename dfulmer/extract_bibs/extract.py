from functools import cached_property
from extract_bibs.bib import Bib
from collections import defaultdict

class Extract:
    def __init__(self, record, bib=None):
        self.record = record
        self._bib = bib     

    def process(self):
        if self.has_008:
                if self.bib.pub_date[2] != "":
                     print(f"{self.bib.pub_date[2]}")
                if self.bib.arrival_date[2] != "":
                     print(f"{self.bib.arrival_date[2]}")
                
                          
                #return { "no 008 field": "0", "no arrival date": f"{self.bib.arrival_date[1]}", "line": f"SYSNUM:{self.bib.recid}	FMT:BK	LANG:{self.bib.f008_lang}	TITLE:{self.bib.title_ab}	AUTHOR:{self.bib.author_and_tag[0]}	AUTHOR_TAG:{self.bib.author_and_tag[1]}	DATE:{self.bib.pub_date[0]}	TITLE_H:{self.bib.title_h}	IMPRINT:{self.bib.imprint}	ARRIVAL_DATE:{self.bib.arrival_date[0]}{self.bib.search_keys}", "source of date": f"{self.bib.pub_date[1]}"}
                line = (
                    f"SYSNUM:{self.bib.recid}\t"
                    f"FMT:BK\t"
                    f"LANG:{self.bib.f008_lang}\t"
                    f"TITLE:{self.bib.title_ab}\t"
                    f"AUTHOR:{self.bib.author_and_tag[0]}\t"
                    f"AUTHOR_TAG:{self.bib.author_and_tag[1]}\t"
                    f"DATE:{self.bib.pub_date[0]}\t"
                    f"TITLE_H:{self.bib.title_h}\t"
                    f"IMPRINT:{self.bib.imprint}\t"
                    f"ARRIVAL_DATE:{self.bib.arrival_date[0]}"
                    f"{self.bib.search_keys}"
                )
                return {
                    "no 008 field": "0",
                    "no arrival date": f"{self.bib.arrival_date[1]}",
                    "line": line,
                    "source of date": f"{self.bib.pub_date[1]}",
                }
        else:
            return { "no 008 field": "1", "no arrival date": "0", "line": ""}            

    @cached_property
    def bib(self):
        if not self._bib:
            self._bib = Bib(self.record)
        return self._bib
    
    @property
    def has_008(self):
        return bool(len(self.record.get_fields("008")))
