# PUCRS 2021/02 Extraction and visual analysis of heterogeneous data

# Goal

This project aims to create a database and explore the possibility of data from Twitter influencing at some point the
Brazilian asset market.

It uses a web crawler to acquire tweets and the MT5 library of the MetaTrader platform for graphical analysis of the
Dice.

# Env configuration
- Copy .env.example to .env
```dotenv
MONGO_DB_URL=mongodb+srv://root:password@localhost/database?retryWrites=true&w=majority
MONGO_DB_CLIENT=client
MONGO_DB_COLLECTION=collection
PATH_TO_SAVE=C:\
```

# Data acquisition
## Scrapper with external libs

### Required 
- --query [-q] what should be in the Tweet
- --since [-s] since when should the search be run

### Non-required 
- --until [-u] how long to run the search (or one day added automatically)

### Examples
- Run search from 2021-01-01 until 2021-01-02
```bash
python fetch.py -q petrobras -s "2021-01-01"
```

- Run search from 2021-01-01 until 2021-12-31
```bash
python fetch.py -q petrobras -s "2021-01-01" -u "2021-12-31"
```

## Scrapper with selenium and chrome
### Required 
- --query [-q] what should be in the Tweet
- --since [-s] since when should the search be run

### Non-required 
- --until [-u] how long to run the search (or one day added automatically)

### Examples
- Run search from 2021-01-01 until 2021-01-02
```bash
python scrap.py -q petrobras -s "2021-01-01"
```

- Run search from 2021-01-01 until 2021-12-31
```bash
python scrap.py -q petrobras -s "2021-01-01" -u "2021-12-31"
```

# Data Plot
## Required
- --tick [-t] stock exchange asset
- --query [-q] what must be in the Tweet to be plotted
- --since [-s] since when should the search run
- --frame [-f] which time frame should be considered:
    - check mt5 library timeframes

## Non required
- --until [-u] how long to run the search
- --count [-c] amount of stock exchange data
- --path [-p] path to save html file (can be setted on .env)
- --lines [-l] vertical lines to plot in chart, format json where key is date and value is the line title

### Examples

- Plot PETR4 with petrobras query search from 2019-01-01 00:00:00 until 2021-08-31 23:59:59 using timeframe D1
```
python plot.py -t PETR4 -q petrobras -s "2019-01-01 00:00:00" -u "2021-08-31 23:59:59" -f TIMEFRAME_D1
```

- Plot VALE3 with brumadinho query search from 2019-01-01 00:00:00 until 2019-01-31 23:59:59 using timeframe D1 and add line into 2019-01-25 13:37:00
```
python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2021-08-31 23:59:59" -f TIMEFRAME_D1 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
```

## Results
Access [Generated results](https://guifabrin.github.io/pucrs_tt_mt5/)