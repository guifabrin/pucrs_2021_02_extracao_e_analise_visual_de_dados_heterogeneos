const fs = require('fs')
const path = require('path')
const { getFilesFrom } = require('./helpers')

const docs = path.join(__dirname, '../../docs/')

const result = {}

for (const filePath of getFilesFrom(docs, 'plot.json')) {
  const [, ref, dates, timeframe] = filePath.split('\\')
  const [dateInit, dateEnd] = dates.split('_')
  const [year] = dateInit.split('-')
  const [tick, query] = ref.split('_')
  const rawData = fs.readFileSync(filePath)
  if (!result[tick]) {
    result[tick] = {}
  }
  if (!result[tick][query]) {
    result[tick][query] = {}
  }
  if (!result[tick][query][year]) {
    result[tick][query][year] = {}
  }
  if (!result[tick][query][year]) {
    result[tick][query][year] = {}
  }
  if (!result[tick][query][year][timeframe]) {
    result[tick][query][year][timeframe] = []
  }
  result[tick][query][year][timeframe].push({
    dateInit,
    dateEnd,
    data: JSON.parse(rawData)
  })
}

const data = JSON.stringify(result)
fs.writeFileSync(`${docs}/results.json`, data)
