CLIENT_ID = 'REDACTED'
SECRET_KEY = 'REDACTED'
from pip._vendor import requests
from collections import Counter
auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

# logging in
data = {
    'grant_type' : 'password',
    'username' : 'REDACTED',
    'password' : 'REDACTED'
}
headers = {'User-Agent' : 'MyAPI/1.0'}

res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

TOKEN = res.json()['access_token']

headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# the page to get data from
res = requests.get("https://oauth.reddit.com/r/wallstreetbets/hot.json?limit=100",
                   headers=headers)

# checking the hot list on wallstreetbets for tickers
list_of_words = []
for post in res.json()['data']['children']:
    split_list = post['data']['title'].split()
    out_list = []
    for word in split_list:
        out_list.append(word.replace('$', ''))
    list_of_words.extend(out_list)

# checking the top list on wallstreetbets for tickers
res = requests.get("https://oauth.reddit.com/r/wallstreetbets/top.json?limit=100",
                   headers=headers)
for post in res.json()['data']['children']:
    split_list = post['data']['title'].split()
    out_list = []
    for word in split_list:
        out_list.append(word.replace('$', ''))
    list_of_words.extend(out_list)

Counter = Counter(list_of_words)

# reading from the text file of all the most common stock tickers and removing new line characters
with open('commonwords.txt') as f:
    content = f.readlines()
content = [x.strip() for x in content] 


# list_to_delete are the words contained in the dictionary that are not stock tickers, so they are irrelevant and must be removed
list_to_delete = []
for key in Counter:
    if key not in content:
        list_to_delete.append(key)

# iterating thru and deleting the words in Counter that are not stock tickers
for key in list_to_delete:
    del Counter[key]
five_most_common = Counter.most_common(5)

newFile = open('wsbstats.txt', 'x')

newFile = open('wsbstats.txt', 'w')

# writing to the file the list of top stock tickers on WSB that day
newFile.write('Here is your /r/WallstreetBets Daily Digest!\n\n')
newFile.write('Top Five Trending Tickers:\n')
counter = 1
for tupler in five_most_common:
    newFile.write(str(counter) + '. ' + tupler[0] + ' - Mentioned ' + str(tupler[1]) + ' times\n')
    counter += 1


# adding extra space between this section and another
newFile.write('\n')

newFile.write('Is today an exciting or boring day in the market today?\n')

res = requests.get('https://oauth.reddit.com/r/wallstreetbets/search?sort=new&restrict_sr=on&q=flair%3A"Daily+Discussion"',
                   headers=headers)

# finding the rolling average number of comments for the most recent daily discussion threads
amount = 0
totalComments = 0
for post in res.json()['data']['children']:
    if 'Daily' in post['data']['title']:
        amount += 1
        totalComments += post['data']['num_comments']

rolling_average = round(totalComments / amount, 0)

# finding the amount of comments in the most recent daily discussion to see if it is above average or below average

for post in res.json()['data']['children']:
    if 'Daily' in post['data']['title']:
        if post['data']['num_comments'] > rolling_average:
            above_average = True
        else:
            above_average = False
        break

# writing to file whether or not it is an exciting day or not
if above_average:
    newFile.write('After my analysis of /r/wallstreetbets, it seems to be an exciting day in the market today!\n')
else:
    newFile.write('After my analysis of /r/wallstreetbets, it seems to be a boring trading day today :(\n')
