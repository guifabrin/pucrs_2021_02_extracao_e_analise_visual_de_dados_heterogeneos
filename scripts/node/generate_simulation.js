const fs = require('fs')
const path = require('path')
const { getFilesFrom } = require('./helpers')

const docs = path.join(__dirname, '../../docs/')

const result = {}

for (const filePath of getFilesFrom(docs, 'plot.json')) {
  const [, ref, dates, timeframe] = filePath.split('\\')
  const [dateInit, dateEnd] = dates.split('_')
  const rawData = fs.readFileSync(filePath)
  if (!result[ref]) {
    result[ref] = {}
  }
  if (!result[ref][timeframe]) {
    result[ref][timeframe] = []
  }
  result[ref][timeframe].push({
    dateInit,
    dateEnd,
    data: JSON.parse(rawData)
  })
}

const data = JSON.stringify(result)
fs.writeFileSync(`${docs}/results.json`, data)
