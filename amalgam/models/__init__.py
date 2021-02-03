def inside(link, links):
    """See if a link is inside a list of links based on the absolute_url of the link(s)"""
    for l in links:
        if l.absolute_url == link.absolute_url:
            return True
    return False