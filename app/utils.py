def comma_list_artists(artist_list):
    # err, unused.
    return ", ".join(artist.get_readable_name() for artist in artist_list)

def artist_db_name(name):
    return name.replace(" ", "_")