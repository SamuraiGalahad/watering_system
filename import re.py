import csv
import requests

CSV_URL = 'https://anchor.fm/api/proxy/v3/analytics/station/webStationId:3b9f29ec/plays?timeInterval=86400&amp;' \
          'timeRangeStart=1607904000&amp;timeRangeEnd=1625529600&amp;csvFilename=Дожитьдо18_TotalPlays_2020-12-' \
          '14_to_2021-07-06.csv'


with requests.Session() as s:
    download = s.get(CSV_URL)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    my_list = list(cr)
    for row in my_list:
        print(row)