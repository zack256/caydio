def comma_list_artists(artist_list):
    # err, unused.
    return ", ".join(artist.get_readable_name() for artist in artist_list)

def artist_db_name(name):
    return name.replace(" ", "_")

def format_tag_name(name):
    new_name = ""
    for c in name:
        if c.isalnum():
            new_name += c.lower()
        else:
            new_name += "-"
    good_name = ""
    for c, el in enumerate(new_name):
        if el != "-":
            good_name += el
        elif good_name and good_name[-1] != "-":
            good_name += "-"
    if good_name and good_name[-1] == "-":
        return good_name[:-1]
    return good_name