import spacy
from spacy.matcher import Matcher


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

    matches_dict = {nlp.vocab.strings[match_id]                    : span for match_id, span in filtered_matches}

    print(matches_dict)

    if "LIST_OBRAS" in matches_dict:
        if ("BY_AUTHOR" in matches_dict and "BETWEEN_YEARS" in matches_dict):
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])
            years = [int(token.text) for token in matches_dict["BETWEEN_YEARS"]
                     if token.like_num]
            lower_year = min(years)
            upper_year = max(years)

            print("Lista de obras escritas por " + author +
                  " entre los años " + str(lower_year) + " y " + str(upper_year))

        elif ("BY_AUTHOR" in matches_dict and "LIST_PUBLICATIONS" in matches_dict):
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])
            year = [int(token.text) for token in matches_dict["LIST_PUBLICATIONS"]
                    if token.like_num][0]

            print("Lista de obras escritas por " + author +
                  " publicadas en el año " + str(year))

        elif "BETWEEN_YEARS" in matches_dict:
            years = [int(token.text) for token in matches_dict["BETWEEN_YEARS"]
                     if token.like_num]
            lower_year = min(years)
            upper_year = max(years)

            print("Lista de obras entre los años " +
                  str(lower_year) + " y " + str(upper_year))

        elif "LIST_PUBLICATIONS" in matches_dict:
            year = [int(token.text) for token in matches_dict["LIST_PUBLICATIONS"]
                    if token.like_num][0]
            print("Lista de obras publicadas en el año " + str(year))

        elif "BY_AUTHOR" in matches_dict:
            author = ' '.join([token.text for token in matches_dict["BY_AUTHOR"]
                               if token.ent_type_ == "PER"])
            print("Lista de obras escritas por " + author)

        else:
            print("Lista de obras")

    else:
        print("No se encontraron coincidencias")


search("Listame las obras que se publicaron en el año 1500.")
