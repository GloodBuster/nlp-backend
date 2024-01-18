import spacy
from spacy.matcher import Matcher
from fastapi.responses import JSONResponse
from nlp_backend.testApi import get_db_connection


def search(input_text):

    def filter_spans(matches):
        # Convert matches to spans and sort by length in descending order
        sorted_matches = sorted(matches, key=lambda match: (
            match[2] - match[1]), reverse=True)
        result = []
        seen_tokens = set()
        for match_id, start, end in sorted_matches:
            # Check for end - 1 here because boundaries are inclusive
            if start not in seen_tokens and end - 1 not in seen_tokens:
                result.append((match_id, doc[start:end]))
                seen_tokens.update(range(start, end))
        return result

    # Load the Spanish model
    nlp = spacy.load("es_core_news_md")

    # Initialize the matcher
    matcher = Matcher(nlp.vocab)

    # Regla escrita por un autor
    by_author = [{"LEMMA": {"IN": ["escribir", "redactar", "componer", "publicar"]}, "OP": "?"}, {
        "LOWER": "por"}, {"ENT_TYPE": "PER", "OP": "+"}]
    matcher.add("BY_AUTHOR", [by_author])

    # Regla entre dos años
    between_years = [{"LOWER": "años"}, {
        "LIKE_NUM": True}, {"LOWER": "y", "OP": "?"}, {"LIKE_NUM": True}]

    matcher.add("BETWEEN_YEARS", [between_years])

    # Rule for obras
    list_obras = [{"LOWER": {"IN": ["obra", "obras"]}}]

    # Add the rule to the matcher
    matcher.add("LIST_OBRAS", [list_obras])

    # Rule for obras
    list_publications = [{"LEMMA": "publicar"}, {"OP": "*"},  {
        "LOWER": "año"}, {"LIKE_NUM": True}]

    # Add the rule to the matcher
    matcher.add("LIST_PUBLICATIONS", [list_publications])

    # Process the text
    doc = nlp(input_text)

    # Apply the matcher
    matches = matcher(doc)

    # Filter the matches
    filtered_matches = filter_spans(matches)

    matches_dict = {nlp.vocab.strings[match_id]
        : span for match_id, span in filtered_matches}

    if "LIST_OBRAS" in matches_dict:
        if ("BY_AUTHOR" in matches_dict and "BETWEEN_YEARS" in matches_dict):
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])
            years = [int(token.text) for token in matches_dict["BETWEEN_YEARS"]
                     if token.like_num]
            lower_year = min(years)
            upper_year = max(years)

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                # Convert author to lowercase for case-insensitive comparison
                author = author.lower()

                # Prepare SQL query
                query = f"""
                SELECT * FROM works
                WHERE elaboration_start_year >= '{lower_year}'
                AND elaboration_end_year <= '{upper_year}'
                AND unaccent(lower('{author}')) = ANY(ARRAY(SELECT unaccent(lower(author)) FROM unnest(authors) as author))
                """

                cur.execute(query)

                rows = cur.fetchall()

                # Convert the rows into a list of dictionaries
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

        elif ("BY_AUTHOR" in matches_dict and "LIST_PUBLICATIONS" in matches_dict):
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])
            year = [token.text for token in matches_dict["LIST_PUBLICATIONS"]
                    if token.like_num][0]

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                # Convert author to lowercase for case-insensitive comparison
                author = author.lower()

                # Prepare SQL query
                query = f"""
                SELECT works.* FROM works
                JOIN publications ON works.id = publications.work_id
                WHERE unaccent(lower('{author}')) = ANY(ARRAY(SELECT unaccent(lower(author)) FROM unnest(works.authors) as author))
                AND publications.publication_year = '{year}'
                """

                cur.execute(query)

                rows = cur.fetchall()

                # Convert the rows into a list of dictionaries
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

        elif "BETWEEN_YEARS" in matches_dict:
            years = [int(token.text) for token in matches_dict["BETWEEN_YEARS"]
                     if token.like_num]
            lower_year = min(years)
            upper_year = max(years)

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                query = f"""
                SELECT * FROM works
                WHERE elaboration_start_year >= '{lower_year}'
                AND elaboration_end_year <= '{upper_year}'
                """

                cur.execute(query)

                rows = cur.fetchall()
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

        elif "LIST_PUBLICATIONS" in matches_dict:
            year = [token.text for token in matches_dict["LIST_PUBLICATIONS"]
                    if token.like_num][0]

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                query = f"""
                SELECT works.* FROM works
                JOIN publications ON works.id = publications.work_id
                WHERE publications.publication_year = '{year}'
                """

                cur.execute(query)

                rows = cur.fetchall()
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

        elif "BY_AUTHOR" in matches_dict:
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                author = author.lower()

                query = f"""
                SELECT * FROM works
                WHERE unaccent(lower('{author}')) = ANY(ARRAY(SELECT unaccent(lower(author)) FROM unnest(authors) as author))
                """

                cur.execute(query)

                rows = cur.fetchall()
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

        else:
            try:
                conn = get_db_connection()
                cur = conn.cursor()

                query = f"""
                SELECT * FROM works LIMIT 10 OFFSET 0
                """

                cur.execute(query)

                rows = cur.fetchall()
                works = [
                    dict(zip([column[0] for column in cur.description], row)) for row in rows]

                cur.close()
                conn.close()

                return works
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

    else:
        return []
