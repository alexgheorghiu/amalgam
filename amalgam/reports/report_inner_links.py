from amalgam.models import inside
from amalgam.models.models import *
from amalgam.delegate import Delegate
from amalgam.database import get_session

import jsonpickle

# Note: full link = (starting from a valid page to the next one)


STEP  = 10


def inner_links_data(crawl_id):
    delegate = Delegate(get_session())

    """
    crawl_id - crawl id
    """
    intervals = []
    for i in range(0, 100, STEP):
        intervals.append([i, i+STEP])
    print("Intervals %r " % intervals)

    # Select all pages
    pages = delegate.resource_get_all_by_crawl(crawl_id)

    # For every page select the no of internal full urls pointing to it. = Li
    d = dict()
    check = 0
    for page in pages:
        no = delegate.url_count_incoming_for_resource(page.id)
        d[page.id] = no
        check = check + no

    for k,v in d.items():
        print("\n%d -> %d" % (k, v))

    # Find the total number of internal full links = T
    no_total = delegate.url_count_internal_full(crawl_id)
    print("Total full internal links: %d " %  no_total)

    assert check == no_total, "The no of total internal links do not match"

    # For every page select the percent % of internal full urls pointing to it. Pi = Li * 100 / T
    percents = dict()
    for page in pages:    
        percents[page.id] = d[page.id] * 100 / no_total

    print("\nPercentages")
    for k,v in percents.items():
        print("\n%d -> %.2f%%" % (k, v))
        

    # Count total links for every interval I1[0-10], I2[10-20],...., I10[90-100] the number of links for the pages
    # that fall into that interval
    #    I1....Ti1...Pi1 = Ti1 *100 /T
    #    I2....Ti2...Pi2 = Ti1 * 100 / T

    # Compute percentage of every interval

    partials = dict()
    labels = []
    for interval in intervals:
        key = "{}-{}%".format(interval[0], interval[1])
        labels.append(key)
        partials[key] = 0
        for page in pages:
            if interval[1] == 100:
                if interval[0] <= percents[page.id] <= interval[1]:
                    partials[key] = partials[key] + percents[page.id]
            else:        
                if interval[0] <= percents[page.id] < interval[1]:
                    partials[key] = partials[key] + percents[page.id]

    print("\nPartials")
    for k, v in partials.items():
        print("\n{} {} " .format(k, v))


    # Prepare the char data, sample bellow
    '''
    {
                labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                datasets: [{
                    label: '# of Votes',
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 159, 64, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            }
    '''

    new_data = {
            'labels': list(partials.keys()),
            'datasets': [{
                'label': 'Inner links',
                'data': list(partials.values())
            }]
        }

    return new_data


if __name__ == '__main__':
    CRAWL_ID = 1
    data = inner_links_data(CRAWL_ID)
    print("Data: %r" % data)

    print("Data: %s" % jsonpickle.encode(data))


