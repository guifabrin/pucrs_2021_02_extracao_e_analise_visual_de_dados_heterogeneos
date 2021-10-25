const fs = require('fs')
const path = require('path')
const { getFilesFrom } = require('./helpers')
const docs = path.join(__dirname, '../../docs/')
const data = JSON.stringify(getFilesFrom(docs, 'plot.html'))
fs.writeFileSync(`${docs}plots.json`, data)