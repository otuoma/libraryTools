from lxml import etree

def convert_tei_to_jats(tei_xml_string, metadata_overrides=None):
    """
    Converts a Grobid TEI XML string to JATS XML (Journal Publishing Tag Set).
    Optionally accepts metadata_overrides to replace extracted values.
    """
    try:
        tei_root = etree.fromstring(tei_xml_string.encode('utf-8'))
        namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        # Create JATS root
        jats_root = etree.Element("article", 
                                  {"article-type": "research-article", 
                                   "dtd-version": "1.2", 
                                   "{http://www.w3.org/XML/1998/namespace}lang": "en"},
                                  nsmap={None: "http://jats.nlm.nih.gov/publishing/1.2/JATS-journalpublishing1.dtd"})
        
        front = etree.SubElement(jats_root, "front")
        
        # Journal Meta
        journal_meta = etree.SubElement(front, "journal-meta")
        journal_id = etree.SubElement(journal_meta, "journal-id", {"journal-id-type": "publisher-id"})
        journal_id.text = "Unknown"
        
        journal_title_group = etree.SubElement(journal_meta, "journal-title-group")
        journal_title = etree.SubElement(journal_title_group, "journal-title")
        
        if metadata_overrides and metadata_overrides.get('journal'):
            journal_title.text = metadata_overrides['journal']
        else:
            journal_title.text = "Unknown Journal"

        if metadata_overrides and metadata_overrides.get('publisher'):
             publisher = etree.SubElement(journal_meta, "publisher")
             publisher_name = etree.SubElement(publisher, "publisher-name")
             publisher_name.text = metadata_overrides['publisher']
        
        if metadata_overrides and metadata_overrides.get('issn'):
            for issn_val in metadata_overrides['issn']:
                 issn_elem = etree.SubElement(journal_meta, "issn")
                 issn_elem.text = issn_val

        # Article Meta
        article_meta = etree.SubElement(front, "article-meta")
        
        # Title
        title_group = etree.SubElement(article_meta, "title-group")
        article_title = etree.SubElement(title_group, "article-title")
        
        if metadata_overrides and metadata_overrides.get('title'):
            article_title.text = metadata_overrides['title']
        else:
            title_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', namespaces=namespaces)
            if title_nodes and title_nodes[0].text:
                article_title.text = title_nodes[0].text

        # Authors
        contrib_group = etree.SubElement(article_meta, "contrib-group")
        
        if metadata_overrides and metadata_overrides.get('authors'):
            for author in metadata_overrides['authors']:
                contrib = etree.SubElement(contrib_group, "contrib", {"contrib-type": "author"})
                name = etree.SubElement(contrib, "name")
                if author.get('last_name'):
                    sn = etree.SubElement(name, "surname")
                    sn.text = author['last_name']
                if author.get('first_name'):
                    gn = etree.SubElement(name, "given-names")
                    gn.text = author['first_name']
                if author.get('affiliation'):
                    aff = etree.SubElement(contrib_group, "aff")
                    aff.text = author['affiliation']
        else:
            author_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author', namespaces=namespaces)
            for author in author_nodes:
                contrib = etree.SubElement(contrib_group, "contrib", {"contrib-type": "author"})
                name = etree.SubElement(contrib, "name")
                
                persName = author.find('tei:persName', namespaces)
                if persName is not None:
                    surname = persName.find('tei:surname', namespaces)
                    forename = persName.find('tei:forename', namespaces)
                    
                    if surname is not None and surname.text:
                        sn = etree.SubElement(name, "surname")
                        sn.text = surname.text
                    if forename is not None and forename.text:
                        gn = etree.SubElement(name, "given-names")
                        gn.text = forename.text

        # Volume / Issue / Pages
        if metadata_overrides and metadata_overrides.get('volume'):
            vol = etree.SubElement(article_meta, "volume")
            vol.text = metadata_overrides['volume']
        else:
             monogr = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr', namespaces=namespaces)
             if monogr:
                 imprint = monogr[0].find('tei:imprint', namespaces)
                 if imprint is not None:
                     biblScope_vol = imprint.find('tei:biblScope[@unit="volume"]', namespaces)
                     if biblScope_vol is not None and biblScope_vol.text:
                         vol = etree.SubElement(article_meta, "volume")
                         vol.text = biblScope_vol.text

        if metadata_overrides and metadata_overrides.get('issue'):
            issue = etree.SubElement(article_meta, "issue")
            issue.text = metadata_overrides['issue']
        else:
             monogr = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr', namespaces=namespaces)
             if monogr:
                 imprint = monogr[0].find('tei:imprint', namespaces)
                 if imprint is not None:
                     biblScope_issue = imprint.find('tei:biblScope[@unit="issue"]', namespaces)
                     if biblScope_issue is not None and biblScope_issue.text:
                         issue = etree.SubElement(article_meta, "issue")
                         issue.text = biblScope_issue.text

        if metadata_overrides and metadata_overrides.get('fpage'):
            fpage = etree.SubElement(article_meta, "fpage")
            fpage.text = metadata_overrides['fpage']
        if metadata_overrides and metadata_overrides.get('lpage'):
            lpage = etree.SubElement(article_meta, "lpage")
            lpage.text = metadata_overrides['lpage']
        
        if not (metadata_overrides and (metadata_overrides.get('fpage') or metadata_overrides.get('lpage'))):
             monogr = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr', namespaces=namespaces)
             if monogr:
                 imprint = monogr[0].find('tei:imprint', namespaces)
                 if imprint is not None:
                     biblScope_page = imprint.find('tei:biblScope[@unit="page"]', namespaces)
                     if biblScope_page is not None:
                         if biblScope_page.get('from'):
                             fpage = etree.SubElement(article_meta, "fpage")
                             fpage.text = biblScope_page.get('from')
                         if biblScope_page.get('to'):
                             lpage = etree.SubElement(article_meta, "lpage")
                             lpage.text = biblScope_page.get('to')

        # Abstract
        if metadata_overrides and metadata_overrides.get('abstract'):
            abstract = etree.SubElement(article_meta, "abstract")
            p = etree.SubElement(abstract, "p")
            p.text = metadata_overrides['abstract']
        else:
            abstract_nodes = tei_root.xpath('//tei:teiHeader/tei:profileDesc/tei:abstract/tei:p', namespaces=namespaces)
            if abstract_nodes:
                abstract = etree.SubElement(article_meta, "abstract")
                for p_node in abstract_nodes:
                    p = etree.SubElement(abstract, "p")
                    p.text = p_node.text

        # Keywords
        if metadata_overrides and metadata_overrides.get('keywords'):
            kwd_group = etree.SubElement(article_meta, "kwd-group")
            for keyword in metadata_overrides['keywords']:
                kwd = etree.SubElement(kwd_group, "kwd")
                kwd.text = keyword

        # License
        if metadata_overrides and (metadata_overrides.get('license_text') or metadata_overrides.get('license_url')):
            permissions = etree.SubElement(article_meta, "permissions")
            license_elem = etree.SubElement(permissions, "license")
            if metadata_overrides.get('license_url'):
                license_elem.set("{http://www.w3.org/1999/xlink}href", metadata_overrides['license_url'])
            if metadata_overrides.get('license_text'):
                license_p = etree.SubElement(license_elem, "license-p")
                license_p.text = metadata_overrides['license_text']

        # Body
        body = etree.SubElement(jats_root, "body")
        div_nodes = tei_root.xpath('//tei:text/tei:body/tei:div', namespaces=namespaces)
        
        for div_node in div_nodes:
            sec = etree.SubElement(body, "sec")
            
            # Section Title
            head = div_node.find('tei:head', namespaces)
            if head is not None and head.text:
                title = etree.SubElement(sec, "title")
                title.text = head.text
            
            # Paragraphs
            p_nodes = div_node.findall('tei:p', namespaces)
            for p_node in p_nodes:
                if p_node.text:
                    p = etree.SubElement(sec, "p")
                    p.text = p_node.text
            
            # Figures and Tables in this section
            # Note: Grobid often puts figures/tables at the top level of body or inside divs. 
            # We'll look for them inside the current div.
            
            figures = div_node.findall('tei:figure', namespaces)
            for fig in figures:
                fig_elem = etree.SubElement(sec, "fig")
                head = fig.find('tei:head', namespaces)
                if head is not None and head.text:
                    label = etree.SubElement(fig_elem, "label")
                    label.text = head.text
                
                figDesc = fig.find('tei:figDesc', namespaces)
                if figDesc is not None and figDesc.text:
                    caption = etree.SubElement(fig_elem, "caption")
                    p = etree.SubElement(caption, "p")
                    p.text = figDesc.text
                
                graphic = fig.find('tei:graphic', namespaces)
                if graphic is not None:
                    url = graphic.get('url')
                    if url:
                         graphic_elem = etree.SubElement(fig_elem, "graphic")
                         graphic_elem.set("{http://www.w3.org/1999/xlink}href", url)

        # Back / References
        back = etree.SubElement(jats_root, "back")
        ref_list = etree.SubElement(back, "ref-list")
        
        bibl_nodes = tei_root.xpath('//tei:text/tei:back/tei:div/tei:listBibl/tei:biblStruct', namespaces=namespaces)
        for i, bibl in enumerate(bibl_nodes):
            ref = etree.SubElement(ref_list, "ref", id=f"bib{i+1}")
            mixed_citation = etree.SubElement(ref, "mixed-citation")
            
            # Title
            title = bibl.find('.//tei:title', namespaces)
            if title is not None and title.text:
                article_title = etree.SubElement(mixed_citation, "article-title")
                article_title.text = title.text
            
            # Authors
            authors = bibl.findall('.//tei:author', namespaces)
            if authors:
                person_group = etree.SubElement(mixed_citation, "person-group", {"person-group-type": "author"})
                for author in authors:
                    persName = author.find('tei:persName', namespaces)
                    if persName is not None:
                        name = etree.SubElement(person_group, "name")
                        surname = persName.find('tei:surname', namespaces)
                        forename = persName.find('tei:forename', namespaces)
                        if surname is not None and surname.text:
                            sn = etree.SubElement(name, "surname")
                            sn.text = surname.text
                        if forename is not None and forename.text:
                            gn = etree.SubElement(name, "given-names")
                            gn.text = forename.text

            # Source / Journal
            monogr = bibl.find('tei:monogr', namespaces)
            if monogr is not None:
                jtitle = monogr.find('tei:title', namespaces)
                if jtitle is not None and jtitle.text:
                    source = etree.SubElement(mixed_citation, "source")
                    source.text = jtitle.text
                
                imprint = monogr.find('tei:imprint', namespaces)
                if imprint is not None:
                    date = imprint.find('tei:date', namespaces)
                    if date is not None and date.get('when'):
                        year = etree.SubElement(mixed_citation, "year")
                        year.text = date.get('when')[:4]

        return etree.tostring(jats_root, pretty_print=True, encoding='unicode')

    except Exception as e:
        return f"Error converting to JATS: {str(e)}"

