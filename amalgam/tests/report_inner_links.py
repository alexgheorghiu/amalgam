from amalgam.models import inside
from amalgam.models.models import *
from amalgam.delegate import delegate

# Note: full link = (starting from a valid page to the next one)

# Select all pages
pages = delegate.resource_get_all_by_crawl(1)

# For every page select the no of internal full urls pointing to it. = Li
d = dict()
for page in pages:
    no = delegate.url_count_incoming_for_resource(page.id)
    d[page.id] = no

for k,v in d.items():
    print("\n%d -> %d" % (k, v))

# Find the total number of internal full links = T

# For every page select the percent % of internal full urls pointing to it. Pi = Li * 100 / T

# Count total links for every interval I1[0-10], I2[10-20],...., I10[90-100] the number of links for the pages
# that fall into that interval
#    I1....Ti1...Pi1 = Ti1 *100 /T
#    I2....Ti2...Pi2 = Ti1 * 100 / T

# Compute percentage of every interval



