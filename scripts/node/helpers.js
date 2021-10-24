const fs = require('fs')
const path = require('path')

function * walkSync (dir, filter = false) {
  const files = fs.readdirSync(dir, { withFileTypes: true })
  for (const file of files) {
    if (file.isDirectory()) {
      yield * walkSync(path.join(dir, file.name), filter)
    } else {
      if (filter && file.name.indexOf(filter) > -1) {
        yield path.relative('./', path.join(dir, file.name))
      }
    }
  }
}

function getFilesFrom (dir, filter) {
  const result = []
  for (const filePath of walkSync(dir, filter)) {
    result.push(filePath)
  }
  return result
}

module.exports = {
  getFilesFrom
}