def extract_metadata(tei_xml_string):
    """
    Extracts structured metadata from Grobid TEI XML.
    """
    try:
        tei_root = etree.fromstring(tei_xml_string.encode('utf-8'))
        namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        metadata = {
            'title': '',
            'journal': '',
            'publisher': '',
            'date': '',
            'doi': '',
            'abstract': '',
            'authors': [],
            'keywords': [],
            'issn': [],
            'license_text': '',
            'license_url': '',
            'volume': '',
            'issue': '',
            'fpage': '',
            'lpage': ''
        }

        # Title
        title_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', namespaces=namespaces)
        if title_nodes and title_nodes[0].text:
            metadata['title'] = title_nodes[0].text

        # Authors
        author_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author', namespaces=namespaces)
        for author in author_nodes:
            author_data = {'first_name': '', 'last_name': '', 'affiliation': ''}
            persName = author.find('tei:persName', namespaces)
            if persName is not None:
                forename = persName.find('tei:forename', namespaces)
                surname = persName.find('tei:surname', namespaces)
                if forename is not None and forename.text:
                    author_data['first_name'] = forename.text
                if surname is not None and surname.text:
                    author_data['last_name'] = surname.text
            
            affiliation = author.find('tei:affiliation', namespaces)
            if affiliation is not None:
                orgName = affiliation.find('tei:orgName', namespaces)
                if orgName is not None and orgName.text:
                    author_data['affiliation'] = orgName.text
            
            metadata['authors'].append(author_data)

        # Abstract
        abstract_node = tei_root.xpath('//tei:teiHeader/tei:profileDesc/tei:abstract', namespaces=namespaces)
        if abstract_node:
            metadata['abstract'] = " ".join("".join(abstract_node[0].itertext()).split())

        # Keywords
        keyword_nodes = tei_root.xpath('//tei:teiHeader/tei:profileDesc/tei:textClass/tei:keywords/tei:term', namespaces=namespaces)
        metadata['keywords'] = [k.text for k in keyword_nodes if k.text]

        # Journal / Publisher / Date / DOI (Often in biblStruct/monogr)
        monogr = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr', namespaces=namespaces)
        if monogr:
            journal_title = monogr[0].find('tei:title', namespaces)
            if journal_title is not None and journal_title.text:
                metadata['journal'] = journal_title.text
            
            imprint = monogr[0].find('tei:imprint', namespaces)
            if imprint is not None:
                publisher = imprint.find('tei:publisher', namespaces)
                if publisher is not None and publisher.text:
                    metadata['publisher'] = publisher.text
                
                date = imprint.find('tei:date', namespaces)
                if date is not None and date.get('when'):
                    metadata['date'] = date.get('when')
                
                biblScope_vol = imprint.find('tei:biblScope[@unit="volume"]', namespaces)
                if biblScope_vol is not None and biblScope_vol.text:
                    metadata['volume'] = biblScope_vol.text
                
                biblScope_issue = imprint.find('tei:biblScope[@unit="issue"]', namespaces)
                if biblScope_issue is not None and biblScope_issue.text:
                    metadata['issue'] = biblScope_issue.text
                
                biblScope_page = imprint.find('tei:biblScope[@unit="page"]', namespaces)
                if biblScope_page is not None:
                    if biblScope_page.get('from'):
                        metadata['fpage'] = biblScope_page.get('from')
                    if biblScope_page.get('to'):
                        metadata['lpage'] = biblScope_page.get('to')

        idno_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[@type="DOI"]', namespaces=namespaces)
        if idno_nodes and idno_nodes[0].text:
            metadata['doi'] = idno_nodes[0].text

        # ISSN
        issn_nodes = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:monogr/tei:idno[@type="ISSN"]', namespaces=namespaces)
        metadata['issn'] = [issn.text for issn in issn_nodes if issn.text]

        # License
        license_node = tei_root.xpath('//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:availability/tei:licence', namespaces=namespaces)
        if license_node:
            if license_node[0].text:
                metadata['license_text'] = license_node[0].text
            if license_node[0].get('target'):
                metadata['license_url'] = license_node[0].get('target')

        # Defaults
        if not metadata['journal']:
            metadata['journal'] = "Regional Journal of Information and Knowledge Management"
        if not metadata['publisher']:
            metadata['publisher'] = "Regional Institute of Information and Knowledge Management"
        if not metadata['issn']:
            metadata['issn'] = ["2412-6535"]

        return metadata

    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {}
