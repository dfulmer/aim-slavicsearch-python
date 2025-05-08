from codecs import decode
import re

class Bib:
    def __init__(self, record):
        self.record = record
    
    @property
    def recid(self):
        return self.record['001'].value()
    
    @property
    def has_008(self):
        return bool(len(self.record.get_fields("008")))
        
    @property
    def f008_lang(self):
        fields_008 = self.record.get_fields('008')
        if not fields_008:
            return ""
        field_008 = fields_008[0].value()
        f008_lang = field_008[35:38]
        return f008_lang
    
    @property
    def title_ab(self):
        field_245 = self.record.get_fields('245')
        if field_245:
            field_245 = field_245[0]
            nf_ind = int(field_245.indicator2)
            title_ab = field_245['a'] or ''
            if 'b' in field_245:
                sub_bs = field_245.get_subfields('b')
                for sub in sub_bs:
                    title_ab = title_ab + " " + sub

            title_ab_bytes = title_ab.encode('utf-8')  # Work in bytes to match Perl behavior
            title_ab_bytes = title_ab_bytes[nf_ind:]   # Skip non-filing characters
            # Decode back into a proper Unicode string
            title_ab = decode(title_ab_bytes, 'utf-8')

        title_ab = title_ab.strip() # clear any leading or trailing whitespace
        return title_ab
    
    @property
    def author_and_tag(self):
        author_and_tag_list = ['', '']
        for tag in ['100', '110', '111', '130']:
            field = self.record.get_fields(tag)
            if field:
                field_1xx = field[0]
                author_and_tag_list[0] = ''.join(field_1xx.get_subfields('a'))
                author_and_tag_list[1] = field_1xx.tag

                break
        return author_and_tag_list
    
    @property
    def pub_date(self):
        pub_date = ''
        date_source = ''
        field_260_264 = None
        for tag in ['260', '264']:
            fields = self.record.get_fields(tag)
            if fields:
                field_260_264 = fields[0]
                imprint_parts = field_260_264.get_subfields('b')
                # subfield b as imprint
                imprint = ' '.join(imprint_parts) if imprint_parts else ''
                subfield_c = field_260_264.get_subfields('c')
                if subfield_c:
                    pub_date = subfield_c[0]
                    date_source = '260/4 subfield c'
                    return [pub_date, date_source, ""]
                # Fall back: parse date(s) from full field text
                pub_text = field_260_264.value()
                dates = re.findall(r'\d{4}', pub_text)
                if not dates:
                    # print(f"{recID}: no dates in pub text: {pub_text}")
                    fields_008 = self.record.get_fields('008')
                    field_008 = fields_008[0].value()
                    f008_date = field_008[7:11]
                    date_source = 'date from 008'
                    return [f008_date, date_source, ""]
                if len(dates) == 1:
                    date_source = '260/4 single date from text'
                    return [dates[0], date_source, ""]
                match = re.search(r'\d{4}-\d{4}', pub_text)
                if match:
                    date_range = match.group(0)
                    #print(f"{self.recid}: date range from 260: {pub_text}: {date_range}")
                    date_source = '260/4 date range from text'
                    return [date_range, date_source, f"{self.recid}: date range from 260: {pub_text}: {date_range}"]

                if len(dates) > 1:
                    #print(f"{self.recid}: {pub_text}: {', '.join(dates)}")
                    date_source = '260/4 unknown multiple dates in from text'
                    pub_date = ''
                    return [pub_date, date_source, f"{self.recid}: {pub_text}: {', '.join(dates)}"]
                break

        if not pub_date:   
            fields_008 = self.record.get_fields('008')
            field_008 = fields_008[0].value()
            f008_date = field_008[7:11]
            date_source = 'date from 008'
            return [f008_date, date_source, ""]
                
    @property
    def title_h(self):
        title_h = ''
        field_245 = self.record.get_fields('245')
        field_245 = field_245[0]           
        title_h = field_245.get_subfields('h')
        title_h = title_h[0] if title_h else ''
        return title_h

    @property
    def imprint(self):
        imprint = ''
        field_260_264 = None
        for tag in ['260', '264']:
            fields = self.record.get_fields(tag)
            if fields:
                field_260_264 = fields[0]
                imprint_parts = field_260_264.get_subfields('b')
                # subfield b as imprint
                imprint = ' '.join(imprint_parts) if imprint_parts else ''
        return imprint

    @property
    def arrival_date(self):
        arrival_dates = {}
        for field in self.record.get_fields('974'):
            if ''.join(field.get_subfields('c')) != 'IS-SEEES':
                continue

            r_val = ''.join(field.get_subfields('r'))
            if r_val:
                date = r_val[:10]
                arrival_dates[date] = arrival_dates.get(date, 0) + 1

        sorted_dates = sorted(arrival_dates.keys())

        if not sorted_dates:
            return ['', '1', '']

        if len(sorted_dates) > 1:
            return [f'{sorted_dates[-1]}', '0', f"{self.recid}: {len(sorted_dates)} arrival dates in record: {', '.join(sorted_dates)}"]

        return [f'{sorted_dates[-1]}', '0', '']
    
    @property
    def search_keys(self):
        search_keys = []

        # ISBNs from 020$a
        isbns = set()
        for field in self.record.get_fields('020'):
            suba = field.get_subfields('a')
            if suba:
                isbns.update(suba)
        # Sorting...
        # for isbn in isbns:
        #     search_keys.append(f"ISBN:{isbn}")
        for isbn in sorted(isbns):
            search_keys.append(f"ISBN:{isbn}")

        # ISSNs from 022$a
        issns = set()
        for field in self.record.get_fields('022'):
            suba = field.get_subfields('a')
            if suba:
                issns.update(suba)
        for issn in issns:
            search_keys.append(f"ISSN:{issn}")

        # OCLC numbers from 035$a
        oclc_numbers = set()
        for field in self.record.get_fields('035'):
            suba_list = field.get_subfields('a')
            for suba in suba_list:
                if not re.search(r'(oco{0,1}lc|ocm|ocn)', suba, re.IGNORECASE):
                    continue
                match = re.search(r'\d+', suba)
                if match:
                    oclc_number = int(match.group(0))
                    oclc_numbers.add(oclc_number)
        for oclc_number in oclc_numbers:
            search_keys.append(f"OCLC:{oclc_number}")

        output = '	'.join(search_keys)
        if output:
            output = '	' + output

        return output