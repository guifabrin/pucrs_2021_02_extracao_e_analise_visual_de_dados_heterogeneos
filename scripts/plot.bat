cd ..


python plot.py -t VALE3 -q mariana -s "2015-10-01 00:00:00" -u "2015-11-30 23:59:59" -f TIMEFRAME_D1 -l "{\"2015-11-05 15:30:00\":\"Dam break\"}"
python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2019-01-31 23:59:59" -f TIMEFRAME_D1 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
python plot.py -t PETR4 -q petrobras -s "2014-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_D1 -j ".\extra\petrobras_lava_jato.json"

python plot.py -t VALE3 -q mariana -s "2015-10-01 00:00:00" -u "2015-11-30 23:59:59" -f TIMEFRAME_H1 -l "{\"2015-11-05 15:30:00\":\"Dam break\"}"
python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2019-01-31 23:59:59" -f TIMEFRAME_H1 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
python plot.py -t PETR4 -q petrobras -s "2014-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_H1 -j ".\extra\petrobras_lava_jato.json"

python plot.py -t VALE3 -q mariana -s "2015-10-01 00:00:00" -u "2015-11-30 23:59:59" -f TIMEFRAME_M30 -l "{\"2015-11-05 15:30:00\":\"Dam break\"}"
python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2019-01-31 23:59:59" -f TIMEFRAME_M30 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
python plot.py -t PETR4 -q petrobras -s "2014-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_M30 -j ".\extra\petrobras_lava_jato.json"

python plot.py -t VALE3 -q mariana -s "2015-10-01 00:00:00" -u "2015-11-30 23:59:59" -f TIMEFRAME_M15 -l "{\"2015-11-05 15:30:00\":\"Dam break\"}"
python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2019-01-31 23:59:59" -f TIMEFRAME_M15 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
python plot.py -t PETR4 -q petrobras -s "2014-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_M15 -j ".\extra\petrobras_lava_jato.json"

python plot.py -t VALE3 -q brumadinho -s "2019-01-01 00:00:00" -u "2019-01-31 23:59:59" -f TIMEFRAME_M1 -l "{\"2019-01-25 13:37:00\":\"Dam break\"}"
python plot.py -t VALE3 -q mariana -s "2015-10-01 00:00:00" -u "2015-11-30 23:59:59" -f TIMEFRAME_M1 -l "{\"2015-11-05 15:30:00\":\"Dam break\"}"
python plot.py -t PETR4 -q petrobras -s "2014-01-01 00:00:00" -u "2021-12-31 23:59:59" -f TIMEFRAME_M1 -j ".\extra\petrobras_lava_jato.json"
