End-to-end vertical web search pseudo relevance feedback queries recommandation software

# Programming files description
The project consists of three files:
helper.py
main.py
preprocessor.py

# preprocessor.py
contains basic preprocessing functions such as decoding HTML characters, removing special characters, etc.

# helper.py
It consists of search results scrapping logic from the SERP API. It extracts all the relevant metainformation from each vertical and each search result such as title, url, description, date, thumbnail, etc. It also consists summarization facility to aid questions generation.

# main.py
It consists of main programming flow sequence and deep learning models including 5W model and transformers.