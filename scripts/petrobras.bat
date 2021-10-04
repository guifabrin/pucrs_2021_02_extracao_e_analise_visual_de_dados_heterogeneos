cd ..
python plot.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_H1
python plot_both.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_H1
python plot.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_D1
python plot_both.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_D1

python plot.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_H1  -m 4 -r 1
python plot_both.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_H1 -m 4 -r 1
python plot.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_D1 -m 4 -r 1
python plot_both.py -t PETR4 -q petrobras -s "2021-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_D1 -m 4 -r 1